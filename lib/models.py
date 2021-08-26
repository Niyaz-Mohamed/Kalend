from bson.objectid import ObjectId
from flask_login.mixins import UserMixin
from datetime import datetime
from lib import mongo, login

class User(UserMixin):

    def __init__(self, id):
        self.id = str(id)
        mongoId = ObjectId(self.id)
        # Get values based on username
        try:
            self.username = mongo.db.users.find_one(
                {'_id': mongoId})['username']
            self.password = mongo.db.users.find_one(
                {'_id': mongoId})['password']
            self.email = mongo.db.users.find_one(
                {'_id': mongoId})['email']
            self.timestamp = mongo.db.users.find_one(
                {'_id': mongoId})['timestamp']
        except:
            self.username = None
            self.password = None
            self.email = None
            self.timestamp = None

    def __repr__(self):
        return 'User {}'.format(self.username)

    @login.user_loader
    def load_user(user_id):
        userData = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        loadedUser = User(userData.get('_id'))
        return loadedUser

class Event():

    id: ObjectId = None
    creatorId: ObjectId = None
    name = None
    desc = None
    startTime: datetime = None
    endTime: datetime = None
    status = None
    location = None
    totalSlots = None

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.desc = kwargs.get('desc')
        self.startTime = kwargs.get('startTime')
        self.endTime = kwargs.get('endTime')
        self.location = kwargs.get('location')
        self.totalSlots = kwargs.get('totalSlots')
        self.creatorId = kwargs.get('creatorId')
        if self.startTime < datetime.now() < self.endTime:
            self.status = 'Ongoing'
        elif datetime.now() < self.startTime:
            self.status = 'Upcoming'
        else:
            self.status = 'Completed'
        self.formattedStartTime = self.startTime.strftime('%m/%d/%Y, %H:%M')
        self.formattedEndTime = self.endTime.strftime('%m/%d/%Y, %H:%M')
        self.creatorName = mongo.db.users.find_one(
            {'_id': ObjectId(str(self.creatorId))}).get('username')

def eventFromData(data: dict) -> Event:
    return Event(
        id=data.get('_id'),
        name=data.get('name'),
        desc=data.get('desc'),
        startTime=data.get('startTime'),
        endTime=data.get('endTime'),
        location=data.get('location'),
        totalSlots=data.get('totalSlots'),
        creatorId=data.get('creatorId')
    )
