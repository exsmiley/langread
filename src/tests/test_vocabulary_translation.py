import unittest
import os
import json
from unittest.mock import patch, MagicMock
import sys
import pytest
from fastapi.testclient import TestClient

# Add the project root to the Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.api.main import app, VocabularyTranslationRequest

# Create a test client
client = TestClient(app)

class TestVocabularyTranslation(unittest.TestCase):
    """Test the context-aware vocabulary translation endpoint"""
    
    def setUp(self):
        # Mock environment variables and dependencies
        self.openai_patcher = patch('openai.OpenAI')
        self.mock_openai = self.openai_patcher.start()
        
        # Set up the mock OpenAI client
        self.mock_client = MagicMock()
        self.mock_openai.return_value = self.mock_client
        
        # Mock the OpenAI response
        mock_response = MagicMock()
        mock_message = MagicMock()
        mock_message.content = json.dumps({
            "word": "테스트",
            "translation": "test",
            "part_of_speech": "noun",
            "definition": "A procedure intended to establish the quality, performance, or reliability of something.",
            "examples": ["이것은 테스트입니다."]
        })
        
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        
        self.mock_client.chat.completions.create.return_value = mock_response
        
        # Mock the API key
        os.environ["OPENAI_API_KEY"] = "test_api_key"
    
    def tearDown(self):
        self.openai_patcher.stop()
        
    def test_vocabulary_translation_with_context(self):
        """Test the vocabulary translation endpoint with context"""
        payload = {
            "text": "테스트",
            "context": "이것은 테스트입니다. 테스트는 중요합니다.",
            "source_lang": "ko",
            "target_lang": "en"
        }
        
        response = client.post("/api/vocabulary/context-aware-translate", json=payload)
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertIn("word", response.json())
        self.assertIn("translation", response.json())
        self.assertIn("part_of_speech", response.json())
        self.assertIn("definition", response.json())
        self.assertIn("examples", response.json())
        
        # Check that the OpenAI client was called with the right arguments
        call_args = self.mock_client.chat.completions.create.call_args[1]
        self.assertEqual(call_args["temperature"], 0.3)
        self.assertEqual(call_args["response_format"]["type"], "json_object")
        
        # Check that the context was included in the prompt
        messages = call_args["messages"]
        user_message = [msg for msg in messages if msg["role"] == "user"][0]
        self.assertIn("테스트", user_message["content"])
        self.assertIn("이것은 테스트입니다. 테스트는 중요합니다.", user_message["content"])
    
    def test_vocabulary_translation_without_context(self):
        """Test the vocabulary translation endpoint without context"""
        payload = {
            "text": "테스트",
            "context": "",
            "source_lang": "ko",
            "target_lang": "en"
        }
        
        response = client.post("/api/vocabulary/context-aware-translate", json=payload)
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        
        # Check that the context was not included in the prompt
        call_args = self.mock_client.chat.completions.create.call_args[1]
        messages = call_args["messages"]
        user_message = [msg for msg in messages if msg["role"] == "user"][0]
        self.assertIn("테스트", user_message["content"])
        self.assertNotIn("It appears in this context:", user_message["content"])
    
    def test_vocabulary_translation_caching(self):
        """Test that translations are cached"""
        # First request
        payload = {
            "text": "테스트",
            "context": "이것은 테스트입니다.",
            "source_lang": "ko",
            "target_lang": "en"
        }
        
        response1 = client.post("/vocabulary/context-aware-translate", json=payload)
        
        # Second request (same parameters)
        response2 = client.post("/vocabulary/context-aware-translate", json=payload)
        
        # Both responses should be successful
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        
        # The API should have been called only once
        self.assertEqual(self.mock_client.chat.completions.create.call_count, 1)
    
    def test_error_handling(self):
        """Test error handling when OpenAI API fails"""
        # Make the OpenAI API raise an exception
        self.mock_client.chat.completions.create.side_effect = Exception("API error")
        
        payload = {
            "text": "테스트",
            "context": "이것은 테스트입니다.",
            "source_lang": "ko",
            "target_lang": "en"
        }
        
        response = client.post("/api/vocabulary/context-aware-translate", json=payload)
        
        # Check the response
        self.assertEqual(response.status_code, 500)
        self.assertIn("Translation failed", response.json()["detail"])

if __name__ == "__main__":
    unittest.main()
