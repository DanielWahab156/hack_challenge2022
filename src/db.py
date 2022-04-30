from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Users(db.Model):
    '''
    Class for the users table (untested - needs cache class to implement fully)
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


class Cache(db.Model):
    """
    Cache model
    """
    __tablename__ = "caches"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_by = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    # distance_from_user = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)
    hint = db.Column(db.String,)
    #is there a way to make only 3 inputs possible (small, medium large) drop-down menu
    size = db.Column()
    # elementary, middle, high, college
    difficulty = db.Column()
    # easy, medium, hard
    terrain = db.Column()
    # we need dates here
    last_found = db.Column(db.Integer)
    date_created = db.Column(db.Integer, nullable=False)
    # user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __init__(self, **kwargs):
        """
        Initializes a Cache object
        """
        self.created_by = kwargs.get("created_by", "")
        self.location = kwargs.get("location", "")
        # self.distance_from_user = kwargs.get("distance_from_user", "")
        self.description = kwargs.get("description", "")
        self.hint = kwargs.get("hint", "")
        self.size = kwargs.get("size", "")
        self.difficulty = kwargs.get("difficulty", "")
        self.terrain = kwargs.get("terrain", "")
        self.last_found = kwargs.get("last_found", "")
        self.date_created = kwargs.get("date_created", "")
        # self.user_id = kwargs.get("user_id", "")

    def serialize(self):
        """
        Serializes a Cache object
        """
        user = User.query.filter_by(username=self.username)# .first()
        return {
            "id": self.id,
            "location": self.location,
            # "distance_from_user": self.distance_from_user,
            "description": self.description,
            "hint": self.hint,
            "size": self.size,
            "difficulty": self.difficulty,
            "terrain": self.terrain,
            "last_found": self.last_found,
            "date_created": self.date_created,
            "user": user.username
        }