#!/usr/bin/env python3
"""
Script to reset the users collection in the Lingogi database.
Use with caution - this will delete all user accounts!
"""

import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def reset_database():
    # Get MongoDB connection string from environment or use default
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/langread")
    print(f"Connecting to database at {mongo_uri}")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongo_uri)
    db = client.get_default_database()
    
    # Access the users collection
    users_collection = db.users
    
    # Get count of users
    count = await users_collection.count_documents({})
    print(f"Found {count} users in the database.")
    
    if count == 0:
        print("No users to delete.")
        return
    
    # Ask for confirmation
    confirm = input(f"Are you sure you want to delete all {count} users? This cannot be undone. (yes/no): ")
    if confirm.lower() != "yes":
        print("Operation cancelled.")
        return
    
    # Delete all users
    result = await users_collection.delete_many({})
    print(f"Successfully deleted {result.deleted_count} users from the database.")

if __name__ == "__main__":
    asyncio.run(reset_database())
