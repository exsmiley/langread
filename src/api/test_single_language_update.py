#!/usr/bin/env python3
"""
Simple test script to verify that additional languages can be saved in the user profile.
This script:
1. Creates a test user
2. Authenticates the user
3. Updates the user profile with additional languages
4. Verifies the languages were saved correctly
"""

import requests
import json
import uuid
import time
import os
from typing import Dict, List, Optional, Any

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER_PREFIX = "test_user_"
TEST_PASSWORD = "test_password"

def print_colored(text, color="green"):
    """Print colored text to the console"""
    colors = {
        "black": "\033[30m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "purple": "\033[95m",
        "reset": "\033[0m"
    }
    
    print(f"{colors.get(color, colors['reset'])}{text}{colors['reset']}")


def create_test_user():
    """Create a test user and return the user credentials"""
    unique_id = str(uuid.uuid4())[:8]
    name = f"Test User {unique_id}"
    email = f"{TEST_USER_PREFIX}{unique_id}@example.com"
    password = TEST_PASSWORD
    
    print_colored(f"\nCreating test user: {email}", "blue")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/signup",
            json={
                "email": email,
                "password": password,
                "name": name,
                "native_language": "en",
                "learning_language": "ko"
            }
        )
        
        if response.status_code not in [200, 201]:
            print_colored(f"Failed to create test user (status code {response.status_code}): {response.text}", "red")
            return None
        
        # Check the response payload - the API returns success in the JSON body
        data = response.json()
        if data.get("success"):
            print_colored(f"Test user created successfully: {email} (user_id: {data.get('user_id', 'unknown')})", "green")
            return {"email": email, "password": password, "name": name, "user_id": data.get('user_id')}
        else:
            print_colored(f"Failed to create test user: {data}", "red")
            return None
    except Exception as e:
        print_colored(f"Error creating test user: {str(e)}", "red")
        return None


def authenticate(email, password):
    """Authenticate with the API and return the token"""
    print_colored(f"Authenticating {email}...", "blue")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/signin",
            json={
                "email": email,
                "password": password
            }
        )
        
        if response.status_code != 200:
            print_colored(f"Authentication failed (status code {response.status_code}): {response.text}", "red")
            return None
        
        data = response.json()
        token = data.get("token")
        if token:
            print_colored("Authentication successful", "green")
            return token
        else:
            print_colored(f"Authentication failed: No token in response: {data}", "red")
            return None
    except Exception as e:
        print_colored(f"Error during authentication: {str(e)}", "red")
        return None


def get_profile(token):
    """Get the current user profile"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/user/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code != 200:
            print_colored(f"Failed to get profile (status code {response.status_code}): {response.text}", "red")
            return None
        
        return response.json()
    except Exception as e:
        print_colored(f"Error getting profile: {str(e)}", "red")
        return None


def update_profile(token, update_data):
    """Update the user profile and return the updated profile"""
    print_colored(f"\nUpdating profile with data:", "blue")
    print(json.dumps(update_data, indent=2))
    
    try:
        response = requests.put(
            f"{BASE_URL}/api/user/profile",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            json=update_data
        )
        
        if response.status_code != 200:
            print_colored(f"Failed to update profile (status code {response.status_code}): {response.text}", "red")
            return None
        
        return response.json()
    except Exception as e:
        print_colored(f"Error updating profile: {str(e)}", "red")
        return None


def delete_test_user(user_id):
    """Delete a test user by ID"""
    print_colored(f"\nDeleting test user (ID: {user_id})...", "blue")
    try:
        response = requests.get(
            f"{BASE_URL}/api/user/test-cleanup",
            params={"prefix": TEST_USER_PREFIX, "secret": "test_secret_key"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("deleted_count", 0) > 0:
                print_colored(f"Deleted {data.get('deleted_count')} test users", "green")
            else:
                print_colored("No test users found to delete", "yellow")
        else:
            print_colored(f"Failed to delete test users: {response.text}", "red")
    except Exception as e:
        print_colored(f"Error deleting test users: {str(e)}", "red")


def main():
    print_colored("\n===== LINGOGI ADDITIONAL LANGUAGES TEST =====", "purple")
    print_colored("Testing if additional languages can be saved to a user profile\n", "purple")
    
    # Create a test user
    user = create_test_user()
    if not user:
        print_colored("Failed to create test user. Aborting.", "red")
        return
    
    # Sleep briefly to ensure user is fully created
    time.sleep(1)
    
    # Authenticate
    token = authenticate(user["email"], user["password"])
    if not token:
        print_colored("Failed to authenticate. Aborting.", "red")
        delete_test_user(user.get("user_id"))
        return
    
    # Get original profile
    original_profile = get_profile(token)
    if not original_profile:
        print_colored("Failed to get original profile. Aborting.", "red")
        delete_test_user(user.get("user_id"))
        return
    
    print_colored("\nOriginal profile:", "yellow")
    print(json.dumps(original_profile, indent=2))
    
    # Update profile with additional languages
    update_data = {
        "name": user["name"],
        "additional_languages": [
            {"language": "ja", "proficiency": "beginner", "isDefault": False},
            {"language": "es", "proficiency": "intermediate", "isDefault": False}
        ]
    }
    
    updated_profile = update_profile(token, update_data)
    if not updated_profile:
        print_colored("Failed to update profile. Aborting.", "red")
        delete_test_user(user.get("user_id"))
        return
    
    print_colored("\nUpdated profile:", "yellow")
    print(json.dumps(updated_profile, indent=2))
    
    # Verify additional languages were saved
    if "additional_languages" not in updated_profile or not updated_profile["additional_languages"]:
        print_colored("\nTest FAILED: additional_languages field is empty or missing!", "red")
    elif len(updated_profile["additional_languages"]) != 2:
        print_colored(f"\nTest FAILED: Expected 2 additional languages, but found {len(updated_profile['additional_languages'])}", "red")
    else:
        print_colored("\nTest PASSED: Additional languages were saved successfully!", "green")
        print_colored("Found languages:", "green")
        for lang in updated_profile["additional_languages"]:
            print(f"  - {lang['language']} ({lang['proficiency']})")
    
    # Clean up test user
    delete_test_user(user.get("user_id"))
    
    print_colored("\n===== TEST COMPLETED =====", "purple")


if __name__ == "__main__":
    main()
