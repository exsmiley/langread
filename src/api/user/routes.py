from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Dict, Any, Optional
import os

from src.api.models.user import UserResponse, UserUpdate
from src.api.auth.routes import get_current_user
from src.models.database import DatabaseService
from src.api.db_helpers import get_database_service

router = APIRouter(prefix="/api/user", tags=["user"])

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    current_user: UserResponse = Depends(get_current_user)
):
    """Get the current user's profile"""
    return current_user

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    user_data: UserUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: DatabaseService = Depends(get_database_service)
):
    """Update the current user's profile"""
    update_data = {k: v for k, v in user_data.model_dump(exclude_unset=True).items() if v is not None}
    
    if not update_data:
        # Nothing to update
        return current_user
        
    # Print received data for debugging
    print(f"\n==== PROFILE UPDATE DEBUG INFO ====")
    print(f"Original update data: {update_data}")
    print(f"User ID: {current_user.id}")
    
    # Handle additional_languages properly - ensure they are serialized correctly
    if 'additional_languages' in update_data:
        if update_data['additional_languages'] is None:
            # If None was passed, set to empty list
            update_data['additional_languages'] = []
            print(f"Setting additional_languages to empty list")
        else:
            # Explicitly convert each language object to dict
            print(f"Original additional languages: {update_data['additional_languages']}")
            update_data['additional_languages'] = [
                lang if isinstance(lang, dict) else lang.dict() 
                for lang in update_data['additional_languages']
            ]
            print(f"Converted additional languages: {update_data['additional_languages']}")
            
            # Ensure isDefault is properly set for each language
            for lang in update_data['additional_languages']:
                if 'isDefault' not in lang:
                    lang['isDefault'] = False
            print(f"Final additional languages to save: {update_data['additional_languages']}")
    
    print(f"MongoDB update query: {{'_id': ObjectId('{current_user.id}')}}")
    print(f"MongoDB update operation: {{$set: {update_data}}}")
    
    # Perform the update
    update_result = await db.users_collection.update_one(
        {"_id": ObjectId(current_user.id)},
        {"$set": update_data}
    )
    print(f"Update result: {{'matched_count': {update_result.matched_count}, 'modified_count': {update_result.modified_count}}}")
    
    # Get the updated user
    user = await db.users_collection.find_one({"_id": ObjectId(current_user.id)})
    print(f"Retrieved user after update: {user}")
    
    # Ensure backward compatibility with existing users who might not have additional_languages
    if user and 'additional_languages' not in user:
        print(f"'additional_languages' field missing, adding it to user")
        # Add the additional_languages field with default empty list
        add_field_result = await db.users_collection.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": {"additional_languages": []}}
        )
        print(f"Result of adding 'additional_languages' field: {{'matched_count': {add_field_result.matched_count}, 'modified_count': {add_field_result.modified_count}}}")
        user = await db.users_collection.find_one({"_id": ObjectId(current_user.id)})
        print(f"User after adding 'additional_languages' field: {user}")
    
    if user is None:
        print("ERROR: User not found after update!")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Convert ObjectId to string
    user["id"] = str(user["_id"])
    print(f"Final user data before creating response: {user}")
    
    # Create the response object
    response = UserResponse(**user)
    print(f"Response model: {response.model_dump()}")
    print(f"Response additional_languages: {response.additional_languages}")
    print("==== END PROFILE UPDATE DEBUG INFO ====\n")
    
    return response

@router.post("/save-article")
async def save_article(
    article_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: DatabaseService = Depends(get_database_service)
):
    """Save an article to the user's saved articles list"""
    # Check if article already saved
    user = await db.users_collection.find_one({
        "_id": ObjectId(current_user.id),
        "saved_articles": article_id
    })
    
    if user:
        return {"message": "Article already saved"}
    
    # Add article to saved list
    await db.users_collection.update_one(
        {"_id": ObjectId(current_user.id)},
        {"$push": {"saved_articles": article_id}}
    )
    
    return {"message": "Article saved successfully"}

@router.delete("/unsave-article/{article_id}")
async def unsave_article(
    article_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: DatabaseService = Depends(get_database_service)
):
    """Remove an article from the user's saved articles list"""
    await db.users_collection.update_one(
        {"_id": ObjectId(current_user.id)},
        {"$pull": {"saved_articles": article_id}}
    )
    
    return {"message": "Article removed from saved list"}

@router.post("/add-vocabulary")
async def add_vocabulary(
    word_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: DatabaseService = Depends(get_database_service)
):
    """Add a word to the user's vocabulary list"""
    # Check if word already in vocabulary
    user = await db.users_collection.find_one({
        "_id": ObjectId(current_user.id),
        "studied_words": word_id
    })
    
    if user:
        return {"message": "Word already in vocabulary"}
    
    # Add word to vocabulary
    await db.users_collection.update_one(
        {"_id": ObjectId(current_user.id)},
        {"$push": {"studied_words": word_id}}
    )
    
    return {"message": "Word added to vocabulary"}

@router.delete("/remove-vocabulary/{word_id}")
async def remove_vocabulary(
    word_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: DatabaseService = Depends(get_database_service)
):
    """Remove a word from the user's vocabulary list"""
    await db.users_collection.update_one(
        {"_id": ObjectId(current_user.id)},
        {"$pull": {"studied_words": word_id}}
    )
    
    return {"message": "Word removed from vocabulary"}


@router.get("/test-cleanup")
async def cleanup_test_users(
    prefix: str = Query(..., description="Email prefix to match for test users"),
    secret: str = Query(..., description="Secret key for security"),
    db: DatabaseService = Depends(get_database_service)
):
    """Delete all test users with emails starting with the specified prefix.
    This endpoint is for testing purposes only and should not be used in production.
    """
    # Simple security check - in production, use a proper authentication mechanism
    test_secret = os.environ.get("TEST_SECRET_KEY", "test_secret_key")
    if secret != test_secret:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid secret key"
        )
    
    # Delete users whose email starts with the specified prefix
    result = await db.users_collection.delete_many(
        {"email": {"$regex": f"^{prefix}"}}
    )
    
    return {
        "message": f"Deleted {result.deleted_count} test users",
        "deleted_count": result.deleted_count
    }
