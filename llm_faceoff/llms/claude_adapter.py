import os
from dotenv import load_dotenv
import requests
from llm_faceoff.llms.adapter_interface import LLMAdapterInterface

load_dotenv()  # Load environment variables from .env file

class ClaudeAdapter(LLMAdapterInterface):
    def __init__(self):
        super().__init__(name="Claude")
        self.api_key = os.getenv('CLAUDE_API_KEY')
        if not self.api_key:
            raise ValueError("CLAUDE_API_KEY environment variable not set")
        self.api_url = "https://api.anthropic.com/v1/chat/completions"
        self.api_version = "2023-06-01"  # Required API version header

    def generate_response(self, topic: str, context: str) -> str:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": self.api_version,
            "Content-Type": "application/json"
        }

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Topic: {topic}\nContext: {context}"}
        ]

        data = {
            "model": "claude-sonnet-4-0",
            "messages": messages,
            "max_tokens_to_sample": 300
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result['completion'] if 'completion' in result else result.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
        except requests.exceptions.HTTPError as e:
            return f"[Claude API error: {response.status_code} {response.text}]"
        except Exception as e:
            return f"[Claude API error: {str(e)}]"
