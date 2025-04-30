import unittest
import requests
import json
import os
import sys
import time

# Add parent directory to path to allow importing from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestChatAnalysisEndpoint(unittest.TestCase):
    BASE_URL = "http://127.0.0.1:8000"
    
    def setUp(self):
        # Check if server is running
        try:
            requests.get(f"{self.BASE_URL}/docs")
        except requests.exceptions.ConnectionError:
            self.skipTest("API server is not running")
    
    def test_basic_analysis(self):
        """Test basic analysis functionality with a simple conversation"""
        payload = {
            "user_id": "test_user",
            "user_type": "guest",
            "chat_messages": [
                "User: How does the weather look today?",
                "Assistant: It's sunny with a high of 75 degrees.",
                "User: Great! I might go for a walk then.",
                "Assistant: That sounds like a good idea. Enjoy your walk!"
            ]
        }
        
        response = requests.post(
            f"{self.BASE_URL}/chat/analyze",
            json=payload
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check response structure
        self.assertIn('summary', data)
        self.assertIn('keywords', data)
        self.assertIn('emoji_count', data)
        self.assertIn('emojis', data)
        self.assertIn('sentiment', data)
        
        # Basic content checks
        self.assertIsInstance(data['summary'], str)
        self.assertIsInstance(data['keywords'], dict)
        self.assertIsInstance(data['emoji_count'], int)
        self.assertIsInstance(data['emojis'], dict)
        self.assertIsInstance(data['sentiment'], str)
        
        # Check that sentiment is one of the expected values
        self.assertIn(data['sentiment'], ["positive", "negative", "neutral", "mixed"])
    
    def test_emotional_content(self):
        """Test analysis with emotional content"""
        payload = {
            "user_id": "test_user",
            "user_type": "paid",
            "chat_messages": [
                "User: I'm feeling really anxious about my upcoming interview. 😟",
                "Assistant: It's normal to feel nervous before interviews. What specifically are you worried about?",
                "User: I'm afraid I'll freeze up when they ask me difficult questions. 😰",
                "Assistant: That's a common concern. Would it help to practice some typical interview questions beforehand? 🤔",
                "User: Yes, that's a good idea. I'm still stressed though.",
                "Assistant: Take deep breaths before the interview. Remember that you've prepared well and are qualified for this position! 👍"
            ]
        }
        
        response = requests.post(
            f"{self.BASE_URL}/chat/analyze",
            json=payload
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check for emotional keywords
        emotional_keywords = ['anxious', 'nervous', 'afraid', 'worried', 'stressed']
        found_emotional = False
        for keyword in emotional_keywords:
            if keyword in data['keywords']:
                found_emotional = True
                break
        
        self.assertTrue(found_emotional, "No emotional keywords detected")
        
        # Check emoji detection
        self.assertGreaterEqual(data['emoji_count'], 3, "Failed to detect emojis")
        
        # Check sentiment (should be negative or mixed)
        self.assertIn(data['sentiment'], ["negative", "mixed"])
    
    def test_sentiment_analysis_positive(self):
        """Test positive sentiment detection"""
        payload = {
            "user_id": "test_user",
            "user_type": "paid",
            "chat_messages": [
                "User: I just got a promotion at work! 🎉",
                "Assistant: Congratulations! That's wonderful news! 🎊",
                "User: Thank you! I'm so happy and excited about the new role.",
                "Assistant: You should be proud of your achievement. How will you celebrate? 🥂",
                "User: I'm going out to dinner with friends tonight. I'm thrilled!",
                "Assistant: That sounds perfect! Enjoy your celebration, you've earned it! 🌟"
            ]
        }
        
        response = requests.post(
            f"{self.BASE_URL}/chat/analyze",
            json=payload
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should detect positive sentiment
        self.assertEqual(data['sentiment'], "positive")
        
        # Should have positive keywords
        positive_keywords = ['happy', 'excited', 'thrilled', 'congratulations', 'celebration']
        found_positive = False
        for keyword in positive_keywords:
            if keyword in data['keywords']:
                found_positive = True
                break
        
        self.assertTrue(found_positive, "No positive keywords detected")
    
    def test_sentiment_analysis_negative(self):
        """Test negative sentiment detection"""
        payload = {
            "user_id": "test_user",
            "user_type": "paid",
            "chat_messages": [
                "User: I lost my job today. 😢",
                "Assistant: I'm so sorry to hear that. That must be really difficult. 😔",
                "User: I'm worried about how I'll pay my bills now.",
                "Assistant: That's a valid concern. Have you looked into unemployment benefits?",
                "User: Not yet. I'm still in shock and feeling overwhelmed.",
                "Assistant: Take some time to process this. When you're ready, I can help you think through next steps. 🤗"
            ]
        }
        
        response = requests.post(
            f"{self.BASE_URL}/chat/analyze",
            json=payload
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should detect negative sentiment
        self.assertEqual(data['sentiment'], "negative")
    
    def test_sentiment_analysis_mixed(self):
        """Test mixed sentiment detection"""
        payload = {
            "user_id": "test_user",
            "user_type": "paid",
            "chat_messages": [
                "User: I got accepted to my dream school! 🎉 But it's in another country and I'm nervous about moving. 😕",
                "Assistant: Congratulations on your acceptance! It's completely normal to have mixed feelings about such a big change.",
                "User: I'm excited about the opportunity but scared about being so far from family.",
                "Assistant: Those are valid feelings. Many students experience this. Have you thought about how you'll stay connected with loved ones?",
                "User: Yes, I'll plan regular video calls. I'm trying to focus on the positive, but it's challenging.",
                "Assistant: It sounds like you're approaching this thoughtfully. Remember that it's okay to be both excited and anxious about new adventures. 🌈"
            ]
        }
        
        response = requests.post(
            f"{self.BASE_URL}/chat/analyze",
            json=payload
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should detect mixed sentiment
        self.assertEqual(data['sentiment'], "mixed")
    
    def test_validation_errors(self):
        """Test validation errors"""
        # Test empty chat messages
        payload = {
            "user_id": "test_user",
            "user_type": "guest",
            "chat_messages": []
        }
        
        response = requests.post(
            f"{self.BASE_URL}/chat/analyze",
            json=payload
        )
        
        self.assertEqual(response.status_code, 422, "Should reject empty chat messages")
        
        # Test missing required fields
        payload = {
            "user_id": "test_user"
            # Missing user_type and chat_messages
        }
        
        response = requests.post(
            f"{self.BASE_URL}/chat/analyze",
            json=payload
        )
        
        self.assertEqual(response.status_code, 422, "Should reject missing required fields")
        
        # Test invalid user type
        payload = {
            "user_id": "test_user",
            "user_type": "invalid_type",
            "chat_messages": ["User: Hello", "Assistant: Hi there!"]
        }
        
        response = requests.post(
            f"{self.BASE_URL}/chat/analyze",
            json=payload
        )
        
        self.assertEqual(response.status_code, 422, "Should reject invalid user type")
    
    def test_model_override(self):
        """Test model override functionality"""
        payload = {
            "user_id": "test_user",
            "user_type": "guest",
            "chat_messages": ["User: Hello", "Assistant: Hi there!"],
            "model": "anthropic/claude-3-opus"  # Override with a more powerful model
        }
        
        response = requests.post(
            f"{self.BASE_URL}/chat/analyze",
            json=payload
        )
        
        self.assertEqual(response.status_code, 200, "Model override should be accepted")
    
    def test_performance(self):
        """Test performance with a longer conversation"""
        # Create a longer conversation
        chat_messages = []
        for i in range(10):
            chat_messages.append(f"User: This is message {i+1} from the user.")
            chat_messages.append(f"Assistant: This is response {i+1} from the assistant.")
        
        payload = {
            "user_id": "test_user",
            "user_type": "paid",
            "chat_messages": chat_messages
        }
        
        start_time = time.time()
        response = requests.post(
            f"{self.BASE_URL}/chat/analyze",
            json=payload
        )
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        
        # Check response time (should be reasonable even for longer conversations)
        response_time = end_time - start_time
        print(f"\nResponse time for long conversation: {response_time:.2f} seconds")
        
        # No strict assertion on time as it depends on the model and server,
        # but we log it for monitoring

if __name__ == "__main__":
    unittest.main()
