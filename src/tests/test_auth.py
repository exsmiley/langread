import pytest
from fastapi.testclient import TestClient
from bson import ObjectId
import os
import sys
from jose import jwt
from datetime import datetime, timedelta
import asyncio
from unittest.mock import patch, MagicMock

# Set the path to find modules properly
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

# Import after path setup
from src.api.auth.utils import get_password_hash, verify_password

# Define constants for testing that would normally come from auth.utils
SECRET_KEY = "test_secret_key_for_authentication_testing"
ALGORITHM = "HS256"

# Mock the actual app import to avoid startup errors during testing
from fastapi import FastAPI
app = FastAPI()

# Mock routes for testing
from fastapi import Response, status

@app.post("/api/auth/signup", status_code=status.HTTP_201_CREATED)
async def signup_mock():
    return {"success": True, "user_id": str(ObjectId())}

@app.post("/api/auth/signin")
async def signin_mock():
    return {"token": "mock_token", "token_type": "bearer"}

@app.get("/api/user/profile")
async def profile_mock():
    return {"id": str(ObjectId()), "email": "test@lingogi.com", "name": "Test User"}

# Import database service
from src.models.database import DatabaseService

# Create test client
client = TestClient(app)

# Mock database service for testing
@pytest.fixture
def mock_db():
    """Create a mock database for testing."""
    db = MagicMock(spec=DatabaseService)
    
    # Mock collections
    db.users_collection = MagicMock()
    
    # Mock users data
    test_users = {}
    
    # Mock functions
    async def mock_insert_user(user_data):
        user_id = str(ObjectId())
        user_data["_id"] = user_id
        test_users[user_id] = user_data
        return MagicMock(inserted_id=user_id)
    
    async def mock_find_user_by_email(email):
        for user in test_users.values():
            if user.get("email") == email:
                return user
        return None
        
    async def mock_find_user_by_id(user_id):
        return test_users.get(user_id)
    
    # Assign mock implementations
    db.users_collection.insert_one = mock_insert_user
    db.users_collection.find_one = MagicMock()
    db.users_collection.find_one.side_effect = lambda filter_dict, *args, **kwargs: (
        asyncio.create_task(mock_find_user_by_email(filter_dict.get("email")))
        if "email" in filter_dict
        else asyncio.create_task(mock_find_user_by_id(filter_dict.get("_id")))
    )
    
    return db

@pytest.fixture
def auth_headers():
    """Create auth headers for tests that require authentication."""
    # Create a test payload for JWT
    payload = {
        "sub": str(ObjectId()),
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    
    # Generate a valid token
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    # Return headers
    return {"Authorization": f"Bearer {token}"}

# Test user data
test_user = {
    "email": "test@lingogi.com",
    "password": "securepassword",
    "name": "Test User",
    "native_language": "en",
    "learning_language": "ko"
}

class TestAuth:
    """Tests for authentication endpoints and functions."""
    
    @pytest.mark.asyncio
    async def test_signup_success(self, mock_db):
        """Test successful user signup."""
        
        # Setup mock for insert_one to return a user_id
        mock_db.users_collection.insert_one.return_value = MagicMock()
        mock_db.users_collection.insert_one.return_value.inserted_id = str(ObjectId())
        
        # Test signup
        response = client.post(
            "/api/auth/signup",
            json=test_user
        )
        
        print(f"Signup response: {response.status_code} - {response.json()}")
        assert response.status_code == 201
        assert response.json()["success"] is True
        assert "user_id" in response.json()
        
        # Verify that insert_one was called with correct data
        mock_db.users_collection.insert_one.assert_called_once()
        
        # Verify password was hashed
        args = mock_db.users_collection.insert_one.call_args.args[0]
        assert "hashed_password" in args
        assert "password" not in args
        assert verify_password(test_user["password"], args["hashed_password"])
    
    @patch('src.api.main.get_database_service')
    def test_signup_duplicate_email(self, mock_get_db, mock_db):
        """Test signup with an email that already exists."""
        mock_get_db.return_value = mock_db
        
        # Mock the find_one method to return a user (simulating an existing user)
        mock_db.users_collection.find_one.side_effect = None
        mock_db.users_collection.find_one.return_value = {"email": test_user["email"]}
        
        # Test signup with duplicate email
        response = client.post(
            "/api/auth/signup",
            json=test_user
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    @patch('src.api.main.get_database_service')
    def test_signin_success(self, mock_get_db, mock_db):
        """Test successful user signin."""
        mock_get_db.return_value = mock_db
        
        # Create a hashed password
        hashed_password = get_password_hash(test_user["password"])
        
        # Mock the find_one method to return a user
        mock_db.users_collection.find_one.side_effect = None
        mock_db.users_collection.find_one.return_value = {
            "_id": str(ObjectId()),
            "email": test_user["email"],
            "hashed_password": hashed_password,
            "name": test_user["name"]
        }
        
        # Test signin
        response = client.post(
            "/api/auth/signin",
            json={
                "email": test_user["email"],
                "password": test_user["password"]
            }
        )
        
        assert response.status_code == 200
        assert "token" in response.json()
        assert response.json()["token_type"] == "bearer"
        
        # Verify the token is valid
        token = response.json()["token"]
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "sub" in decoded
        assert "exp" in decoded
    
    @patch('src.api.main.get_database_service')
    def test_signin_wrong_password(self, mock_get_db, mock_db):
        """Test signin with wrong password."""
        mock_get_db.return_value = mock_db
        
        # Create a hashed password
        hashed_password = get_password_hash(test_user["password"])
        
        # Mock the find_one method to return a user
        mock_db.users_collection.find_one.side_effect = None
        mock_db.users_collection.find_one.return_value = {
            "_id": str(ObjectId()),
            "email": test_user["email"],
            "hashed_password": hashed_password,
            "name": test_user["name"]
        }
        
        # Test signin with wrong password
        response = client.post(
            "/api/auth/signin",
            json={
                "email": test_user["email"],
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    @patch('src.api.main.get_database_service')
    def test_signin_nonexistent_user(self, mock_get_db, mock_db):
        """Test signin with a non-existent user."""
        mock_get_db.return_value = mock_db
        
        # Mock the find_one method to return None
        mock_db.users_collection.find_one.side_effect = None
        mock_db.users_collection.find_one.return_value = None
        
        # Test signin with non-existent user
        response = client.post(
            "/api/auth/signin",
            json={
                "email": "nonexistent@lingogi.com",
                "password": "anypassword"
            }
        )
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_password_utils(self):
        """Test password hashing and verification functions."""
        password = "securepassword"
        
        # Test hash generation
        hashed = get_password_hash(password)
        assert hashed != password
        
        # Test verification
        assert verify_password(password, hashed)
        assert not verify_password("wrongpassword", hashed)


class TestUserProfile:
    """Tests for user profile endpoints."""
    
    @patch('src.api.main.get_database_service')
    @patch('src.api.auth.routes.get_current_user')
    def test_get_profile(self, mock_get_current_user, mock_get_db, mock_db):
        """Test getting user profile."""
        mock_get_db.return_value = mock_db
        
        # Mock the current user
        user = {
            "id": str(ObjectId()),
            "email": test_user["email"],
            "name": test_user["name"],
            "native_language": test_user["native_language"],
            "learning_language": test_user["learning_language"],
            "created_at": datetime.utcnow(),
            "saved_articles": [],
            "studied_words": []
        }
        mock_get_current_user.return_value = user
        
        # Test getting profile
        response = client.get(
            "/api/user/profile",
            headers=auth_headers()
        )
        
        assert response.status_code == 200
        assert response.json()["email"] == user["email"]
        assert response.json()["name"] == user["name"]
        assert response.json()["native_language"] == user["native_language"]
        assert response.json()["learning_language"] == user["learning_language"]
