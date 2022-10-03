from flask import session
from db import db
import services.cart as cart

def getorders(user_id = None):
    if not user_id:
        sql = "SELECT id, user_id, handler_id, total_sum, order_state,created_at, updated_at FROM order_details"
        return db.session.execute(sql).fetchall()
    sql = "SELECT id, user_id, handler_id, total_sum, order_state, created_at, updated_at FROM order_details WHERE user_id=:user_id"
    return db.session.execute(sql, {"user_id":user_id}).fetchall()

def processorder(order_id):
    handler_id = session["user_id"]
    sql = "UPDATE order_details SET order_state='processed', handler_id=:handler_id WHERE id=:order_id AND order_state='created'"
    db.session.execute(sql, {"handler_id":handler_id, "order_id":order_id})
    db.session.commit()

def createorder(items, user_id):
    cart.remove()
    try:
        order_id = new_order_detail(user_id)
        new_order_items(items, order_id)
        db.session.commit()
        cart.clear(user_id)
        return True
    except:
        return False

def new_order_detail(user_id):
    cart_sum = session["cart_sum"]
    sql = "INSERT INTO order_details (user_id, total_sum, order_state, created_at) VALUES (:user_id, :total_sum, :order_state, NOW()) RETURNING id"
    return db.session.execute(sql, {"user_id":user_id, "total_sum":cart_sum,"order_state":"created"}).fetchone()[0]

def new_order_items(items, order_id):
    for item in items:
        product_id = item["product_id"]
        quantity = item["quantity"]
        unit_price = item["price"]
        sql = "INSERT INTO order_items (order_id, product_id, quantity, unit_price, created_at) VALUES (:order_id, :product_id, :quantity, :unit_price, NOW())"
        db.session.execute(sql, {"order_id":order_id, "product_id":product_id,"quantity":quantity, "unit_price":unit_price })
