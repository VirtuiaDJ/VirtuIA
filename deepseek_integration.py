import requests
import os
from dotenv import load_dotenv

load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-5219276b9cf743c5abc9d7148d31ae71")

def consulta_deepseek(mensagem):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Responda de forma objetiva, clara e em português."},
            {"role": "user", "content": mensagem}
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            return f"[DeepSeek Erro {response.status_code}]"
    except Exception as e:
        return f"[DeepSeek Exceção: {e}]"