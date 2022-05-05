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
    email = db.Column(db.String, nullable=False, unique=True)
    password_digest = db.Column(db.String, nullable=False)

    # Relationships
    caches_created = db.relationship("Cache")
    caches_completed = db.relationship("Cache", secondary=caches_completed_table, back_populates="user_completed")
    caches_favorited = db.relationship("Cache", secondary=favorites_table, back_populates="user_favorited")

    # Session information
    session_token = db.Column(db.String, nullable=False, unique=True)
    session_expiration = db.Column(db.DateTime, nullable=False)
    update_token = db.Column(db.String, nullable=False, unique=True)

    def __init__(self, **kwargs):
        """
        Initializes a User object
        """
        self.name = kwargs.get("name")
        self.username = kwargs.get("username", "")
        self.email = kwargs.get("email")
        self.password_digest = bcrypt.hashpw(kwargs.get("password").encode("utf8"), bcrypt.gensalt(rounds=13))
        self.renew_session()

    def serialize(self):
        """
        Serializes a User object
        """
        return {
            "id": self.id,
            "name": self.name,
            "username": self.username,
            "caches_created": [cache.serialize() for cache in self.caches_created],
            "caches_completed": [cache.serialize() for cache in self.caches_completed],
            "favorites": [cache.serialize() for cache in self.caches_favorited],
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
    location = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    hint = db.Column(db.String, nullable=False)
    size = db.Column(db.String, nullable=False)
    difficulty = db.Column(db.Integer, nullable=False)
    terrain = db.Column(db.Integer, nullable=False)
    last_found = db.Column(db.String, nullable=False)
    date_created = db.Column(db.String, nullable=False)

    # Relationships
    created_by = db.Column(db.Integer, db.ForeignKey("users.username"), nullable=False)
    user_completed = db.relationship("User", secondary=caches_completed_table, back_populates="caches_completed")
    user_favorited = db.relationship("User", secondary=favorites_table, back_populates="caches_favorited")

    def __init__(self, **kwargs):
        """
        Initializes a Cache object
        """
        self.name = kwargs.get("name", "")
        self.location = kwargs.get("location", "")
        self.description = kwargs.get("description", "")
        self.hint = kwargs.get("hint", "")
        self.size = kwargs.get("size", "")
        self.difficulty = kwargs.get("difficulty", "")
        self.terrain = kwargs.get("terrain", "")
        self.last_found = kwargs.get("last_found", "")
        self.date_created = kwargs.get("date_created", "")
        self.created_by = kwargs.get("created_by", "")

    def serialize(self):
        """
        Serializes a Cache object
        """
        user = User.query.filter_by(username=self.created_by).first()
        return {
            "id": self.id,
            "name": self.name,
            "created_by": user.username,
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