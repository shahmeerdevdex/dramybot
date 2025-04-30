import unittest
import requests
import json
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base URL for API
BASE_URL = "http://127.0.0.1:8000"

class TestPerformance(unittest.TestCase):
    
    def setUp(self):
        """Set up test case with common variables"""
        # Check if the server is running
        try:
            response = requests.get(f"{BASE_URL}/docs")
            if response.status_code != 200:
                self.skipTest("API server is not running. Start the server with 'uvicorn app.main:app --reload'")
        except requests.exceptions.ConnectionError:
            self.skipTest("API server is not running. Start the server with 'uvicorn app.main:app --reload'")
    
    def test_response_time_sync(self):
        """Test response time for synchronous endpoint"""
        payload = {
            "user_id": "test_user",
            "user_type": "guest",
            "chat_mode": "general",
            "feature": "test_feature",
            "last_messages": ["Hello"],
            "user_prompt": "What is 2+2?"
        }
        
        # Measure response time
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/chat/generate",
            json=payload
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        self.assertEqual(response.status_code, 200)
        print(f"\nSync Response Time: {response_time:.2f} seconds")
    
    def test_response_time_streaming(self):
        """Test response time for streaming endpoint (time to first chunk)"""
        payload = {
            "user_id": "test_user",
            "user_type": "guest",
            "chat_mode": "general",
            "feature": "test_feature",
            "last_messages": ["Hello"],
            "user_prompt": "What is 2+2?"
        }
        
        # Measure time to first chunk
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/chat/stream",
            json=payload,
            stream=True,
            headers={"Accept": "text/event-stream"}
        )
        
        first_chunk_time = None
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith("data: ") and "response" in line[6:]:
                    first_chunk_time = time.time()
                    break
        
        time_to_first_chunk = first_chunk_time - start_time if first_chunk_time else None
        
        self.assertIsNotNone(time_to_first_chunk)
        print(f"\nStreaming Time to First Chunk: {time_to_first_chunk:.2f} seconds")
    
    def test_load_multiple_requests(self):
        """Test handling multiple requests in parallel"""
        num_requests = 5  # Number of parallel requests
        
        def make_request():
            payload = {
                "user_id": "test_user",
                "user_type": "guest",
                "chat_mode": "general",
                "feature": "test_feature",
                "last_messages": ["Hello"],
                "user_prompt": "What is 2+2?"
            }
            
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/chat/generate",
                json=payload
            )
            end_time = time.time()
            
            return {
                "status_code": response.status_code,
                "response_time": end_time - start_time
            }
        
        # Execute requests in parallel
        with ThreadPoolExecutor(max_workers=num_requests) as executor:
            results = list(executor.map(lambda _: make_request(), range(num_requests)))
        
        # Analyze results
        status_codes = [result["status_code"] for result in results]
        response_times = [result["response_time"] for result in results]
        
        # All requests should be successful
        self.assertTrue(all(status == 200 for status in status_codes))
        
        # Calculate statistics
        avg_time = statistics.mean(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        print(f"\nLoad Test Results ({num_requests} parallel requests):")
        print(f"  Average response time: {avg_time:.2f} seconds")
        print(f"  Minimum response time: {min_time:.2f} seconds")
        print(f"  Maximum response time: {max_time:.2f} seconds")

if __name__ == "__main__":
    unittest.main()
