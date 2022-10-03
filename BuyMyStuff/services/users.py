import os
from flask import session, request, abort
from werkzeug.security import check_password_hash, generate_password_hash
from db import db
from services import cart

def login(username, password):
    sql = "SELECT id, username, password, role FROM users WHERE username=:username"
    user = db.session.execute(sql, {"username":username}).fetchone()
    if not user:
        return False
    if check_password_hash(user.password, password):
        session["user_id"] = user.id
        session["username"] = username
        session["user_role"] = user.role
        session["cart_sum"] = cart.sum(user.id)
        session["csrf_token"] = os.urandom(16).hex()
        return True
    return False

def register(username, password, role):
    hash_value = generate_password_hash(password)
    try:
        sql = "INSERT INTO users (username, password, role) VALUES (:username, :password, :role)"
        db.session.execute(sql, {"username":username, "password":hash_value, "role":role})
        db.session.commit()
    except:
        return False
    return login(username, password)

def logout():
    session.clear()

def role():
    try:
        return session["user_role"]
    except:
        return None

def user_id():
    return session["user_id"]

def require_role(role):
    if session.get("user_role", None) != role:
        abort(403)

def confirm_id(id):
    if session.get("user_id", 0) != id:
        abort(403)

def check_csrf():
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)
