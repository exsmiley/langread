"""
Routes for tag management.
"""
from fastapi import APIRouter, Depends, Query, Body, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

# Add the project root to the Python path for imports
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.models.database import DatabaseService

# Dependency to get the database service
async def get_database_service():
    db = DatabaseService()
    await db.connect()
    try:
        yield db
    finally:
        await db.disconnect()

router = APIRouter(prefix="/tags", tags=["tags"])

class TagCreate(BaseModel):
    """Model for creating a tag"""
    name: str
    language: str
    active: bool = False
    
class TagUpdate(BaseModel):
    """Model for updating a tag"""
    name: Optional[str] = None
    language: Optional[str] = None
    active: Optional[bool] = None

@router.get("/")
async def get_tags(
    language: Optional[str] = None,
    active_only: bool = False,
    name_contains: Optional[str] = None,
    limit: int = 100,
    skip: int = 0,
    db: DatabaseService = Depends(get_database_service)
):
    """
    Get a list of tags with optional filtering.
    """
    # Parameter name in db.get_tags is 'query' not 'name_contains'
    tags = await db.get_tags(
        language=language,
        active_only=active_only,
        query=name_contains
    )
    
    # Convert ObjectId to string for JSON serialization
    serialized_tags = []
    for tag in tags:
        tag_copy = dict(tag)
        if '_id' in tag_copy and not isinstance(tag_copy['_id'], str):
            tag_copy['_id'] = str(tag_copy['_id'])
        serialized_tags.append(tag_copy)
        
    return {"tags": serialized_tags, "count": len(serialized_tags)}

@router.get("/stats")
async def get_tag_stats(db: DatabaseService = Depends(get_database_service)):
    """
    Get tag usage statistics.
    """
    stats = await db.get_tag_stats()
    return stats

@router.get("/{tag_id}")
async def get_tag(tag_id: str, db: DatabaseService = Depends(get_database_service)):
    """
    Get a specific tag by ID.
    """
    tag = await db.get_tag(tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag

@router.post("/")
async def create_tag(tag: TagCreate, db: DatabaseService = Depends(get_database_service)):
    """
    Create a new tag.
    """
    tag_data = tag.model_dump()
    tag_data["created_at"] = datetime.now()
    tag_data["updated_at"] = tag_data["created_at"]
    tag_data["article_count"] = 0
    
    try:
        tag_id = await db.save_tag(tag_data)
        return {"id": tag_id, "message": "Tag created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating tag: {str(e)}")

@router.patch("/{tag_id}")
async def update_tag(
    tag_id: str,
    tag_update: TagUpdate,
    db: DatabaseService = Depends(get_database_service)
):
    """
    Update a tag.
    """
    # Get the existing tag
    existing_tag = await db.get_tag(tag_id)
    if not existing_tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    # Update only the specified fields
    update_data = {k: v for k, v in tag_update.model_dump().items() if v is not None}
    if not update_data:
        return {"message": "No changes to update"}
    
    update_data["updated_at"] = datetime.now()
    
    # Create a merged dictionary of existing and updated data
    tag_data = {**existing_tag, **update_data}
    
    try:
        await db.save_tag(tag_data)
        return {"id": tag_id, "message": "Tag updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating tag: {str(e)}")

@router.delete("/{tag_id}")
async def delete_tag(tag_id: str, db: DatabaseService = Depends(get_database_service)):
    """
    Delete a tag.
    """
    success = await db.delete_tag(tag_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tag not found or could not be deleted")
    return {"message": "Tag deleted successfully"}

@router.post("/{tag_id}/activate")
async def activate_tag(tag_id: str, db: DatabaseService = Depends(get_database_service)):
    """
    Activate a tag (approve it for use).
    """
    success = await db.activate_tag(tag_id, True)
    if not success:
        raise HTTPException(status_code=404, detail="Tag not found or could not be activated")
    return {"message": "Tag activated successfully"}

@router.post("/{tag_id}/deactivate")
async def deactivate_tag(tag_id: str, db: DatabaseService = Depends(get_database_service)):
    """
    Deactivate a tag.
    """
    success = await db.activate_tag(tag_id, False)
    if not success:
        raise HTTPException(status_code=404, detail="Tag not found or could not be deactivated")
    return {"message": "Tag deactivated successfully"}

@router.get("/article/{article_id}")
async def get_article_tags(
    article_id: str,
    db: DatabaseService = Depends(get_database_service)
):
    """
    Get tags for a specific article.
    """
    article = await db.get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return {
        "article_id": article_id,
        "tags": article.get("tags", []),
        "auto_generated_tags": article.get("auto_generated_tags", [])
    }

@router.put("/article/{article_id}")
async def update_article_tags(
    article_id: str,
    tags: List[str] = Body(...),
    db: DatabaseService = Depends(get_database_service)
):
    """
    Update tags for a specific article.
    """
    # Verify article exists
    article = await db.get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    success = await db.update_article_tags(article_id, tags)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update article tags")
    
    return {"message": "Article tags updated successfully"}
