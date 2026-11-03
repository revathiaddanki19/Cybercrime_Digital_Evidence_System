
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from config.db import test_connection, db

import os

# Load environment variables
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# Enable frontend communication
CORS(app)

# Application configuration
app.config["SECRET_KEY"] = os.getenv("JWT_SECRET")

# Maximum upload size: 20 MB
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024


# Home route
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Cybercrime Digital Evidence Management System API",
        "status": "Running successfully"
    })


# Health check route
@app.route("/api/health", methods=["GET"])
def health_check():
    try:
        db.command("ping")

        return jsonify({
            "status": "success",
            "message": "Backend and MongoDB are connected",
            "database": "CybercrimeEvidenceDB"
        }), 200

    except Exception:
        return jsonify({
            "status": "error",
            "message": "Database connection failed"
        }), 500


# Start application
if __name__ == "__main__":

    if test_connection():
        print("Starting Cybercrime Digital Evidence Management System...")

        app.run(
            host="127.0.0.1",
            port=5000,
            debug=True
        )

    else:
        print("Unable to start application. Check MongoDB connection.")
