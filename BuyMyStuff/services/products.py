from db import db
from services import cart

def getall():
    sql = "SELECT id, creator_id, name, price, description,active, created_at, updated_at FROM products"
    return db.session.execute(sql).fetchall()

def getactive():
    sql = "SELECT id, creator_id, name, price, description,active, created_at, updated_at FROM products WHERE active=true"
    return db.session.execute(sql).fetchall()

def add(creator_id, name, price, description):
    sql = "INSERT INTO products (creator_id, name, price,description, active, created_at, updated_at) VALUES (:creator_id, :name, :price, :description, true, NOW(), NOW())"
    try:
        db.session.execute(sql, {"creator_id":creator_id, "name":name,"price":price, "description":description})
        db.session.commit()
        return True
    except:
        return False

def active(product_id):
    sql = "SELECT active FROM products WHERE id=:product_id"
    try:
        return db.session.execute(sql, {"product_id":product_id}).fetchone()[0]
    except:
        return False

def get(product_id):
    sql = "SELECT id, creator_id, name, price, description,active, created_at, updated_at FROM products WHERE id=:product_id"
    return db.session.execute(sql, {"product_id": product_id}).fetchone()

def edit(product_id, new_name, new_price, new_description, active):
    sql = "UPDATE products SET name=:new_name, price=:new_price, description=:new_description,active=:is_active, updated_at=NOW() WHERE id=:product_id"
    try:
        db.session.execute(sql, {"new_name":new_name, "new_price":new_price,"new_description":new_description, "is_active":active, "product_id":product_id})
        db.session.commit()
        if not active:
            cart.remove()
        return True
    except:
        db.session.close()
        return False
