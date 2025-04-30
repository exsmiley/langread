#!/usr/bin/env python
"""
Setup environment configuration file (.env) for Lingogi application.
This script creates a .env file with your OpenAI API key and other configuration.
"""
import os
import secrets
import sys

def generate_secret_key():
    """Generate a secure random secret key."""
    return secrets.token_hex(32)

def setup_env():
    """Create .env file with user's configuration."""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    
    # Check if .env already exists
    if os.path.exists(env_path):
        overwrite = input(".env file already exists. Overwrite? (y/n): ").lower().strip()
        if overwrite != 'y':
            print("Setup cancelled.")
            return
    
    # Get configuration values from user
    openai_api_key = input("Enter your OpenAI API key: ").strip()
    
    # Optional database configuration
    use_mongodb = input("Do you want to configure MongoDB? (y/n, default: n): ").lower().strip()
    if use_mongodb == 'y':
        mongodb_uri = input("Enter MongoDB URI (default: mongodb://localhost:27017/langread): ").strip()
        if not mongodb_uri:
            mongodb_uri = "mongodb://localhost:27017/langread"
    else:
        mongodb_uri = "mongodb://localhost:27017/langread"
    
    # Generate a secret key
    secret_key = generate_secret_key()
    
    # Create the .env file content
    env_content = f"""# API Keys
OPENAI_API_KEY={openai_api_key}

# Database configuration
MONGODB_URI={mongodb_uri}

# Server settings
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000

# Security
SECRET_KEY={secret_key}
TOKEN_EXPIRE_MINUTES=129600  # 3 months

# Logging
LOG_LEVEL=INFO
"""
    
    # Write the .env file
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print(f"\n.env file created successfully at {env_path}")
    print("\nIMPORTANT: Keep your .env file secure and never commit it to version control.")

if __name__ == "__main__":
    print("Lingogi Environment Setup")
    print("==========================")
    setup_env()
