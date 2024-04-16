"""
app.py contains all of the server application
this is where you'll find all of the get/post request handlers
the socket event handlers are inside of socket_routes.py
"""

import hashlib
import secrets
import ssl

from flask import Flask, abort, render_template, request, url_for
from flask_socketio import SocketIO

import db

# import logging

# this turns off Flask Logging, uncomment this to turn off Logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

app = Flask(__name__)

# secret key used to sign the session cookie
app.config["SECRET_KEY"] = secrets.token_hex()
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

    password = password + user.salt

    hash_object = hashlib.sha256()
    hash_object.update(password.encode())
    pwdHash = hash_object.hexdigest()

    if user is None:
        return "Error: User does not exist!"

    if user.password != str(pwdHash):
        return f"Error: Password does not match!"
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
    salt = request.json.get("salt")

    if db.get_user(username) is None:

        db.insert_user(username, password, salt)
        return url_for("home", username=username)
    return "Error: User already exists!"


# handler when a "404" error happens
@app.errorhandler(404)
def page_not_found(_):
    return render_template("404.jinja"), 404


# home page, where the messaging app is
@app.route("/home")
def home():
    if request.args.get("username") is None:
        abort(404)
    return render_template(
        "home.jinja",
        username=request.args.get("username"),
        friends=db.getFriends(request.args.get("username")),
        receivedList=db.getRequestsReceived(request.args.get("username")),
        sentList=db.getRequestsSent(request.args.get("username")),
    )


ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
ssl_context.load_cert_chain(
    "certs/info2222.test.crt", "certs/info2222.test.key", "password"
)

if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=8000, ssl_context=ssl_context)
