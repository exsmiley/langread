"""
Common FastAPI dependencies for the Lingogi API.
"""
from fastapi import Depends
from src.models.database import DatabaseService

# Global database service instance
db_service = DatabaseService()

# Dependency to get the database service
def get_database_service():
    """Dependency for injecting the database service."""
    return db_service
