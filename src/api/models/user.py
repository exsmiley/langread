from datetime import datetime
from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class LearningLanguage(BaseModel):
    """Model for a language the user is learning"""
    language: str
    proficiency: str = "intermediate"  # beginner, intermediate, advanced
    isDefault: Optional[bool] = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "language": "ko",
                "proficiency": "intermediate",
                "isDefault": True
            }
        }

class UserBase(BaseModel):
    """Base model for user data"""
    email: EmailStr
    name: str
    native_language: str = "en"
    learning_language: str = "ko"  # Primary learning language (for backward compatibility)
    proficiency: Optional[str] = "intermediate"
    additional_languages: List[LearningLanguage] = []  # Additional languages user is learning

class UserCreate(UserBase):
    """Model for creating a new user"""
    password: str

class UserUpdate(BaseModel):
    """Model for updating user information"""
    name: Optional[str] = None
    native_language: Optional[str] = None
    learning_language: Optional[str] = None
    proficiency: Optional[str] = None
    additional_languages: Optional[List[LearningLanguage]] = []  # Default to empty list instead of None

class UserInDB(UserBase):
    """Model for user information stored in the database"""
    id: str = Field(..., alias="_id")
    hashed_password: str
    created_at: datetime
    saved_articles: List[str] = []
    studied_words: List[str] = []
    additional_languages: List[LearningLanguage] = []

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserResponse(UserBase):
    """Model for user information returned to the client"""
    id: str
    created_at: datetime
    saved_articles: List[str] = []
    studied_words: List[str] = []
    additional_languages: List[LearningLanguage] = []
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class Token(BaseModel):
    """Model for JWT token"""
    token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Data contained in JWT token"""
    user_id: str
