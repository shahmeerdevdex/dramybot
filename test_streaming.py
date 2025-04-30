import requests
import json
import time

def test_user_type_and_mode(user_type, chat_mode, custom_prompt=None):
    print(f"\n===== Testing {user_type} user with {chat_mode} chat mode =====")
    
    # Prepare the request payload
    payload = {
        "user_id": "test_user",
        "user_type": user_type,
        "chat_mode": chat_mode,
        "feature": "test_feature",
        "last_messages": ["Hello"],
        "user_prompt": custom_prompt or "Tell me a short joke about programming."
    }
    
    # Send the request with stream=True to get the streaming response
    response = requests.post(
        "http://127.0.0.1:8000/chat/stream",
        json=payload,
        stream=True,
        headers={"Accept": "text/event-stream"}
    )
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return
    
    # Process the streaming response
    print("Streaming response:")
    full_response = ""
    error_received = False
    
    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            
            if line == "data: [DONE]":
                print("Stream completed.")
                break
                
            if line.startswith("data: "):
                try:
                    data = json.loads(line[6:])  # Remove "data: " prefix
                    
                    if 'error' in data:
                        print(f"Error: {data['error']}")
                        error_received = True
                        break
                        
                    if 'response' in data:
                        chunk = data['response']
                        full_response += chunk
                        # Print only the first 50 characters of each chunk to keep output clean
                        print_chunk = chunk if len(chunk) <= 50 else chunk[:47] + "..."
                        print(f"Received: {print_chunk}")
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {e} - {line}")
    
    if not error_received:
        # Print only the first 200 characters of the full response to keep output clean
        print_response = full_response if len(full_response) <= 200 else full_response[:197] + "..."
        print("\nFull response (truncated):")
        print(print_response)
        
    # Add a small delay between tests
    time.sleep(1)

def test_all_user_types_and_modes():
    # Test guest user with general chat
    test_user_type_and_mode("guest", "general")
    
    # Test paid user with general chat
    test_user_type_and_mode("paid", "general")
    
    # Test paid user with dream chat
    test_user_type_and_mode("paid", "dream", "Interpret this dream: I was flying over a city made of books.")
    
    # Test invalid combination: guest user with dream chat (should return an error)
    test_user_type_and_mode("guest", "dream")

if __name__ == "__main__":
    test_all_user_types_and_modes()
