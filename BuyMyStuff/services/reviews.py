from flask import session
from db import db

def add(product_id, grade, content):
    user_id = session["user_id"]
    sql = "INSERT INTO reviews (user_id, product_id, grade, content, created_at) VALUES (:user_id, :product_id, :grade, :content, NOW())"
    try:
        db.session.execute(sql, {"user_id":user_id, "product_id":product_id,"grade":grade, "content":content})
        db.session.commit()
        return True
    except:
        return False

def reviews(product_id):
    sql = "SELECT r.id, r.user_id, r.product_id, r.grade, r.content, r.created_at, u.username FROM reviews r, users u WHERE r.product_id=:product_id AND r.user_id=u.id"
    return db.session.execute(sql, {"product_id":product_id}).fetchall()

def getavg(product_id):
    sql = "SELECT ROUND(COALESCE(AVG(grade), 0), 1) FROM reviews WHERE product_id=:product_id"
    return db.session.execute(sql, {"product_id":product_id}).fetchone()[0]

def count(product_id):
    sql = "SELECT COUNT(*) FROM reviews WHERE product_id=:product_id"
    return db.session.execute(sql, {"product_id":product_id}).fetchone()[0]
