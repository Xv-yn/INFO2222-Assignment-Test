"""
socket_routes
file containing all the routes related to socket.io
"""

from flask import request, session
from flask_socketio import emit, join_room, leave_room

try:
    from __main__ import socketio
except ImportError:
    from app import socketio

import hashlib
import hmac

import db
from models import Room

room = Room()


# when the client connects to a socket
# this event is emitted when the io() function is called in JS
@socketio.on("connect")
def connect():
    if not session.get("logged_in"):
        return False

    username = request.cookies.get("username")
    room_id = request.cookies.get("room_id")
    if room_id is None or username is None:
        return
    # socket automatically leaves a room on client disconnect
    # so on client connect, the room needs to be rejoined
    join_room(int(room_id))
    emit("incoming", (f"{username} has connected", "green"), to=int(room_id))


# event when client disconnects
# quite unreliable use sparingly
@socketio.on("disconnect")
def disconnect():
    username = request.cookies.get("username")
    room_id = request.cookies.get("room_id")
    if room_id is None or username is None:
        return
    emit("incoming", (f"{username} has disconnected", "red"), to=int(room_id))


def verify_hmac(message, messageHMAC, secret_key):
    try:
        mac = hmac.new(
            secret_key.encode(), message.encode(), hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(mac, messageHMAC)
    except ValueError:
        return False


# send message event handler
@socketio.on("send")
def send(encryptedMessage, messageHMAC, room_id):
    room.add_message(room_id, encryptedMessage)
    emit("incomingMessage", (encryptedMessage, messageHMAC), to=room_id)


# join room event handler
# sent when the user joins a room
@socketio.on("join")
def join(sender_name, receiver_name):

    receiver = db.get_user(receiver_name)
    if receiver is None:
        return "Unknown receiver!"

    sender = db.get_user(sender_name)
    if sender is None:
        return "Unknown sender!"

    room_id = room.get_room_id(receiver_name)

    # if the user is already inside of a room
    if room_id is not None:

        room.join_room(sender_name, room_id)
        join_room(room_id)
        # emit to everyone in the room except the sender
        emit(
            "incoming",
            (f"{sender_name} has joined the room {room_id}.", "green"),
            to=room_id,
            include_self=False,
        )
        # emit only to the sender
        emit(
            "incoming",
            (
                f"{sender_name} has joined the room {room_id}. Now talking to {receiver_name}.",
                "green",
            ),
        )
        for message in room.get_messages(room_id):
            emit("incomingHistory", message)
        return room_id

    # if the user isn't inside of any room,
    # perhaps this user has recently left a room
    # or is simply a new user looking to chat with someone
    room_id = room.create_room(sender_name, receiver_name)
    join_room(room_id)
    emit(
        "incoming",
        (
            f"{sender_name} has joined the room {room_id}. Now talking to {receiver_name}.",
            "green",
        ),
        to=room_id,
    )
    return room_id


# leave room event handler
@socketio.on("leave")
def leave(username, room_id):
    emit("incoming", (f"{username} has left the room.", "red"), to=room_id)
    leave_room(room_id)
    room.leave_room(username)


# send friend request event handler
@socketio.on("friendRequest")
def friendRequest(sender, receiver, room_id):
    emit(
        "incoming",
        (f"{sender} has sent {receiver} a friend request.", "red"),
        to=room_id,
    )

    db.send_request(sender, receiver)


@socketio.on("acceptRequest")
def acceptRequest(receiver, sender, room_id):
    emit(
        "incoming",
        (f"{receiver} has accepted {sender}'s friend request.", "red"),
        to=room_id,
    )

    db.acceptRequest(sender, receiver)


@socketio.on("rejectRequest")
def rejectRequest(receiver, sender, room_id):
    emit(
        "incoming",
        (f"{receiver} has rejected {sender}'s friend request.", "red"),
        to=room_id,
    )

    db.rejectRequest(sender, receiver)


@socketio.on("removeFriend")
def removeFriend(username, friend):
    db.removeFriend(username, friend)


@socketio.on("setRole")
def removeFriend(username, role):
    db.setRole(username, role)


@socketio.on("deleteMessage")
def deleteMessage(message, room_id):
    room.delete_message(room_id, message)


@socketio.on("muteUser")
def muteUser(message, room_id):
    db.muteUser(message, room_id)


@socketio.on("unmuteUser")
def unmuteUser(message, room_id):
    db.unmuteUser(message, room_id)
