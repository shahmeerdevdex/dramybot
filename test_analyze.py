import requests
import json

def test_analyze_endpoint():
    print("\n===== Testing Chat Analysis Endpoint =====\n")
    
    # Test cases with different emotional content to verify sentiment analysis
    
    # Test case 1: Guest user with emotional content and emojis
    print("Test Case 1: Guest user with emotional content and emojis")
    payload = {
        "user_id": "test_user",
        "user_type": "guest",
        "chat_messages": [
            "User: I've been feeling really anxious 😟 about my upcoming presentation at work.",
            "Assistant: I understand that presentations can be stressful. What specifically are you worried about? 🤔",
            "User: I'm scared 😨 that I'll forget what to say or that people will judge me harshly.",
            "Assistant: Those are common fears. Remember that everyone gets nervous about public speaking. Would it help to practice with a friend first? 👍",
            "User: Yes, that's a good idea. I'm still worried though. My heart races just thinking about it. 💓",
            "Assistant: That's completely normal. Deep breathing exercises can help calm your nerves. Also, remember that you're well-prepared and know your material! 😊"
        ]
    }
    
    response = requests.post(
        "http://127.0.0.1:8000/chat/analyze",
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Summary: {data['summary']}")
        print(f"Sentiment: {data['sentiment']}")
        print("\nKeywords:")
        for keyword, count in data['keywords'].items():
            print(f"  {keyword}: {count}")
        print(f"\nEmoji count: {data['emoji_count']}")
        print("Emojis:")
        for emoji, count in data['emojis'].items():
            print(f"  {emoji}: {count}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
    
    # Test case 2: Paid user with mixed emotions
    print("\nTest Case 2: Paid user with mixed emotions")
    payload = {
        "user_id": "test_user",
        "user_type": "paid",
        "chat_messages": [
            "User: I just got a promotion at work! 🎉 I'm so excited!",
            "Assistant: Congratulations! That's wonderful news! 🎊 How are you planning to celebrate?",
            "User: Thanks! I'm going out to dinner with friends tonight. But I'm also a bit nervous about the new responsibilities. 😬",
            "Assistant: That's understandable. It's normal to feel both excited and nervous about new challenges. What aspects of the new role concern you the most?",
            "User: I'll be managing a team for the first time. I'm worried I won't be a good leader. 😕",
            "Assistant: Many new managers feel that way. Remember that leadership skills develop with practice. Would it help to discuss some management strategies? 💡",
            "User: Yes, that would be great. I want to be supportive but also effective. I hope I can find the right balance. 🤞",
            "Assistant: Finding that balance is key. Good leaders are both supportive and able to set clear expectations. I'm confident you'll do well, especially since you're already thinking about how to be effective! 👏"
        ]
    }
    
    response = requests.post(
        "http://127.0.0.1:8000/chat/analyze",
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Summary: {data['summary']}")
        print(f"Sentiment: {data['sentiment']}")
        print("\nKeywords:")
        for keyword, count in data['keywords'].items():
            print(f"  {keyword}: {count}")
        print(f"\nEmoji count: {data['emoji_count']}")
        print("Emojis:")
        for emoji, count in data['emojis'].items():
            print(f"  {emoji}: {count}")
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
        "http://127.0.0.1:8000/chat/analyze",
        json=payload
    )
    
    if response.status_code != 200:
        print(f"Validation error received as expected: {response.status_code}")
    else:
        print("Error: Expected validation error but received success response")

def test_advanced_analysis():
    print("\n===== Testing Advanced Analysis Features =====\n")
    
    # Test case 1: Positive sentiment
    print("Test Case 1: Positive sentiment")
    payload = {
        "user_id": "test_user",
        "user_type": "paid",
        "chat_messages": [
            "User: I just got accepted to my dream university! 🎉 I'm so happy and excited!",
            "Assistant: That's fantastic news! Congratulations! 🎊 How are you planning to celebrate?",
            "User: Thank you! I'm going out for dinner with my family tonight. I'm just so grateful for all their support. 🥰",
            "Assistant: That sounds like a wonderful way to celebrate! Your family will be so proud of you. What program will you be studying? 🎓",
            "User: I'll be studying computer science! I've been dreaming about this for years. I'm so thrilled to finally start this journey! 💻",
            "Assistant: Computer Science is an excellent choice! With your enthusiasm and dedication, I'm sure you'll excel in your studies. This is truly a moment to cherish! 🌟"
        ]
    }
    
    response = requests.post(
        "http://127.0.0.1:8000/chat/analyze",
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Summary: {data['summary']}")
        print(f"Sentiment: {data['sentiment']}")
        print("\nKeywords:")
        for keyword, count in data['keywords'].items():
            print(f"  {keyword}: {count}")
        print(f"\nEmoji count: {data['emoji_count']}")
        print("Emojis:")
        for emoji, count in data['emojis'].items():
            print(f"  {emoji}: {count}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
    
    # Test case 2: Negative sentiment
    print("\nTest Case 2: Negative sentiment")
    payload = {
        "user_id": "test_user",
        "user_type": "paid",
        "chat_messages": [
            "User: I failed my final exam today. 😢 I'm devastated.",
            "Assistant: I'm so sorry to hear that. It's completely understandable to feel upset about this. Would you like to talk about what happened? 🤔",
            "User: I studied so hard but I just froze up during the test. I'm worried I might have to repeat the course now. 😰",
            "Assistant: That sounds really stressful. Test anxiety can be overwhelming sometimes. Have you spoken with your professor about possible options? 🙁",
            "User: Not yet. I'm too embarrassed and disappointed in myself. I feel like I've let everyone down. 😔",
            "Assistant: Please don't be too hard on yourself. Many students experience test anxiety, and one exam doesn't define your abilities or worth. Would it help to prepare what you might say to your professor? 💌"
        ]
    }
    
    response = requests.post(
        "http://127.0.0.1:8000/chat/analyze",
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Summary: {data['summary']}")
        print(f"Sentiment: {data['sentiment']}")
        print("\nKeywords:")
        for keyword, count in data['keywords'].items():
            print(f"  {keyword}: {count}")
        print(f"\nEmoji count: {data['emoji_count']}")
        print("Emojis:")
        for emoji, count in data['emojis'].items():
            print(f"  {emoji}: {count}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
    
    # Test case 3: Mixed sentiment
    print("\nTest Case 3: Mixed sentiment")
    payload = {
        "user_id": "test_user",
        "user_type": "paid",
        "chat_messages": [
            "User: I got a job offer today! 🎉 But it means I'll have to move away from my family and friends. 😕",
            "Assistant: That's both exciting and challenging news! Congratulations on the job offer. 🎊 It's natural to have mixed feelings about a big life change like this. What are you thinking about it?",
            "User: I'm happy about the career opportunity, but sad about leaving everyone behind. I'm also nervous about moving to a new city alone. 😬",
            "Assistant: Those are all valid feelings. Big changes often come with both excitement and anxiety. Have you thought about ways to stay connected with your loved ones while embracing this new chapter? 💭",
            "User: Yes, I'm planning regular video calls and visits. I'm trying to focus on the positive aspects, but it's still hard. 🙂😢",
            "Assistant: It sounds like you're approaching this thoughtfully. Remember that it's okay to be excited about your future while also honoring your feelings of sadness. This transition period might be difficult, but it can also lead to growth and new experiences. 🌱"
        ]
    }
    
    response = requests.post(
        "http://127.0.0.1:8000/chat/analyze",
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Summary: {data['summary']}")
        print(f"Sentiment: {data['sentiment']}")
        print("\nKeywords:")
        for keyword, count in data['keywords'].items():
            print(f"  {keyword}: {count}")
        print(f"\nEmoji count: {data['emoji_count']}")
        print("Emojis:")
        for emoji, count in data['emojis'].items():
            print(f"  {emoji}: {count}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_analyze_endpoint()
    test_advanced_analysis()
