
from datetime import datetime, timezone

import bcrypt

from config.db import db


# MongoDB users collection
users_collection = db["users"]


def hash_password(password):
    """Hash a password securely using bcrypt."""

    password_bytes = password.encode("utf-8")

    if len(password_bytes) > 72:
        raise ValueError("Password must not exceed 72 UTF-8 bytes.")

    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    )

    return hashed.decode("utf-8")


def verify_password(password, stored_hash):
    """Verify a password against its stored bcrypt hash."""

    password_bytes = password.encode("utf-8")
    hashed_bytes = stored_hash.encode("utf-8")

    if len(password_bytes) > 72:
        return False

    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_user(name, email, password, role="investigator"):
    """Create a new user in MongoDB."""

    email = email.strip().lower()

    if users_collection.find_one({"email": email}):
        return None

    user = {
        "name": name.strip(),
        "email": email,
        "password": hash_password(password),
        "role": role,
        "is_active": True,
        "created_at": datetime.now(timezone.utc)
    }

    result = users_collection.insert_one(user)

    user["_id"] = result.inserted_id

    return user


def find_user_by_email(email):
    """Find a user using their email address."""

    return users_collection.find_one({
        "email": email.strip().lower()
    })


def find_user_by_id(user_id):
    """Find a user using their MongoDB ID."""

    from bson import ObjectId
    from bson.errors import InvalidId

    try:
        return users_collection.find_one({
            "_id": ObjectId(user_id)
        })
    except (InvalidId, TypeError):
        return None
