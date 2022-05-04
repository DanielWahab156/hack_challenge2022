from flask_sqlalchemy import SQLAlchemy
import datetime
import hashlib
import os
import bcrypt

db = SQLAlchemy()

favorites_table = db.Table(
    "favorites",
    db.Column("users_id", db.String, db.ForeignKey("users.id")),
    db.Column("cache_id", db.String, db.ForeignKey("caches.id")),
)

caches_completed_table = db.Table(
    "caches_completed",
    db.Column("users_id", db.String, db.ForeignKey("users.id")),
    db.Column("caches_id", db.String, db.ForeignKey("caches.id")),
)

class User(db.Model):
    """
    User model
    """
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False, unique=True)
    
    caches = db.relationship("Cache")
    caches_completed = db.relationship("Cache", secondary=caches_completed_table, back_populates="users")
    caches_favorited = db.relationship("Cache", secondary=favorites_table, back_populates="users")

    session_token = db.Column(db.String, nullable=False)
    session_expiration = db.Column(db.DateTime, nullable=False)
    update_token = db.Column(db.String, nullable=False, unique=True)

    def __init__(self, **kwargs):
        """
        Initializes a User object
        """
        self.username = kwargs.get("username", "")
        self.caches_completed = kwargs.get("caches_completed")
        self.favorites = kwargs.get("favorites")

    def serialize(self):
        """
        Serializes a User object
        """
        return {
            "id": self.id,
            "username": self.username,
            "caches_completed": [cache.simple_serialize() for cache in self.caches_completed],
            "favorites": self.favorites,
        }
    
    def _urlsafe_base_64(self):
        """
        Randomly generates hashed tokens (used for session/update tokens)
        """
        return hashlib.sha1(os.urandom(64)).hexdigest()

    def renew_session(self):
        """
        Renews the sessions, i.e.
        1. Creates a new session token
        2. Sets the expiration time of the session to be a day from now
        3. Creates a new update token
        """
        self.session_token = self._urlsafe_base_64()
        self.session_expiration = datetime.datetime.now() + datetime.timedelta(days=1)
        self.update_token = self._urlsafe_base_64()

    def verify_password(self, password):
        """
        Verifies the password of a user
        """
        return bcrypt.checkpw(password.encode("utf8"), self.password_digest)

    def verify_session_token(self, session_token):
        """
        Verifies the session token of a user
        """
        return session_token == self.session_token and datetime.datetime.now() < self.session_expiration

    def verify_update_token(self, update_token):
        """
        Verifies the update token of a user
        """
        return update_token == self.update_token


class Cache(db.Model):
    """
    Cache model
    """
    __tablename__ = "caches"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    created_by = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    hint = db.Column(db.String)
    size = db.Column(db.String)
    difficulty = db.Column(db.String)
    terrain = db.Column(db.String)
    last_found = db.Column(db.Integer)
    date_created = db.Column(db.Integer, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user_completed = db.relationship("User", secondary=caches_completed_table, back_populates="caches")
    user_favorited = db.relationship("User", secondary=favorites_table, back_populates="caches")

    def __init__(self, **kwargs):
        """
        Initializes a Cache object
        """
        self.created_by = kwargs.get("created_by", "")
        self.location = kwargs.get("location", "")
        self.description = kwargs.get("description", "")
        self.hint = kwargs.get("hint", "")
        self.size = kwargs.get("size", "")
        self.difficulty = kwargs.get("difficulty", "")
        self.terrain = kwargs.get("terrain", "")
        self.last_found = kwargs.get("last_found", "")
        self.date_created = kwargs.get("date_created", "")

    def serialize(self):
        """
        Serializes a Cache object
        """
        user = User.query.filter_by(username=self.username)
        return {
            "id": self.id,
            "username": user.username,
            "location": self.location,
            "description": self.description,
            "hint": self.hint,
            "size": self.size,
            "difficulty": self.difficulty,
            "terrain": self.terrain,
            "last_found": self.last_found,
            "date_created": self.date_created,
        }

    def simple_serialize(self):
        """
        Simple serializes a Cache object with compact information
        """
        return {
            "id": self.id,
            "location": self.location,
            "description": self.description,
            "difficulty": self.difficulty,
            "date_created": self.date_created,
        }