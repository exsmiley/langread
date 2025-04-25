"""
Common test fixtures and configuration for pytest.
"""
import pytest
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up test MongoDB URI
os.environ["TEST_MONGODB_URI"] = os.getenv("TEST_MONGODB_URI", "mongodb://localhost:27017/langread_test")

# Configure pytest to handle event loop for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Skip tests that require OpenAI API key if not available
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "openai: mark test as requiring OpenAI API key")
    config.addinivalue_line("markers", "mongodb: mark test as requiring MongoDB connection")

def pytest_runtest_setup(item):
    """Skip tests that require API keys or database connections if not available."""
    # Skip tests that require OpenAI API key
    openai_marks = [mark for mark in item.iter_markers(name="openai")]
    if openai_marks and not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OpenAI API key not available")
    
    # Skip tests that require MongoDB
    mongodb_marks = [mark for mark in item.iter_markers(name="mongodb")]
    if mongodb_marks and not os.getenv("TEST_MONGODB_URI"):
        pytest.skip("MongoDB connection string not available")
