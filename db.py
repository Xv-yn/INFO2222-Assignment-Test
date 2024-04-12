"""
db
database file, containing all the logic to interface with the sql database
"""

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import *

# creates the database directory
Path("database").mkdir(exist_ok=True)

# "database/main.db" specifies the database file
# change it if you wish
# turn echo = True to display the sql output
engine = create_engine("sqlite:///database/main.db", echo=False)

# initializes the database
Base.metadata.create_all(engine)


# inserts a user to the database
def insert_user(username: str, password: str, salt: str):
    with Session(engine) as session:
        user = User(
            username=username,
            password=password,
            salt=salt,
            friends="",
            requestsReceived="",
            requestsSent="",
        )
        session.add(user)
        session.commit()


# gets a user from the database
def get_user(username: str):
    with Session(engine) as session:
        return session.get(User, username)


def send_request(sender: str, receiver: str):
    with Session(engine) as session:
        sender = session.get(User, sender)
        receiver = session.get(User, receiver)

        if sender and receiver:
            sender.requestsSent += receiver.username + ","
            receiver.requestsReceived += sender.username + ","

        session.commit()


def getFriends(username: str):
    with Session(engine) as session:
        user = session.get(User, username)
        friendsList = user.friends.split(",")
        friendsList.pop()
        return friendsList


def getRequestsSent(username: str):
    with Session(engine) as session:
        user = session.get(User, username)
        requestsSentList = user.requestsSent.split(",")
        requestsSentList.pop()
        return requestsSentList


def getRequestsReceived(username: str):
    with Session(engine) as session:
        user = session.get(User, username)
        requestsReceivedList = user.requestsReceived.split(",")
        requestsReceivedList.pop()
        return requestsReceivedList


def acceptRequest(sender: str, receiver: str):
    with Session(engine) as session:
        sender = session.get(User, sender)
        receiver = session.get(User, receiver)

        receiverReceivedList = receiver.requestsReceived.split(",")
        receiverReceivedList.pop()
        senderSentList = sender.requestsSent.split(",")
        senderSentList.pop()

        temp1 = ""
        temp2 = ""

        for i in receiverReceivedList:
            if i == sender.username:
                receiverReceivedList.remove(sender.username)
            else:
                temp1 += i

        for i in senderSentList:
            if i == receiver.username:
                senderSentList.remove(receiver.username)
            else:
                temp2 += i

        receiver.requestsReceived = temp1
        receiver.friends += sender.username + ","
        sender.requestsSent = temp2
        sender.friends += receiver.username + ","

        session.commit()
