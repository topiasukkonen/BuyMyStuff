from flask import session, abort
from db import db

def add(user_id, product_id, quantity):
    sql = "SELECT id, quantity FROM cart_items WHERE user_id=:user_id AND product_id=:product_id"
    cart_item = db.session.execute(sql, {"user_id":user_id, "product_id":product_id}).fetchone()
    try:
        if not cart_item:
            sql = "INSERT INTO cart_items (user_id, product_id, quantity, created_at) VALUES (:user_id, :product_id, :quantity, NOW())"
            db.session.execute(sql, {"user_id":user_id, "product_id":product_id,
                               "quantity":quantity})
            db.session.commit()
        else:
            new_quantity = cart_item["quantity"] + int(quantity)
            sql = "UPDATE cart_items SET quantity=:quantity WHERE id=:id"
            db.session.execute(sql, {"quantity":new_quantity, "id":cart_item["id"]})
            db.session.commit()
        session["cart_sum"] = sum(user_id)
    except:
        pass

def sum(user_id):
    remove()
    sql = "SELECT COALESCE(SUM(p.price * c.quantity), 0) FROM products p, cart_items c WHERE p.id=c.product_id AND c.user_id=:user_id"
    return db.session.execute(sql, {"user_id":user_id}).fetchone()[0]

def get(user_id):
    sql = "SELECT c.id, p.id as product_id, p.name, p.price, c.quantity,(p.price * c.quantity) AS sum FROM products p, cart_items c WHERE p.id=c.product_id AND c.user_id=:user_id"
    return db.session.execute(sql, {"user_id": user_id}).fetchall()

def delete(cart_item_id):
    sql = "DELETE FROM cart_items WHERE id=:cart_item_id RETURNING user_id"
    user_id = db.session.execute(sql, {"cart_item_id":cart_item_id}).fetchone()
    if not user_id or session.get("user_id", 0) != user_id[0]:
        abort(403)
    else:
        db.session.commit()
        session["cart_sum"] = sum(session["user_id"])

def clear(user_id):
    sql = "DELETE FROM cart_items WHERE user_id=:user_id"
    db.session.execute(sql, {"user_id":user_id})
    db.session.commit()
    session["cart_sum"] = 0.0

def remove():
    sql = "DELETE FROM cart_items c USING products p WHERE p.id=c.product_id AND p.active=false"
    db.session.execute(sql)
    db.session.commit()
