"""
app.py contains all of the server application
this is where you'll find all of the get/post request handlers
the socket event handlers are inside of socket_routes.py
"""

import hashlib
import secrets
import ssl
from functools import wraps

from flask import Flask, abort, redirect, render_template, request, session, url_for
from flask_socketio import SocketIO

import db

# import logging

# this turns off Flask Logging, uncomment this to turn off Logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

app = Flask(__name__)

# secret key used to sign the session cookie
app.config["SECRET_KEY"] = secrets.token_hex()

app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
)

socketio = SocketIO(app)

# don't remove this!!
import socket_routes


# index page
@app.route("/")
def index():
    return render_template("index.jinja")


# login page
@app.route("/login")
def login():
    return render_template("login.jinja")


# handles a post request when the user clicks the log in button
@app.route("/login/user", methods=["POST"])
def login_user():
    if not request.is_json:
        abort(404)

    username = request.json.get("username")
    password = request.json.get("password")

    user = db.get_user(username)

    if user is None:
        return "Error: User does not exist!"

    password = password + user.salt

    hash_object = hashlib.sha256()
    hash_object.update(password.encode())
    pwdHash = hash_object.hexdigest()

    if user.password != str(pwdHash):
        return f"Error: Password does not match!"

    session["username"] = user.username
    session["logged_in"] = True
    return url_for("home", username=request.json.get("username"))


# handles a get request to the signup page
@app.route("/signup")
def signup():
    return render_template("signup.jinja")


# handles a post request when the user clicks the signup button
@app.route("/signup/user", methods=["POST"])
def signup_user():
    if not request.is_json:
        abort(404)
    username = request.json.get("username")
    password = request.json.get("password")

    salt = secrets.token_bytes(16)

    if len(username.split(",")) > 1:
        return "Error: Invalid Username!"

    password += str(salt)

    hash_object = hashlib.sha256()
    hash_object.update(password.encode())
    pwdHash = hash_object.hexdigest()

    if db.get_user(username) is None:

        db.insert_user(username, str(pwdHash), str(salt))
        return url_for("home", username=username)
    return "Error: User already exists!"


# handler when a "404" error happens
@app.errorhandler(404)
def page_not_found(_):
    return render_template("404.jinja"), 404


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" not in session or not session["logged_in"]:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


# home page, where the messaging app is
@app.route("/home")
@login_required
def home():

    session_username = session.get("username")
    requested_username = request.args.get("username")
    if request.args.get("username") is None:
        abort(404)

    if session_username is None or session_username != requested_username:
        return redirect(url_for("login"))

    user = db.get_user(requested_username)

    return render_template(
        "home.jinja",
        username=requested_username,
        friends=user.getFriends(),
        receivedList=user.getRequestsReceived(),
        sentList=user.getRequestsSent(),
        privateKey=user.password,
        accessLevel=user.accessLevel,
    )


ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
ssl_context.load_cert_chain(
    "certs/info2222.test.crt", "certs/info2222.test.key", "password"
)

if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=8000, ssl_context=ssl_context)
