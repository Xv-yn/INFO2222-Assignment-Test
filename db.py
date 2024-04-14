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
            if sender.requestsSent == "":
                sender.requestsSent += receiver.username
            else:
                sender.requestsSent += "," + receiver.username
            if receiver.requestsReceived == "":
                receiver.requestsReceived += sender.username
            else:
                receiver.requestsReceived += "," + sender.username

        session.commit()


def getFriends(username: str):
    with Session(engine) as session:
        user = session.get(User, username)
        friendsList = user.friends.split(",")
        if len(friendsList) == 1 and friendsList[0] == "":
            friendsList.pop()
        return friendsList


def getRequestsSent(username: str):
    with Session(engine) as session:
        user = session.get(User, username)
        requestsSentList = user.requestsSent.split(",")
        if len(requestsSentList) == 1 and requestsSentList[0] == "":
            requestsSentList.pop()
        return requestsSentList


def getRequestsReceived(username: str):
    with Session(engine) as session:
        user = session.get(User, username)
        requestsReceivedList = user.requestsReceived.split(",")
        if len(requestsReceivedList) == 1 and requestsReceivedList[0] == "":
            requestsReceivedList.pop()
        return requestsReceivedList


def acceptRequest(sender: str, receiver: str):
    with Session(engine) as session:
        sender = session.get(User, sender)
        receiver = session.get(User, receiver)

        receiverReceivedList = receiver.requestsReceived.split(",")
        senderSentList = sender.requestsSent.split(",")

        temp1 = list(filter(lambda x: x != sender.username, receiverReceivedList))
        receiver.requestsReceived = ",".join(temp1)

        temp2 = list(filter(lambda x: x != receiver.username, senderSentList))
        sender.requestsSent = ",".join(temp2)

        if receiver.friends == "":
            receiver.friends += sender.username
        else:
            receiver.friends += "," + sender.username
        if sender.friends == "":
            sender.friends += receiver.username
        else:
            sender.friends += "," + receiver.username

        session.commit()


def rejectRequest(sender: str, receiver: str):
    with Session(engine) as session:
        sender = session.get(User, sender)
        receiver = session.get(User, receiver)

        receiverReceivedList = receiver.requestsReceived.split(",")
        senderSentList = sender.requestsSent.split(",")

        temp1 = list(filter(lambda x: x != sender.username, receiverReceivedList))
        receiver.requestsReceived = ",".join(temp1)

        temp2 = list(filter(lambda x: x != receiver.username, senderSentList))
        sender.requestsSent = ",".join(temp2)

        session.commit()
