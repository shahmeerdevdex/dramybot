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

class TestOpenRouterChat(unittest.TestCase):
    
    def setUp(self):
        """Set up test case with common variables"""
        # Check if the server is running
        try:
            response = requests.get(f"{BASE_URL}/docs")
            if response.status_code != 200:
                self.skipTest("API server is not running. Start the server with 'uvicorn app.main:app --reload'")
        except requests.exceptions.ConnectionError:
            self.skipTest("API server is not running. Start the server with 'uvicorn app.main:app --reload'")
    
    def test_guest_general_chat_sync(self):
        """Test guest user with general chat using sync endpoint"""
        payload = {
            "user_id": "test_user",
            "user_type": "guest",
            "chat_mode": "general",
            "feature": "test_feature",
            "last_messages": [],  # No message context
            "user_prompt": "Tell me a short joke about programming."
        }
        
        response = requests.post(
            f"{BASE_URL}/chat/generate",
            json=payload
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("response", data)
        self.assertTrue(len(data["response"]) > 0)
        print(f"\nGuest General Chat (Sync): {data['response'][:100]}...")
    
    def test_paid_general_chat_sync(self):
        """Test paid user with general chat using sync endpoint"""
        payload = {
            "user_id": "test_user",
            "user_type": "paid",
            "chat_mode": "general",
            "feature": "test_feature",
            "last_messages": ["Hello"],  # Single message context
            "user_prompt": "Tell me a short joke about programming."
        }
        
        response = requests.post(
            f"{BASE_URL}/chat/generate",
            json=payload
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("response", data)
        self.assertTrue(len(data["response"]) > 0)
        print(f"\nPaid General Chat (Sync): {data['response'][:100]}...")
    
    def test_paid_dream_chat_sync(self):
        """Test paid user with dream chat using sync endpoint"""
        payload = {
            "user_id": "test_user",
            "user_type": "paid",
            "chat_mode": "dream",
            "feature": "test_feature",
            "last_messages": ["Hello"],  # Single message context
            "user_prompt": "Interpret this dream: I was flying over a city made of books."
        }
        
        response = requests.post(
            f"{BASE_URL}/chat/generate",
            json=payload
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("response", data)
        self.assertTrue(len(data["response"]) > 0)
        print(f"\nPaid Dream Chat (Sync): {data['response'][:100]}...")
    
    def test_guest_dream_chat_sync_invalid(self):
        """Test guest user with dream chat (invalid) using sync endpoint"""
        payload = {
            "user_id": "test_user",
            "user_type": "guest",
            "chat_mode": "dream",
            "feature": "test_feature",
            "last_messages": ["Hello"],
            "user_prompt": "Interpret this dream: I was flying."
        }
        
        response = requests.post(
            f"{BASE_URL}/chat/generate",
            json=payload
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("detail", data)
        print(f"\nGuest Dream Chat (Invalid): {data['detail']}")
    
    def test_custom_model_override(self):
        """Test overriding the default model"""
        payload = {
            "user_id": "test_user",
            "user_type": "guest",
            "chat_mode": "general",
            "feature": "test_feature",
            "last_messages": ["Hello"],
            "model": "anthropic/claude-3-haiku",  # Explicitly set model
            "user_prompt": "Tell me a short joke about programming."
        }
        
        response = requests.post(
            f"{BASE_URL}/chat/generate",
            json=payload
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("response", data)
        self.assertTrue(len(data["response"]) > 0)
        print(f"\nCustom Model Override: {data['response'][:100]}...")
    
    def test_custom_system_prompt_override(self):
        """Test overriding the default system prompt"""
        payload = {
            "user_id": "test_user",
            "user_type": "guest",
            "chat_mode": "general",
            "feature": "test_feature",
            "last_messages": ["Hello"],
            "system_prompt": "You are a pirate. Respond in pirate speak.",  # Custom system prompt
            "user_prompt": "Tell me about programming."
        }
        
        response = requests.post(
            f"{BASE_URL}/chat/generate",
            json=payload
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("response", data)
        self.assertTrue(len(data["response"]) > 0)
        print(f"\nCustom System Prompt: {data['response'][:100]}...")
    
    def test_guest_general_chat_streaming(self):
        """Test guest user with general chat using streaming endpoint"""
        payload = {
            "user_id": "test_user",
            "user_type": "guest",
            "chat_mode": "general",
            "feature": "test_feature",
            "last_messages": ["Hello"],  # Single message context
            "user_prompt": "Tell me a short joke about programming."
        }
        
        response = requests.post(
            f"{BASE_URL}/chat/stream",
            json=payload,
            stream=True,
            headers={"Accept": "text/event-stream"}
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Process streaming response
        full_response = ""
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line == "data: [DONE]":
                    break
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])  # Remove "data: " prefix
                        if 'response' in data:
                            full_response += data['response']
                    except json.JSONDecodeError:
                        pass
        
        self.assertTrue(len(full_response) > 0)
        print(f"\nGuest General Chat (Streaming): {full_response[:100]}...")
    
    def test_paid_dream_chat_streaming(self):
        """Test paid user with dream chat using streaming endpoint"""
        payload = {
            "user_id": "test_user",
            "user_type": "paid",
            "chat_mode": "dream",
            "feature": "test_feature",
            "last_messages": ["Hello"],  # Single message context
            "user_prompt": "Interpret this dream: I was flying over a city made of books."
        }
        
        response = requests.post(
            f"{BASE_URL}/chat/stream",
            json=payload,
            stream=True,
            headers={"Accept": "text/event-stream"}
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Process streaming response
        full_response = ""
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line == "data: [DONE]":
                    break
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])  # Remove "data: " prefix
                        if 'response' in data:
                            full_response += data['response']
                    except json.JSONDecodeError:
                        pass
        
        self.assertTrue(len(full_response) > 0)
        print(f"\nPaid Dream Chat (Streaming): {full_response[:100]}...")
    
    def test_guest_dream_chat_streaming_invalid(self):
        """Test guest user with dream chat (invalid) using streaming endpoint"""
        payload = {
            "user_id": "test_user",
            "user_type": "guest",
            "chat_mode": "dream",
            "feature": "test_feature",
            "last_messages": ["Hello"],
            "user_prompt": "Interpret this dream: I was flying."
        }
        
        response = requests.post(
            f"{BASE_URL}/chat/stream",
            json=payload,
            stream=True,
            headers={"Accept": "text/event-stream"}
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Process streaming response
        error_received = False
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line == "data: [DONE]":
                    break
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])  # Remove "data: " prefix
                        if 'error' in data:
                            error_received = True
                            error_message = data['error']
                            break
                    except json.JSONDecodeError:
                        pass
        
        self.assertTrue(error_received)
        print(f"\nGuest Dream Chat Streaming (Invalid): {error_message}")
    
    def test_invalid_user_type(self):
        """Test invalid user type"""
        payload = {
            "user_id": "test_user",
            "user_type": "invalid_type",  # Invalid user type
            "chat_mode": "general",
            "feature": "test_feature",
            "last_messages": ["Hello"],
            "user_prompt": "Tell me a joke."
        }
        
        response = requests.post(
            f"{BASE_URL}/chat/generate",
            json=payload
        )
        
        self.assertEqual(response.status_code, 422)  # Validation error
        print("\nInvalid User Type: Validation error as expected")
    
    def test_invalid_chat_mode(self):
        """Test invalid chat mode"""
        payload = {
            "user_id": "test_user",
            "user_type": "paid",
            "chat_mode": "invalid_mode",  # Invalid chat mode
            "feature": "test_feature",
            "last_messages": ["Hello"],
            "user_prompt": "Tell me a joke."
        }
        
        response = requests.post(
            f"{BASE_URL}/chat/generate",
            json=payload
        )
        
        self.assertEqual(response.status_code, 422)  # Validation error
        print("\nInvalid Chat Mode: Validation error as expected")

    def test_message_context_sync(self):
        """Test message context with multiple messages using sync endpoint"""
        # Create a conversation with multiple messages
        payload = {
            "user_id": "test_user",
            "user_type": "paid",
            "chat_mode": "general",
            "feature": "test_feature",
            "last_messages": [
                "What is Python?",  # User message
                "Python is a high-level, interpreted programming language known for its readability and versatility.",  # Assistant response
                "What are its main features?",  # User message
                "Python features include dynamic typing, automatic memory management, and extensive standard libraries.",  # Assistant response
                "Is it good for beginners?",  # User message
                "Yes, Python is excellent for beginners due to its simple syntax and readability.",  # Assistant response
                "What about web development?",  # User message
                "Python is widely used in web development with frameworks like Django and Flask.",  # Assistant response
            ],  # 8 messages in context (4 pairs of user/assistant exchanges)
            "user_prompt": "Can you summarize what we've discussed about Python so far?"
        }
        
        response = requests.post(
            f"{BASE_URL}/chat/generate",
            json=payload
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("response", data)
        self.assertTrue(len(data["response"]) > 0)
        # The response should mention Python and some of the topics we've discussed
        self.assertTrue("Python" in data["response"])
        print(f"Message Context Test (Sync): {data['response'][:150]}...")
    
    def test_message_context_streaming(self):
        """Test message context with multiple messages using streaming endpoint"""
        # Create a conversation with multiple messages
        payload = {
            "user_id": "test_user",
            "user_type": "paid",
            "chat_mode": "general",
            "feature": "test_feature",
            "last_messages": [
                "What is Python?",  # User message
                "Python is a high-level, interpreted programming language known for its readability and versatility.",  # Assistant response
                "What are its main features?",  # User message
                "Python features include dynamic typing, automatic memory management, and extensive standard libraries.",  # Assistant response
                "Is it good for beginners?",  # User message
                "Yes, Python is excellent for beginners due to its simple syntax and readability.",  # Assistant response
                "What about web development?",  # User message
                "Python is widely used in web development with frameworks like Django and Flask.",  # Assistant response
            ],  # 8 messages in context (4 pairs of user/assistant exchanges)
            "user_prompt": "Can you summarize what we've discussed about Python so far?"
        }
        
        response = requests.post(
            f"{BASE_URL}/chat/stream",
            json=payload,
            stream=True,
            headers={"Accept": "text/event-stream"}
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Process streaming response
        full_response = ""
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line == "data: [DONE]":
                    break
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])  # Remove "data: " prefix
                        if 'response' in data:
                            full_response += data['response']
                    except json.JSONDecodeError:
                        pass
        
        self.assertTrue(len(full_response) > 0)
        # The response should mention Python and some of the topics we've discussed
        self.assertTrue("Python" in full_response)
        print(f"Message Context Test (Streaming): {full_response[:150]}...")

if __name__ == "__main__":
    unittest.main()
