import os
from dotenv import load_dotenv
from openai import OpenAI
from llm_faceoff.llms.adapter_interface import LLMAdapterInterface

load_dotenv()  # Load environment variables from .env file

class OpenAIAdapter(LLMAdapterInterface):
    def __init__(self):
        super().__init__(name="OpenAI")
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        self.client = OpenAI(api_key=self.api_key)

    def generate_response(self, topic: str, context: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a debater."},
                    {"role": "user", "content": f"Topic: {topic}\nContext: {context}"}
                ],
                max_tokens=300
            )
            content = response.choices[0].message.content
            return content.strip() if content else ""
        except Exception as e:
            return f"[OpenAI API error: {str(e)}]"