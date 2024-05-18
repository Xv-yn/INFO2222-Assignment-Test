"""
models
defines sql alchemy data models
also contains the definition for the room class used to keep track of socket.io rooms

Just a sidenote, using SQLAlchemy is a pain. If you want to go above and beyond, 
do this whole project in Node.js + Express and use Prisma instead, 
Prisma docs also looks so much better in comparison

or use SQLite, if you're not into fancy ORMs (but be mindful of Injection attacks :) )
"""

from typing import Dict, List

from sqlalchemy import JSON, String
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# data models
class Base(DeclarativeBase):
    pass


# model to store user information
class User(Base):
    __tablename__ = "user"

    # looks complicated but basically means
    # I want a username column of type string,
    # and I want this column to be my primary key
    # then accessing john.username -> will give me some data of type string
    # in other words we've mapped the username Python object property to an SQL column of type String
    username: Mapped[str] = mapped_column(String, primary_key=True)
    password: Mapped[str] = mapped_column(String)
    salt: Mapped[str] = mapped_column(String)
    friends: Mapped[str] = mapped_column(String)
    requestsReceived: Mapped[str] = mapped_column(String)
    requestsSent: Mapped[str] = mapped_column(String)
    accessLevel: Mapped[str] = mapped_column(String)

    def getFriends(self):
        friendsList = self.friends.split(",")
        if len(friendsList) == 1 and friendsList[0] == "":
            friendsList.pop()
        return friendsList

    def getRequestsSent(self):
        requestsSentList = self.requestsSent.split(",")
        if len(requestsSentList) == 1 and requestsSentList[0] == "":
            requestsSentList.pop()
        return requestsSentList

    def getRequestsReceived(self):
        requestsReceivedList = self.requestsReceived.split(",")
        if len(requestsReceivedList) == 1 and requestsReceivedList[0] == "":
            requestsReceivedList.pop()
        return requestsReceivedList


# stateful counter used to generate the room id
class Counter:
    def __init__(self):
        self.counter = 0

    def get(self):
        self.counter += 1
        return self.counter


# Room class, used to keep track of which username is in which room
class Room:
    def __init__(self):
        self.counter = Counter()
        # dictionary that maps the username to the room id
        # for example self.dict["John"] -> gives you the room id of
        # the room where John is in
        self.dict: Dict[str, int] = {}
        self.messageHistory: Dict[int, List[str]] = {}

    def create_room(self, sender: str, receiver: str) -> int:
        room_id = self.counter.get()
        self.dict[sender] = room_id
        self.dict[receiver] = room_id
        return room_id

    def join_room(self, sender: str, room_id: int) -> int:
        self.dict[sender] = room_id

    def leave_room(self, user):
        if user not in self.dict.keys():
            return
        del self.dict[user]

    def get_room_id(self, user: str):
        if user not in self.dict.keys():
            return None
        return self.dict[user]

    def add_message(self, room_id: int, message: str):
        if room_id not in self.messageHistory:
            self.messageHistory[room_id] = []
        self.messageHistory[room_id].append(message)

    def get_messages(self, room_id: int) -> List[str]:
        return self.messageHistory.get(room_id, [])

    def add_message(self, room_id: int, message: str):
        if room_id not in self.messageHistory:
            self.messageHistory[room_id] = []
        self.messageHistory[room_id].append(message)

    def delete_message(self, room_id: int, message: str):
        self.messageHistory[room_id].remove(message)
