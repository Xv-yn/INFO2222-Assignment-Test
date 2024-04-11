'''
db
database file, containing all the logic to interface with the sql database
'''

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import *

from pathlib import Path

# creates the database directory
Path("database") \
    .mkdir(exist_ok=True)

# "database/main.db" specifies the database file
# change it if you wish
# turn echo = True to display the sql output
engine = create_engine("sqlite:///database/main.db", echo=False)

# initializes the database
Base.metadata.create_all(engine)

# inserts a user to the database
def insert_user(username: str, password: str, salt: str):
    with Session(engine) as session:
        user = User(username=username, password=password, salt=salt, friends="", requestsReceived="", requestsSent="")
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