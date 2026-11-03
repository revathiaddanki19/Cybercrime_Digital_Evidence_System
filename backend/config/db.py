
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000
)

db = client[DATABASE_NAME]


def test_connection():
    try:
        client.admin.command("ping")
        print("MongoDB connected successfully!")
        print(f"Database: {DATABASE_NAME}")
        return True

    except ConnectionFailure as error:
        print("MongoDB connection failed:", error)
        return False
