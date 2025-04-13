import requests
import json

api_key = "your-deepseek-api-key-here"
url = "https://api.deepseek.com/v1/chat/completions"  # This URL might vary based on DeepSeek's API

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "model": "deepseek-coder",  # Use the appropriate model name
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a short professional summary for a cybersecurity analyst."}
    ]
}

response = requests.post(url, headers=headers, data=json.dumps(data))
print(response.json())