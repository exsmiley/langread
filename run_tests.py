#!/usr/bin/env python
"""
Test runner script for LangRead application.
Run this script to execute unit and integration tests.
"""
import os
import sys
import subprocess
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import pytest
        import motor
        import pymongo
        import openai
        print("✅ All required testing dependencies are installed.")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install required dependencies: pip install -r requirements.txt")
        return False

def check_environment():
    """Check if required environment variables are set."""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    mongodb_uri = os.getenv("MONGODB_URI") or os.getenv("TEST_MONGODB_URI")
    
    if not openai_api_key:
        print("⚠️  Warning: OPENAI_API_KEY environment variable is not set.")
        print("Some tests that require OpenAI API will be skipped.")
    else:
        print("✅ OpenAI API key is configured.")
        
    if not mongodb_uri:
        print("⚠️  Warning: MONGODB_URI environment variable is not set.")
        print("Some tests that require MongoDB will be skipped.")
    else:
        print("✅ MongoDB connection is configured.")
    
    return True

def run_tests(args):
    """Run pytest with the specified arguments."""
    test_args = ["pytest"]
    
    # Add verbosity
    test_args.append("-v")
    
    # Add test type
    if args.unit_only:
        test_args.extend(["-m", "unit"])
    elif args.integration_only:
        test_args.extend(["-m", "integration"])
    
    # Add specific test path if provided
    if args.test_path:
        test_args.append(args.test_path)
    
    # Add coverage if requested
    if args.coverage:
        test_args.extend(["--cov=src", "--cov-report=term", "--cov-report=html"])
    
    # Add markers to skip expensive tests
    if args.skip_slow:
        test_args.extend(["-m", "not slow"])
    
    # Print test command
    print(f"Running: {' '.join(test_args)}")
    
    # Run tests
    result = subprocess.run(test_args)
    return result.returncode

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run tests for LangRead application.")
    parser.add_argument("--unit-only", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration-only", action="store_true", help="Run only integration tests")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--skip-slow", action="store_true", help="Skip slow tests (e.g., API calls)")
    parser.add_argument("test_path", nargs="?", help="Specific test path to run")
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("LangRead Test Runner")
    print("=" * 80)
    
    # Check dependencies and environment
    if not check_dependencies() or not check_environment():
        sys.exit(1)
    
    print("\nRunning tests...")
    print("-" * 80)
    
    # Run tests
    exit_code = run_tests(args)
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed.")
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
