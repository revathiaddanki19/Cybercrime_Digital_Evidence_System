
from datetime import datetime, timedelta, timezone
from functools import wraps
import os
import re

import jwt
from flask import Blueprint, request, jsonify, current_app

from models.user_model import (
    create_user,
    find_user_by_email,
    verify_password
)

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def token_required(function):
    """Check whether the request contains a valid JWT."""

    @wraps(function)
    def wrapper(*args, **kwargs):

        authorization = request.headers.get("Authorization", "")

        if not authorization.startswith("Bearer "):
            return jsonify({
                "status": "error",
                "message": "Authentication token is required."
            }), 401

        token = authorization.split(" ", 1)[1].strip()

        try:
            data = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )

            user = find_user_by_email(data["email"])

            if not user or not user.get("is_active", False):
                return jsonify({
                    "status": "error",
                    "message": "User account is inactive or unavailable."
                }), 401

            request.current_user = user

        except jwt.ExpiredSignatureError:
            return jsonify({
                "status": "error",
                "message": "Your session has expired. Please log in again."
            }), 401

        except (jwt.InvalidTokenError, KeyError):
            return jsonify({
                "status": "error",
                "message": "Invalid authentication token."
            }), 401

        return function(*args, **kwargs)

    return wrapper


def role_required(*allowed_roles):
    """Restrict an endpoint to specified user roles."""

    def decorator(function):

        @wraps(function)
        @token_required
        def wrapper(*args, **kwargs):

            if request.current_user.get("role") not in allowed_roles:
                return jsonify({
                    "status": "error",
                    "message": "You do not have permission to access this resource."
                }), 403

            return function(*args, **kwargs)

        return wrapper

    return decorator


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register an investigator account."""

    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({
            "status": "error",
            "message": "Name, email and password are required."
        }), 400

    if len(name) > 100:
        return jsonify({
            "status": "error",
            "message": "Name must not exceed 100 characters."
        }), 400

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return jsonify({
            "status": "error",
            "message": "Enter a valid email address."
        }), 400

    if len(password) < 8 or len(password.encode("utf-8")) > 72:
        return jsonify({
            "status": "error",
            "message": "Password must contain at least 8 characters and no more than 72 UTF-8 bytes."
        }), 400

    if find_user_by_email(email):
        return jsonify({
            "status": "error",
            "message": "An account with this email already exists."
        }), 409

    try:
        user = create_user(
            name=name,
            email=email,
            password=password,
            role="investigator"
        )

        if not user:
            return jsonify({
                "status": "error",
                "message": "An account with this email already exists."
            }), 409

        return jsonify({
            "status": "success",
            "message": "Investigator account registered successfully.",
            "user": {
                "id": str(user["_id"]),
                "name": user["name"],
                "email": user["email"],
                "role": user["role"]
            }
        }), 201

    except ValueError as error:
        return jsonify({
            "status": "error",
            "message": str(error)
        }), 400


@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate a user and issue a JWT."""

    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({
            "status": "error",
            "message": "Email and password are required."
        }), 400

    user = find_user_by_email(email)

    if (
        not user
        or not user.get("is_active", False)
        or not verify_password(password, user["password"])
    ):
        return jsonify({
            "status": "error",
            "message": "Invalid email or password."
        }), 401

    secret = current_app.config.get("SECRET_KEY")

    if not secret:
        return jsonify({
            "status": "error",
            "message": "Server authentication is not configured."
        }), 500

    expiration_hours = int(os.getenv("JWT_EXPIRATION_HOURS", "8"))

    token = jwt.encode(
        {
            "user_id": str(user["_id"]),
            "email": user["email"],
            "role": user["role"],
            "exp": datetime.now(timezone.utc)
                   + timedelta(hours=expiration_hours)
        },
        secret,
        algorithm="HS256"
    )

    return jsonify({
        "status": "success",
        "message": "Login successful.",
        "token": token,
        "user": {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }
    }), 200


@auth_bp.route("/profile", methods=["GET"])
@token_required
def profile():
    """Return the currently authenticated user's profile."""

    user = request.current_user

    return jsonify({
        "status": "success",
        "user": {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }
    }), 200


@auth_bp.route("/admin-test", methods=["GET"])
@role_required("admin")
def admin_test():
    """Example endpoint accessible only to administrators."""

    return jsonify({
        "status": "success",
        "message": "Admin access verified."
    }), 200
