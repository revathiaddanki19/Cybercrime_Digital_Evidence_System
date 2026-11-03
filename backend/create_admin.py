
import re
from getpass import getpass

from models.user_model import create_user, users_collection


def create_first_admin():

    # Prevent creating another administrator through this script
    existing_admin = users_collection.find_one({
        "role": "admin"
    })

    if existing_admin:
        print("An administrator account already exists.")
        print("Admin setup has been stopped.")
        return

    print("\n======================================")
    print("  CREATE FIRST ADMINISTRATOR ACCOUNT")
    print("======================================\n")

    name = input("Enter administrator name: ").strip()
    email = input("Enter administrator email: ").strip().lower()

    if not name or not email:
        print("Name and email are required.")
        return

    if len(name) > 100:
        print("Name must not exceed 100 characters.")
        return

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        print("Please enter a valid email address.")
        return

    if users_collection.find_one({"email": email}):
        print("An account with this email already exists.")
        return

    password = getpass("Create administrator password: ")
    confirm_password = getpass("Confirm administrator password: ")

    if password != confirm_password:
        print("Passwords do not match.")
        return

    if len(password) < 8 or len(password.encode("utf-8")) > 72:
        print("Password must contain at least 8 characters and no more than 72 UTF-8 bytes.")
        return

    try:
        user = create_user(
            name=name,
            email=email,
            password=password,
            role="admin"
        )

        if user:
            print("\nAdministrator account created successfully!")
            print("Email:", user["email"])
            print("Role:", user["role"])
        else:
            print("Account creation failed. Email may already exist.")

    except ValueError as error:
        print("Error:", error)


if __name__ == "__main__":
    create_first_admin()
