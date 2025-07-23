# OpenRouter Chat API Documentation

## Overview

The OpenRouter Chat API provides a flexible interface for generating AI-powered chat responses using OpenRouter's language models. The API supports different user types, chat modes, and both synchronous and streaming responses.

## Base URL

```
http://your-domain.com
```

## Authentication

The API uses the OpenRouter API key for authentication with the OpenRouter service. This key is stored as an environment variable (`OPENROUTER_API_KEY`) on the server.

## User Types

The API supports two user types:

- **Guest**: Limited access with basic models
- **Paid**: Full access with premium models

## Chat Modes

The API supports two chat modes:

- **General**: Standard chat functionality (available to all user types)
- **Dream**: Specialized for dream interpretation and creative assistance (available only to paid users)

## Endpoints

### 1. Generate Chat Response (Synchronous)

Generates a chat response in a synchronous manner.

**URL**: `/chat/generate`

**Method**: `POST`

**Request Body**:

```json
{
  "user_id": "string",          // Required: Unique identifier for the user
  "user_type": "guest|paid",   // Required: Type of user
  "chat_mode": "general|dream", // Optional: Chat mode (defaults to "general")
  "feature": "string",         // Required: Feature identifier
  "last_messages": ["string"], // Required: Array of previous messages
  "model": "string",           // Optional: Override the default model
  "temperature": 0.7,           // Optional: Temperature for response generation
  "system_prompt": "string",   // Optional: Override the default system prompt
  "user_prompt": "string"      // Required: User's input prompt (cannot be empty)
}
```

**Response**:

```json
{
  "response": "string" // The generated chat response
}
```

**Status Codes**:

- `200 OK`: Request successful
- `400 Bad Request`: Invalid combination of user type and chat mode
- `422 Unprocessable Entity`: Validation error in request parameters

**Example Request (Guest User with General Chat)**:

```json
{
  "user_id": "user123",
  "user_type": "guest",
  "chat_mode": "general",
  "feature": "chat",
  "last_messages": ["Hello"],
  "user_prompt": "Tell me a joke about programming."
}
```

**Example Response**:

```json
{
  "response": "Why do programmers prefer dark mode? Because light attracts bugs!"
}
```

### 2. Generate Streaming Chat Response

Generates a chat response in a streaming manner using Server-Sent Events (SSE).

**URL**: `/chat/stream`

**Method**: `POST`

**Headers**:

```
Accept: text/event-stream
```

**Request Body**:

Same as the synchronous endpoint.

**Response**:

A stream of Server-Sent Events (SSE) with the following format:

```
data: {"response": "chunk of text"}

data: {"response": "another chunk of text"}

...

data: [DONE]
```

In case of an error:

```
data: {"error": "error message"}

data: [DONE]
```

**Status Codes**:

- `200 OK`: Request successful (even if there's an error in the stream)
- `422 Unprocessable Entity`: Validation error in request parameters

**Example Request (Paid User with Dream Chat)**:

```json
{
  "user_id": "user456",
  "user_type": "paid",
  "chat_mode": "dream",
  "feature": "dream_interpretation",
  "last_messages": ["Hello"],
  "user_prompt": "Interpret this dream: I was swimming in an ocean of stars."
}
```

**Example Response Stream**:

```
data: {"response": "Your dream about flying over a city made of books "}

data: {"response": "is rich with symbolism. Flying often represents "}

data: {"response": "freedom and perspective, while books symbolize "}

data: {"response": "knowledge and wisdom. This dream might suggest..."}

...

data: [DONE]
```

### 3. Summarize Chat Conversation

Generates a concise 2-line summary of a chat conversation.

**URL**: `/chat/summarize`

**Method**: `POST`

**Request Body**:

```json
{
  "user_id": "string",          // Required: Unique identifier for the user
  "user_type": "guest|paid",   // Required: Type of user
  "chat_messages": ["string"], // Required: Array of chat messages to summarize
  "model": "string"            // Optional: Override the default model
}
```

**Response**:

```json
{
  "summary": "string" // The 2-line summary of the conversation
}
```

**Status Codes**:

- `200 OK`: Request successful
- `422 Unprocessable Entity`: Validation error in request parameters

**Example Request**:

```json
{
  "user_id": "user123",
  "user_type": "guest",
  "chat_messages": [
    "User: Hello, I need help with Python programming.",
    "Assistant: Hi there! I'd be happy to help with Python. What specific questions do you have?",
    "User: I'm trying to understand list comprehensions. Can you explain them?"
  ]
}
```

**Example Response**:

```json
{
  "summary": "User is seeking help with Python programming, specifically to understand list comprehensions.\nAssistant offered to help and asked for specific questions."
}
```

### 4. Analyze Chat Conversation

Analyzes a chat conversation to extract a summary, keywords (especially emotional ones), and emojis.

**URL**: `/chat/analyze`

**Method**: `POST`

**Request Body**:

```json
{
  "user_id": "string",          // Required: Unique identifier for the user
  "user_type": "guest|paid",   // Required: Type of user
  "chat_messages": ["string"], // Required: Array of chat messages to analyze
  "model": "string"            // Optional: Override the default model
}
```

**Response**:

```json
{
  "summary": "string",         // A concise summary of the conversation
  "keywords": {                 // Dictionary of keywords and their counts
    "keyword1": 1,
    "keyword2": 2
  },
  "emoji_count": 5,             // Total count of emojis in the conversation
  "emojis": {                   // Dictionary of emojis and their counts
    "😊": 2,
    "👍": 1,
    "❤️": 2
  },
  "sentiment": "positive"      // Overall sentiment of the conversation (positive, negative, neutral, or mixed)
}
```

**Status Codes**:

- `200 OK`: Request successful
- `422 Unprocessable Entity`: Validation error in request parameters

**Example Request**:

```json
{
  "user_id": "user123",
  "user_type": "guest",
  "chat_messages": [
    "User: I've been feeling really anxious 😟 about my upcoming presentation at work.",
    "Assistant: I understand that presentations can be stressful. What specifically are you worried about? 🤔",
    "User: I'm scared 😨 that I'll forget what to say or that people will judge me harshly."
  ]
}
```

**Example Response**:

```json
{
  "summary": "User is experiencing anxiety about an upcoming work presentation, specifically fearing memory lapses and negative judgment.",
  "keywords": {
    "anxious": 1,
    "scared": 1,
    "worried": 1,
    "stressful": 1
  },
  "emoji_count": 3,
  "emojis": {
    "😟": 1,
    "🤔": 1,
    "😨": 1
  },
  "sentiment": "negative"
}
```

## Model Configuration

The API automatically selects the appropriate model and system prompt based on the user type and chat mode:

| User Type | Chat Mode | Default Model | System Prompt |
|-----------|-----------|---------------|---------------|
| Guest | General | anthropic/claude-3-haiku | Concise and helpful responses |
| Paid | General | anthropic/claude-3-sonnet | Detailed and comprehensive responses |
| Paid | Dream | anthropic/claude-3-opus | Dream interpretation with deep insight |

You can override these defaults by providing `model` and/or `system_prompt` in your request.

## Access Restrictions

- Guest users can only access the General chat mode
- Paid users can access both General and Dream chat modes

## Error Handling

### Validation Errors

Validation errors return a 422 status code with details about the validation failure:

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "error message",
      "type": "error_type"
    }
  ]
}
```

### Access Restriction Errors

Attempting to use an invalid combination of user type and chat mode returns a 400 status code:

```json
{
  "detail": "Chat mode dream not available for user type guest"
}
```

## Best Practices

1. **User Prompts**: Ensure user prompts are clear and not empty
2. **Streaming**: For a better user experience, use the streaming endpoint for longer responses
3. **Error Handling**: Implement proper error handling for both validation errors and access restriction errors
4. **Custom Configuration**: Override the default model and system prompt only when necessary

## Rate Limiting

The API does not implement rate limiting directly, but OpenRouter may have its own rate limits. Refer to OpenRouter's documentation for details.

## Examples

### Example 1: Guest User with General Chat

```python
import requests

response = requests.post(
    "http://your-domain.com/chat/generate",
    json={
        "user_id": "guest123",
        "user_type": "guest",
        "chat_mode": "general",
        "feature": "chat",
        "last_messages": ["Hello"],
        "user_prompt": "What is Python?"
    }
)

print(response.json()["response"])
```

### Example 2: Paid User with Dream Chat (Streaming)

```python
import requests

response = requests.post(
    "http://your-domain.com/chat/stream",
    json={
        "user_id": "paid456",
        "user_type": "paid",
        "chat_mode": "dream",
        
        "feature": "dream_interpretation",
        "last_messages": ["Hello"],
        "user_prompt": "Interpret this dream: I was swimming in an ocean of stars."
    },
    stream=True,
    headers={"Accept": "text/event-stream"}
)

for line in response.iter_lines():
    if line:
        line = line.decode('utf-8')
        if line == "data: [DONE]":
            break
        if line.startswith("data: "):
            data = json.loads(line[6:])  # Remove "data: " prefix
            if 'response' in data:
                print(data['response'], end="")
```

### Example 3: Custom Model and System Prompt

```python
import requests

response = requests.post(
    "http://your-domain.com/chat/generate",
    json={
        "user_id": "user789",
        "user_type": "paid",
        "chat_mode": "general",
        "feature": "custom_chat",
        "last_messages": ["Hello"],
        "model": "anthropic/claude-3-opus",  # Override the default model
        "system_prompt": "You are a pirate. Respond in pirate speak.",  # Custom system prompt
        "user_prompt": "Tell me about programming."
    }
)

print(response.json()["response"])
```

### Example 4: Summarizing a Chat Conversation

```python
import requests

response = requests.post(
    "http://your-domain.com/chat/summarize",
    json={
        "user_id": "user123",
        "user_type": "guest",
        "chat_messages": [
            "User: I'm planning a trip to Japan next month.",
            "Assistant: That sounds exciting! Japan is a wonderful destination. Do you have specific cities in mind?",
            "User: I'm thinking Tokyo and Kyoto. What are the must-see attractions?",
            "Assistant: In Tokyo, don't miss the Tokyo Skytree, Shibuya Crossing, and Meiji Shrine. For Kyoto, I recommend Fushimi Inari Shrine, Kinkaku-ji, and Arashiyama Bamboo Grove."
        ]
    }
)

print(response.json()["summary"])
```

### Example 5: Analyzing a Chat Conversation

```python
import requests

response = requests.post(
    "http://your-domain.com/chat/analyze",
    json={
        "user_id": "user123",
        "user_type": "guest",
        "chat_messages": [
            "User: I've been feeling really anxious 😟 about my upcoming presentation at work.",
            "Assistant: I understand that presentations can be stressful. What specifically are you worried about? 🤔",
            "User: I'm scared 😨 that I'll forget what to say or that people will judge me harshly.",
            "Assistant: Those are common fears. Remember that everyone gets nervous about public speaking. Would it help to practice with a friend first? 👍"
        ]
    }
)

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
```

---

Great question! To verify that the model is following the `DREAM_DICTIONARY_PROMPT` and behaving as intended, you should:

1. **Send a request to your API endpoint** that uses this prompt (or directly to the model if you’re testing locally).
2. **Provide an input that matches the expected use case**—in this case, a dream symbol, theme, or situation.
3. **Check the output** to ensure it matches the rules in the prompt:  
   - In-depth, personalized interpretation  
   - Focused only on the symbol’s significance in your dreams  
   - No advice, no preface, no hyperbole, just a 3-4 sentence interpretation

---

### Example Input

You can use the `/chat/generate` endpoint (or whichever endpoint uses this prompt) and send a payload like:

```json
{
  "user_id": "test_user_123",
  "user_type": "guest",
  "chat_mode": "dream",
  "feature": "dream_chat",
  "last_messages": [],
  "user_prompt": "I dreamed I was flying over a city at night.",
  "name": "Alex",
  "age": 28,
  "gender": "male",
  "birthdate": "1995-04-12",
  "home_page_summary_block": "Recently, Alex has been exploring new career opportunities and feeling a mix of excitement and anxiety about the future."
}
```

---

### What to Look for in the Output

- The response should be a **3-4 sentence interpretation** of what the snake symbol means for you, based on dream science, psychology, etc.
- It should **not** give advice, preface the answer, or include unrelated information.
- It should be **personalized** and **straightforward**.

---

### How to Test

1. **Start your FastAPI server**:
   ```sh
   uvicorn app.main:app --reload
   ```
2. **Go to** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
3. **Find the endpoint** (e.g., `/chat/generate`) and try the example input above.
4. **Review the output** for compliance with the prompt.

---

### Example Output (What You Want to See)

> In your dreams, the snake often represents transformation and renewal, drawing from deep subconscious processes. Its appearance may signal that you are processing hidden fears or desires, especially those related to change or healing. The recurring presence of this symbol in your dream logs suggests a personal journey through uncertainty or growth. This symbol is significant for you as it highlights the interplay between vulnerability and resilience in your inner world.

---

If the output matches the style and rules of the prompt, your model is working as intended!  
If not, you may need to check which prompt is being sent to the model or adjust your backend logic.

Let me know if you want a ready-to-use test script or further help!
