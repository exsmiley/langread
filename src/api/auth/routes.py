from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Annotated, List
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from src.api.models.user import (
    UserCreate,
    UserBase,
    UserInDB,
    UserResponse
)

# Define additional models needed for auth
class UserSignIn(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    token: str
    token_type: str
    
class TokenData(BaseModel):
    user_id: str
    
# We're importing UserResponse from models.user, so this one is not needed anymore
# The model should be consistent across the application

from src.api.models.password_reset import (
    PasswordResetRequest,
    PasswordResetConfirm
)
from src.api.auth.utils import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_token,
    create_password_reset_token,
    verify_password_reset_token,
    oauth2_scheme
)
from src.api.models.user import UserResponse, TokenData
from src.models.database import DatabaseService
from src.api.db_helpers import get_database_service

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/forgot-password")
async def request_password_reset(request: PasswordResetRequest, db: DatabaseService = Depends(get_database_service)):
    """Request a password reset link"""
    # Always return success to avoid email enumeration attacks
    # In a real system, you would send an email with the reset link
    
    # Check if user exists
    user = await db.users_collection.find_one({"email": request.email})
    if not user:
        # Return success even if user doesn't exist (security best practice)
        return {"success": True, "message": "If your email is registered, you will receive a password reset link"}
    
    # Generate a reset token
    token = create_password_reset_token(request.email)
    
    # In a real implementation, send an email with a link containing this token
    # For now, just return the token in the response (for testing only)
    reset_link = f"http://localhost:5173/reset-password?token={token}"
    
    print(f"Password reset requested for {request.email}")
    print(f"Reset link: {reset_link}")
    
    return {
        "success": True,
        "message": "If your email is registered, you will receive a password reset link",
        # In production, you wouldn't return these, they're just for testing
        "debug_token": token,
        "debug_link": reset_link
    }

@router.post("/reset-password")
async def reset_password(request: PasswordResetConfirm, db: DatabaseService = Depends(get_database_service)):
    """Reset a password using a valid reset token"""
    # Verify the token
    email = verify_password_reset_token(request.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
    
    # Find the user
    user = await db.users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Hash the new password
    hashed_password = get_password_hash(request.new_password)
    
    # Update the user's password
    result = await db.users_collection.update_one(
        {"email": email},
        {"$set": {"hashed_password": hashed_password}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update password"
        )
    
    return {"success": True, "message": "Password has been reset successfully"}

@router.get("/check-email/{email}")
async def check_email(email: str, db: DatabaseService = Depends(get_database_service)):
    """Check if an email is already registered"""
    try:
        # Ensure users collection exists
        if not hasattr(db, 'users_collection') or db.users_collection is None:
            if hasattr(db, 'db') and db.db is not None:
                db.users_collection = db.db.users
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database not initialized properly"
                )
                
        # Check if user exists
        existing_user = await db.users_collection.find_one({"email": email})
        return {"exists": existing_user is not None}
    except Exception as e:
        print(f"Error checking email existence: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    db: DatabaseService = Depends(get_database_service)
):
    """Register a new user"""
    try:
        # Ensure users collection exists
        if not hasattr(db, 'users_collection') or db.users_collection is None:
            if hasattr(db, 'db') and db.db is not None:
                db.users_collection = db.db.users
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database not initialized properly"
                )
        
        # Log the request for debugging
        print(f"Signup request received for: {user_data.email}")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database initialization error: {str(e)}"
        )
    
    # Check if user already exists
    existing_user = await db.users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user with hashed password
    hashed_password = get_password_hash(user_data.password)
    user_dict = user_data.model_dump()
    del user_dict["password"]
    
    # Add additional fields
    user_dict["hashed_password"] = hashed_password
    user_dict["created_at"] = datetime.utcnow()
    user_dict["saved_articles"] = []
    user_dict["studied_words"] = []
    
    # Insert into database
    try:
        result = await db.users_collection.insert_one(user_dict)
        return {"success": True, "message": "User created successfully", "user_id": str(result.inserted_id)}
    except Exception as e:
        print(f"Database insertion error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    except:
        print("Unknown error during database insertion")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unknown error occurred during account creation"
        )
    finally:
        print(f"Signup process completed for: {user_data.email}")

class SignInRequest(BaseModel):
    """Model for sign-in request"""
    email: str
    password: str

@router.post("/signin")
async def signin(
    form_data: SignInRequest,
    db: DatabaseService = Depends(get_database_service)
):
    """Authenticate a user and return a token"""
    # Find user by email
    user = await db.users_collection.find_one({"email": form_data.email})
    
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    token_data = {"sub": str(user["_id"])}
    token = create_access_token(token_data)
    
    return {"token": token, "token_type": "bearer"}

# Helper function to get the current user from token
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DatabaseService = Depends(get_database_service)
) -> UserResponse:
    """Get the current user from the token"""
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        token_data = TokenData(user_id=user_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await db.users_collection.find_one({"_id": ObjectId(token_data.user_id)})
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Convert MongoDB document to a format compatible with UserResponse
    user_dict = {
        "email": user["email"],
        "name": user["name"],
        "native_language": user.get("native_language", "en"),
        "learning_language": user.get("learning_language", "ko"),
        "proficiency": user.get("proficiency", "intermediate"),
        "id": str(user["_id"]),
        "created_at": user.get("created_at", datetime.utcnow()),
        "saved_articles": user.get("saved_articles", []),
        "studied_words": user.get("studied_words", []),
        "additional_languages": user.get("additional_languages", [])
    }
    
    return UserResponse(**user_dict)
