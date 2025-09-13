from llm_faceoff.llms.adapter_interface import LLMAdapterInterface

class ClaudeAdapter(LLMAdapterInterface):
    def __init__(self):
        super().__init__(name="Claude")

    def generate_response(self, topic: str, context: str) -> str:
        # Placeholder implementation
        # TODO: Integrate with Claude API
        return f"[Claude response on '{topic}']"
