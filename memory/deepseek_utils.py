import os
import requests
import json

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

async def deepseek_chat_completion(messages: list, model: str = "deepseek-reasoner", stream: bool = False):
    if not DEEPSEEK_API_KEY:
        print("DeepSeek API key not set. Cannot make API call.")
        return None

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }

    payload = {
        "model": model,
        "messages": messages,
        "stream": stream
    }

    try:
        # Using requests.post for synchronous call, will need to be wrapped in run_in_executor for async FastAPI
        # For now, this is a placeholder for direct usage in async functions.
        response = requests.post(DEEPSEEK_API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling DeepSeek API: {e}")
        return None


