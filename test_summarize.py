import requests
import json

def test_summarize_endpoint():
    print("\n===== Testing Chat Summarization Endpoint =====\n")
    
    # Test case 1: Guest user with a short conversation
    print("Test Case 1: Guest user with a short conversation")
    payload = {
        "user_id": "test_user",
        "user_type": "guest",
        "chat_messages": [
            "User: Hello, I need help with Python programming.",
            "Assistant: Hi there! I'd be happy to help with Python. What specific questions do you have?",
            "User: I'm trying to understand list comprehensions. Can you explain them?",
            "Assistant: List comprehensions are a concise way to create lists in Python. The basic syntax is [expression for item in iterable if condition]. They allow you to transform and filter data in a single line.",
            "User: Could you give me an example?",
            "Assistant: Sure! Here's a simple example: [x*2 for x in range(5)] would create [0, 2, 4, 6, 8]. This takes each number from 0 to 4 and multiplies it by 2."
        ]
    }
    
    response = requests.post(
        "http://127.0.0.1:8000/chat/summarize",
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Summary: {data['summary']}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
    
    # Test case 2: Paid user with a longer conversation
    print("\nTest Case 2: Paid user with a longer conversation")
    payload = {
        "user_id": "test_user",
        "user_type": "paid",
        "chat_messages": [
            "User: I'm planning a trip to Japan next month.",
            "Assistant: That sounds exciting! Japan is a wonderful destination. Do you have specific cities or regions in mind?",
            "User: I'm thinking Tokyo and Kyoto. What are the must-see attractions?",
            "Assistant: In Tokyo, don't miss the Tokyo Skytree, Shibuya Crossing, Meiji Shrine, and Shinjuku Gyoen National Garden. For Kyoto, I recommend Fushimi Inari Shrine, Kinkaku-ji (Golden Pavilion), Arashiyama Bamboo Grove, and Gion District.",
            "User: How many days should I spend in each city?",
            "Assistant: I'd recommend at least 4-5 days in Tokyo and 3-4 days in Kyoto to see the major attractions without rushing. If you have more time, you could also take day trips to nearby places like Nara from Kyoto or Hakone from Tokyo.",
            "User: What about transportation between cities?",
            "Assistant: The most efficient way to travel between Tokyo and Kyoto is the Shinkansen (bullet train). It takes about 2.5 hours and is covered by the Japan Rail Pass if you purchase one. The trains are frequent, comfortable, and very reliable.",
            "User: Is it worth getting a Japan Rail Pass?",
            "Assistant: If you're planning to travel between multiple cities, a Japan Rail Pass is usually worth it. For just Tokyo and Kyoto, calculate the round-trip Shinkansen cost (about 27,000 yen) and compare it to the 7-day JR Pass price (about 33,000 yen). If you'll use local JR lines within cities or make any day trips, the pass likely becomes worthwhile."
        ]
    }
    
    response = requests.post(
        "http://127.0.0.1:8000/chat/summarize",
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Summary: {data['summary']}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
    
    # Test case 3: Empty chat messages (should return validation error)
    print("\nTest Case 3: Empty chat messages (validation error expected)")
    payload = {
        "user_id": "test_user",
        "user_type": "guest",
        "chat_messages": []
    }
    
    response = requests.post(
        "http://127.0.0.1:8000/chat/summarize",
        json=payload
    )
    
    if response.status_code != 200:
        print(f"Validation error received as expected: {response.status_code}")
    else:
        print("Error: Expected validation error but received success response")

if __name__ == "__main__":
    test_summarize_endpoint()
