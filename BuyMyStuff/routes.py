from flask import redirect, render_template, request, url_for
from app import app
from services import users, products, cart, orders, reviews

@app.route("/")
def index():
    product_list = products.getactive()
    return render_template("index.html", products=product_list)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        role = "admin" if request.form.get("create_admin") else "customer"
        if len(username) not in range(1,21):
            return render_template("register.html",error_message="Username must be between 1 and 20 characters long")
        if password1 != password2:
            return render_template("register.html", error_message="Passwords do not match")
        if len(password1) not in range(5,51):
            return render_template("register.html",error_message="Password must be 5-50 characters long")

        if users.register(username, password1, role):
            if role == "customer":
                return redirect(url_for("index"))
            if role == "admin":
                return redirect(url_for("admin_products"))
        return render_template("register.html", error_message="Username already in use")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if not users.login(username, password):
            return render_template("login.html", error_message="Wrong username or password")
        if users.role() == "customer":
            return redirect(url_for("index"))
        if users.role() == "admin":
            return redirect(url_for("admin_products"))
@app.route("/logout")
def logout():
    users.logout()
    return redirect(url_for("index"))
@app.route("/product/<int:product_id>")
def show_product(product_id):
    product = products.get(product_id)
    reviews_list = reviews.reviews(product_id)
    avg_grade = reviews.getavg(product_id)
    review_count = reviews.count(product_id)
    return render_template("product.html", product=product, reviews_list=reviews_list,avg_grade=avg_grade, review_count=review_count)

@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    users.check_csrf()
    product_id = request.form["product_id"]
    try:
        quantity = int(request.form["quantity"])
    except:
        return redirect(url_for("show_product"), product_id=product_id)
    if not products.active(product_id) or quantity not in range(1, 51):
        return redirect(url_for("index"))
    cart.add(users.user_id(), product_id, quantity)
    return redirect(url_for("show_product"), product_id=product_id)

@app.route("/user/<int:user_id>")
def user(user_id):
    users.require_role("customer")
    users.confirm_id(user_id)
    items = cart.get(user_id)
    order_list = orders.getorders(user_id)
    return render_template("user.html", items=items, order_list=order_list)

@app.route("/user/<int:user_id>/checkout", methods=["GET", "POST"])
def checkout(user_id):
    users.require_role("customer")
    users.confirm_id(user_id)
    items = cart.get(user_id)
    if request.method == "GET":
        return render_template("checkout.html", items=items)
    if request.method == "POST":
        users.check_csrf()
        if items and str(items) == request.form["items"]:
            orders.createorder(items, user_id)
        return redirect(url_for("user", user_id=user_id))

@app.route("/delete_cart_item", methods=["POST"])
def delete_cart_item():
    users.check_csrf()
    cart.delete(request.form["cart_item_id"])
    return redirect(url_for("user", user_id=users.user_id()))

@app.route("/add_review", methods=["POST"])
def add_review():
    users.check_csrf()

    product_id = request.form["product_id"]
    content = request.form["content"]
    try:
        grade = int(request.form["grade"])
        if grade in [1,2,3,4,5] and len(content) in range(1,501) and products.active(product_id):
            reviews.add(product_id, grade, content)
    except:
        pass
    return redirect(url_for("show_product", product_id=product_id))

@app.route("/admin", methods=["GET", "POST"])
def admin_products():
    if not users.role() == "admin":
        return render_template("login.html",error_message="No access")

    product_list = products.getall()
    def render_with_error(error_message):
        return render_template("admin/index.html", products=product_list,error_message=error_message)

    if request.method == "GET":
        return render_template("admin/index.html", products=product_list)

    if request.method == "POST":
        users.check_csrf()
        name = request.form["name"]
        if len(name) not in range(1, 31):
            return render_with_error("Error")

        try:
            price = float(request.form["price"])
        except:
            return render_with_error("Error")
        if price <= 0 or price > 100_000:
            return render_with_error("Negative or over 100k prices not allowed")

        description = request.form["description"]
        if len(description) not in range(1, 500):
            return render_with_error("Error")

        if products.add(users.user_id(), name, price, description):
            return redirect(url_for("admin_products"))
        else:
            return render_with_error(f"Already available")

@app.route("/admin/orders", methods=["GET", "POST"])
def admin_orders():
    if not users.role() == "admin":
        return render_template("login.html",error_message="No access")
    orders_list = orders.getorders()
    if request.method == "GET":
        return render_template("admin/orders.html", order_list=orders_list)
    if request.method == "POST":
        users.check_csrf()
        order_id = request.form["order_id"]
        orders.processorder(order_id)
        return redirect(url_for("admin_orders"))

@app.route("/admin/product/<int:id>")
def admin_product(id):
    if not users.role() == "admin":
        return render_template("login.html",error_message="No access")
    return _admin_product_with_message(id, None)

@app.route("/admin/product/<int:id>/update", methods=["POST"])
def admin_product_update(id):
    users.check_csrf()
    if not users.role() == "admin":
        return render_template("login.html",error_message="No access")
    product = products.get(id)
    if not product:
        return redirect(url_for("admin_products"))
    new_name = request.form["name"] if request.form["name"] else product.name
    if len(new_name) > 30:
        return _admin_product_with_message(id, "Max 30 characters for name")
    new_description = request.form["description"] if request.form["description"] else product.description
    if len(new_description) > 500:
        return _admin_product_with_message(id, "Max 500 characters for description")
    new_price = request.form["price"] if request.form["price"] else product.price
    try:
        new_price = float(new_price)
    except:
        return _admin_product_with_message(id, "Error")
    if new_price < 0 or new_price > 100000:
        return _admin_product_with_message(id,"""Negative or over 100k prices not allowed""")
    is_active = "active" in request.form
    if products.edit(product.id, new_name, new_price, new_description, is_active):
        return redirect(url_for("admin_product", id=id))
    return _admin_product_with_message(id, f"Product {new_name} already available")

def _admin_product_with_message(id, message):
    product = products.get(id)
    if not product:
        return redirect(url_for("admin_products"))
    avg_grade = reviews.getavg(id)
    review_count = reviews.count(id)
    return render_template("admin/product.html", product=product, avg_grade=avg_grade,review_count=review_count, error_message=message)
