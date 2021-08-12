from bson.objectid import ObjectId
from flask_login.mixins import UserMixin
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

