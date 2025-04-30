#!/usr/bin/env python
"""
Test script to verify that the .env file is properly configured 
for the Lingogi application. Also tests if the OpenAI API key works correctly.
"""
import os
import sys
from urllib.parse import urlparse
from dotenv import load_dotenv
import time

def emoji_status(status):
    """Return emoji based on status."""
    return "✅" if status else "❌"

def test_openai_api_key(api_key):
    """
    Test if the OpenAI API key is valid by making a simple API call.
    Returns a tuple of (success, message)
    """
    if not api_key:
        return False, "No OpenAI API key provided"
        
    try:
        # Dynamically import OpenAI to avoid requiring it for basic tests
        try:
            from openai import OpenAI
        except ImportError:
            return False, "OpenAI package not installed. Install with: pip install openai"
        
        # Initialize the client
        client = OpenAI(api_key=api_key)
        
        # Make a simple API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=10
        )
        
        # Check if response contains content
        if response and response.choices and len(response.choices) > 0:
            content = response.choices[0].message.content.strip()
            return True, f"API call successful. Response: '{content}'"
        else:
            return False, "API call didn't return expected content"
            
    except Exception as e:
        return False, f"API call failed: {str(e)}"


def test_env_file():
    """Test if .env file exists and contains all required variables."""
    print("Testing .env configuration...")
    print("=" * 50)
    
    # Check if .env file exists
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    env_exists = os.path.isfile(env_path)
    print(f"{emoji_status(env_exists)} .env file exists: {env_exists}")
    
    if not env_exists:
        print("\n❌ ERROR: .env file not found!")
        print("Please run setup_env.py to create your .env file.")
        return False
    
    # Load environment variables from .env
    load_dotenv(env_path)
    
    # Required variables to check
    required_vars = {
        "OPENAI_API_KEY": {
            "validator": lambda x: x and len(x) > 20,  # Simple length check
            "message": "OpenAI API key is present and has valid length"
        },
        "MONGODB_URI": {
            "validator": lambda x: x and urlparse(x).scheme and urlparse(x).netloc,
            "message": "MongoDB URI is present and has valid format"
        },
        "API_HOST": {
            "validator": lambda x: x and len(x) > 0,
            "message": "API host is configured"
        },
        "API_PORT": {
            "validator": lambda x: x and x.isdigit() and 1 <= int(x) <= 65535,
            "message": "API port is valid (1-65535)"
        },
        "SECRET_KEY": {
            "validator": lambda x: x and len(x) >= 32,
            "message": "Secret key is present and has sufficient length"
        },
        "TOKEN_EXPIRE_MINUTES": {
            "validator": lambda x: x and x.isdigit(),
            "message": "Token expiration is configured correctly"
        }
    }
    
    # Test each required variable
    all_passed = True
    for var_name, var_props in required_vars.items():
        var_value = os.getenv(var_name)
        
        # Don't print actual values for sensitive data
        is_sensitive = var_name in ["OPENAI_API_KEY", "SECRET_KEY"]
        display_value = "[HIDDEN]" if is_sensitive and var_value else var_value
        
        is_valid = var_props["validator"](var_value) if var_value else False
        
        # Print status
        print(f"{emoji_status(is_valid)} {var_props['message']}")
        
        if not is_valid:
            all_passed = False
    
    # Summary of basic configuration tests
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ SUCCESS: All environment variables are properly configured!")
    else:
        print("❌ WARNING: Some environment variables are missing or misconfigured.")
        print("Please check the issues above and update your .env file.")
        return False
    
    # Test if OpenAI API key actually works
    print("\nTesting OpenAI API key functionality...")
    print("=" * 50)
    print("Making a test API call to OpenAI...")    
    
    # Add a small delay to separate the outputs visually
    time.sleep(1)
    
    # Get the API key
    api_key = os.getenv("OPENAI_API_KEY")
    success, message = test_openai_api_key(api_key)
    
    print(f"{emoji_status(success)} OpenAI API key is functioning: {success}")
    if success:
        print(f"  Details: {message}")
    else:
        print(f"  Error: {message}")
        all_passed = False
    
    # Final summary
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ SUCCESS: All environment variables are properly configured and the OpenAI API key is working!")
        print("You're ready to run the Lingogi application.")
    else:
        print("❌ WARNING: There are issues with your configuration.")
        print("Please check the errors above and update your settings.")
    
    return all_passed

if __name__ == "__main__":
    test_env_file()
