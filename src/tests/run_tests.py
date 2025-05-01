#!/usr/bin/env python3
"""
Test runner for Lingogi authentication tests

This script runs the auth and database tests to verify that the authentication
system is working correctly.
"""

import os
import sys
import pytest
import subprocess

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        "pytest",
        "pytest-asyncio",
        "fastapi",
        "httpx",  # For TestClient
        "motor",
        "pymongo",
        "python-jose[cryptography]",
        "passlib[bcrypt]"
    ]
    
    print("Checking for required dependencies...")
    missing = []
    
    for package in required_packages:
        try:
            name = package.split('[')[0]  # Extract base package name
            __import__(name)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Missing packages: {', '.join(missing)}")
        install = input("Install missing packages? (y/n): ")
        if install.lower() == 'y':
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
        else:
            print("Tests may fail without the required dependencies.")
    else:
        print("All required dependencies are installed.")

def run_tests():
    """Run the authentication and database tests"""
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create __init__.py if it doesn't exist to make the tests directory a package
    init_file = os.path.join(test_dir, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            f.write("# Tests package\n")
    
    print("\n=== Running Authentication Tests ===\n")
    auth_result = pytest.main(["-xvs", os.path.join(test_dir, "test_auth.py")])
    
    print("\n=== Running User Database Tests ===\n")
    db_result = pytest.main(["-xvs", os.path.join(test_dir, "test_user_db.py")])
    
    return auth_result == 0 and db_result == 0

if __name__ == "__main__":
    check_dependencies()
    success = run_tests()
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1)
