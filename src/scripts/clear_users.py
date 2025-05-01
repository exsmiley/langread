#!/usr/bin/env python3
"""
Script to clear all users from the database for testing purposes.
This should only be used in development environments.
"""

import asyncio
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.models.database import DatabaseService

async def clear_users():
    """Clear all users from the database"""
    print("Connecting to database...")
    db_service = DatabaseService()
    await db_service.connect()
    
    # Check if users collection is initialized
    if db_service.users_collection is None:
        print("Error: Users collection not initialized.")
        return
    
    # Get current count
    count = await db_service.users_collection.count_documents({})
    print(f"Found {count} users in the database.")
    
    # Confirm with user
    confirm = input("Are you sure you want to delete ALL users? This cannot be undone. (y/n): ")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        return
    
    # Delete all users
    result = await db_service.users_collection.delete_many({})
    print(f"Deleted {result.deleted_count} users from the database.")

if __name__ == "__main__":
    asyncio.run(clear_users())
