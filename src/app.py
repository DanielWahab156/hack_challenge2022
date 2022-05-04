from db import db
from db import User
from db import Cache
from flask import Flask, request
import json
import os


app = Flask(__name__)
db_filename = "geocache.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.drop_all()
    db.create_all()

#generalized response formats
def success_response(data, code=200):
    """
    Generalized success response function
    """
    return json.dumps(data), code

def failure_response(message, code=404):
    """
    Generalized failure response function
    """
    return json.dumps({"error": message}), code


# -- User ROUTES ------------------------------------------------------

# Route 1: Get session token
@app.route("/secret/", methods=["GET"])

# Route 2: Get a specific user
@app.route("/users/<int:user_id>/")
def get_user(user_id):
    """
    Endpoint for getting user by id
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found!")
    return success_response(user.serialize())

# Route 3: Create a new user
@app.route("/users/", methods=["POST"])
def create_user():
    """
    Endpoint for creating a new user
    """
    body = json.loads(request.data)

    name = body.get("name")
    if name is None:
        return failure_response("Enter valid name!", 400)
    username = body.get("username")
    if username is None:
        return failure_response("Enter valid username!", 400)

    # if user tries to take an already created username or is this covered by
    # the fact that username is unique? (which would create an error when we try
    # to create a new User object)
    user = User.query.filter_by(username=username).first()
    if user is not None:
        return failure_response("Username already taken!", 400)

    new_user = User(name=name, username=username)
    db.session.add(new_user)
    db.session.commit()
    return success_response(new_user.serialize(), 201)

# Route 4: Logging in a user
@app.route("/login/", methods=["POST"])

# Route 5: Update a user's session
@app.route("/session/", methods=["POST"])

# Route 6: Logging out a user
@app.route("/logout/", methods=["POST"])

# Route 7: Delete a user by id
@app.route("/users/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
    """
    Endpoint for deleting a user by id
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found!")

    db.session.delete(user)
    db.session.commit()
    return success_response(user.serialize())


# -- Cache ROUTES ------------------------------------------------------ 

# Route 1: Get all caches
@app.route("/caches/")
def get_all_caches():
    """
    Endpoint for getting all caches
    """
    caches = []
    for cache in Cache.query.all():
        caches.append(cache.serialize())
    return success_response({"caches": caches})

# Route 2: Get all caches for a user (that they created)
@app.route("/caches/<username>/")
def get_cache(username):
    """
    Endpoint for getting all caches for a specific user (that they created)
    """
    caches = []
    for cache in Cache.query.filter_by(created_by=username):
        caches.append(cache.serialize())
    return success_response({"caches": caches})

# Route 3: Get all caches for a user (that they completed)
@app.route("/caches/<int:user_id>/")
def get_cache(user_id):
    """
    Endpoint for getting all caches for a specific user (that they completed)
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found!")
    
    caches = []
    for cache in user.caches_completed:
        caches.append(cache.serialize())
    return success_response({"caches": caches})

# Route 4: Get all caches for a user (that they favorited)
@app.route("/caches/<int:user_id>/")
def get_cache(user_id):
    """
    Endpoint for getting all caches for a specific user (that they favorited)
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found!")
    
    caches = []
    for cache in user.caches_favorited:
        caches.append(cache.serialize())
    return success_response({"caches": caches})

# Route 5: Get caches that follow a certain category (size, difficulty, etc)
# How would we do something like get all caches closest to me
# I don't think this is right.
@app.route("/caches/<category>/<item>/", methods=["POST"])
def get_conditional_cache(category, item):
    """
    Endpoint for getting all caches that follow a certain category
    """
    caches = []
    for cache in Cache.query.filter_by(category=item):
        caches.append(cache.seralize())
    return success_response({"caches": caches})


# Route 6: Create a cache (associated with a specific user)
@app.route("/caches/<int:user_id>/", methods=["POST"])
def create_cache(user_id):
    """
    Endpoint for creating a cache for a user
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")

    body = json.loads(request.data)
    created_by = body.get("created_by")
    # how do I make sure this is a valid username?
    if created_by != user.username:
        return failure_response("Incorrect username", 400)
    location = body.get("location")
    if location is None:
        return failure_response("Enter valid location", 400)
    description = body.get("description")
    if description is None:
        return failure_response("Enter valid description", 400)
    hint = body.get("hint")
    size = body.get("size")
    difficulty = body.get("difficulty")
    terrain = body.get("terrain")
    last_found = body.get("last_found")
    date_created = body.get("date_created")
    if date_created is None:
        return failure_response("Enter valid date", 400)
    
    new_cache = Cache(
        created_by=created_by,
        location=location,
        description=description,
        hint=hint,
        size=size,
        difficulty=difficulty,
        terrain=terrain,
        last_found=last_found,
        date_created=date_created,
        user_id=user_id
    )

    db.session.add(new_cache)
    db.session.commit()
    return success_response(new_cache.serialize(), 201)

# Route 7: Add a cache to a specific user's completed_caches
@app.route("/caches/<int:user_id>/add/completed/", methods=["POST"])
def add_cache(user_id):
    """
    Endpoint for adding a cache to a specific user's completed caches or favorites
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found!")
    
    body = json.loads(request.data)
    cache_id = body.get("cache_id")
    if cache_id is None:
        return failure_response("Enter valid cache!", 400)
    
    cache = Cache.query.filter_by(id=cache_id).first()
    user.caches_completed.append(cache)
    db.session.commit()
    return success_response(cache.serialize())

# Route 8: Add a cache to a specific user's favorites
@app.route("/caches/<int:user_id>/add/favorited/", methods=["POST"])
def add_favorite(user_id):
    """
    Endpoint for adding a cache to a user's favorited caches
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found!")
    
    body = json.loads(request.data)
    cache_id = body.get("cache_id")
    if cache_id is None:
        return failure_response("Enter valid cache!", 400)
    
    cache = Cache.query.filter_by(id=cache_id).first()
    user.caches_favorited.append(cache)
    db.session.commit()
    return success_response(cache.serialize())

# Route 7&8: Update the status of a cache (completed or favorited)
@app.route("/caches/<int:user_id>/add/", methods=["POST"])
def add_cache(user_id):
    """
    Endpoint for updating the status of a cache (completed or favorited)
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found!")
    
    body = json.loads(request.data)
    cache_id = body.get("cache_id")
    if cache_id is None:
        return failure_response("Enter valid cache!", 400)
    status = body.get("status")
    if status is None:
        return failure_response("Ivalid status", 400)

    cache = Cache.query.filter_by(id=cache_id).first()
    if status == "completed":
        user.caches_completed.append(cache)
    if status == "favorited":
        user.caches_favorited.append(cache)

    db.session.commit()
    return success_response(cache.serialize())


# Route 9: Delete cache by id
@app.route("/caches/<cache_id>", methods=["DELETE"])
def delete_cache(cache_id):
    """
    Endpoint for deleting a cache
    """
    cache = Cache.query.filter_by(id=cache_id).first()
    if cache is None:
        return failure_response("Cache not found!")

    db.session.delete(cache)
    db.session.commit()
    return success_response(cache.serialize())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
