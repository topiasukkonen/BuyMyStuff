from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from os import getenv

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.config["APPLICATION_ROOT"] = "/"
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1, x_prefix=1, x_proto=1)

import routes
