import os
from dotenv import load_dotenv
from llm_faceoff.llms.adapter_interface import LLMAdapterInterface

load_dotenv()  # Load environment variables from .env file

class OpenAIAdapter(LLMAdapterInterface):
    def __init__(self):
        super().__init__(name="OpenAI")
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

    def generate_response(self, topic: str, context: str) -> str:
        # TODO: Implement actual API call to OpenAI
        # Use self.api_key for authentication
        return f"[OpenAI response on '{topic}']"