from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Users(db.Model):
    '''
    Class for the users table (untested)
    '''

    __tablename__ = "assignments"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    caches_completed = db.Column(db.Integer, db.ForeignKey("caches.id"), nullable=False)
    favorites = db.Column(db.Integer, db.ForeignKey("caches.id"), nullable=False)

    def __init__(self, **kwargs):
        self.username = kwargs.get("username", "")
        self.caches_completed = kwargs.get("caches_completed")
        self.favorites = kwargs.get("favorites")

    def serialize(self):
        '''
        Full serialization of the users table
        '''

        return {
            "id": self.id,
            "username": self.username,
            "caches_completed": self.caches_completed,
            "favorites": self.favorites,
        }