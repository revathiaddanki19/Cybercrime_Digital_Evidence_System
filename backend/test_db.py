
from config.db import test_connection

if test_connection():
    print("Database test completed successfully!")
else:
    print("Please check your MongoDB configuration.")
