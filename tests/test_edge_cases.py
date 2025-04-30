import unittest
import requests
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base URL for API
BASE_URL = "http://127.0.0.1:8000"

class TestEdgeCases(unittest.TestCase):
    
    def setUp(self):
        """Set up test case with common variables"""
        # Check if the server is running
        try:
            response = requests.get(f"{BASE_URL}/docs")
            if response.status_code != 200:
                self.skipTest("API server is not running. Start the server with 'uvicorn app.main:app --reload'")
        except requests.exceptions.ConnectionError:
            self.skipTest("API server is not running. Start the server with 'uvicorn app.main:app --reload'")
    
    def test_empty_user_prompt(self):
        """Test with empty user prompt"""
        payload = {
            "user_id": "test_user",
            "user_type": "guest",
            "chat_mode": "general",
            "feature": "test_feature",
            "last_messages": ["Hello"],
            "user_prompt": ""  # Empty prompt
        }
        
        response = requests.post(
            f"{BASE_URL}/chat/generate",
            json=payload
        )
        
        self.assertEqual(response.status_code, 422)  # Validation error expected
        print("\nEmpty User Prompt: Validation error as expected")
    
    def test_long_user_prompt(self):
        """Test with a very long user prompt"""
        # Generate a long prompt (5000 characters)
        long_prompt = "This is a long prompt. " * 250
        
        payload = {
            "user_id": "test_user",
            "user_type": "paid",
            "chat_mode": "general",
            "feature": "test_feature",
            "last_messages": ["Hello"],
            "user_prompt": long_prompt
        }
        
        response = requests.post(
            f"{BASE_URL}/chat/generate",
            json=payload
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("response", data)
        self.assertTrue(len(data["response"]) > 0)
        print(f"\nLong User Prompt: Response received successfully with {len(data['response'])} characters")
    
    def test_special_characters(self):
        """Test with special characters in the prompt"""
        payload = {
            "user_id": "test_user",
            "user_type": "guest",
            "chat_mode": "general",
            "feature": "test_feature",
            "last_messages": ["Hello"],
            "user_prompt": "Tell me about programming in C++ with special chars: !@#$%^&*()_+{}|:\"<>?~`-=[]\\;',./"
        }
        
        response = requests.post(
            f"{BASE_URL}/chat/generate",
            json=payload
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("response", data)
        self.assertTrue(len(data["response"]) > 0)
        print(f"\nSpecial Characters: Response received successfully")
    
    def test_missing_user_id(self):
        """Test with missing user_id"""
        payload = {
            # Missing user_id
            "user_type": "guest",
            "chat_mode": "general",
            "feature": "test_feature",
            "last_messages": ["Hello"],
            "user_prompt": "Tell me a joke."
        }
        
        response = requests.post(
            f"{BASE_URL}/chat/generate",
            json=payload
        )
        
        self.assertEqual(response.status_code, 422)  # Validation error expected
        print("\nMissing User ID: Validation error as expected")
    
    def test_missing_feature(self):
        """Test with missing feature"""
        payload = {
            "user_id": "test_user",
            "user_type": "guest",
            "chat_mode": "general",
            # Missing feature
            "last_messages": ["Hello"],
            "user_prompt": "Tell me a joke."
        }
        
        response = requests.post(
            f"{BASE_URL}/chat/generate",
            json=payload
        )
        
        self.assertEqual(response.status_code, 422)  # Validation error expected
        print("\nMissing Feature: Validation error as expected")
    
    def test_empty_last_messages(self):
        """Test with empty last_messages list"""
        payload = {
            "user_id": "test_user",
            "user_type": "guest",
            "chat_mode": "general",
            "feature": "test_feature",
            "last_messages": [],  # Empty list
            "user_prompt": "Tell me a joke."
        }
        
        response = requests.post(
            f"{BASE_URL}/chat/generate",
            json=payload
        )
        
        self.assertEqual(response.status_code, 200)  # Should still work
        data = response.json()
        self.assertIn("response", data)
        self.assertTrue(len(data["response"]) > 0)
        print(f"\nEmpty Last Messages: Response received successfully")
    
    def test_concurrent_requests(self):
        """Test multiple concurrent requests"""
        payload = {
            "user_id": "test_user",
            "user_type": "guest",
            "chat_mode": "general",
            "feature": "test_feature",
            "last_messages": ["Hello"],
            "user_prompt": "Tell me a short joke."
        }
        
        # Send 3 concurrent requests
        import threading
        results = [None] * 3
        
        def make_request(index):
            response = requests.post(
                f"{BASE_URL}/chat/generate",
                json=payload
            )
            results[index] = response.status_code
        
        threads = []
        for i in range(3):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        self.assertTrue(all(status == 200 for status in results))
        print(f"\nConcurrent Requests: All {len(results)} requests completed successfully")

if __name__ == "__main__":
    unittest.main()
