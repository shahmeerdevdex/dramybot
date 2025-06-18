
import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import httpx
import json


app = FastAPI()


@app.get("/chat")
async def chat(question: str):
    async def generate():
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer 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",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "openai/gpt-4o",
            "messages": [
                {"role": "user", "content": question}
            ],
            "stream": True
        }

        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("POST", url, headers=headers, json=payload) as response:
                async for line in response.aiter_lines():
                    if line.strip() == "" or line.strip() == "data: [DONE]":
                        continue
                    if line.startswith("data: "):
                        try:
                            chunk = json.loads(line[len("data: "):])
                            content = chunk.get("choices", [{}])[0].get("delta", {}).get("content")
                            if content:
                                yield f"data: {json.dumps({
                                    'statusCode': 200,
                                    'message': 'fetch sucessfully',
                                    'data': { 'response': content }
                                })}\n\n"
                        except Exception as e:
                            continue

    return StreamingResponse(generate(), media_type="text/event-stream")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)