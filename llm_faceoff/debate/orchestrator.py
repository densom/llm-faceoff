from typing import List, Dict, Any
from llm_faceoff.llms.adapter_interface import LLMAdapterInterface
from llm_faceoff.config import ConfigManager

class DebateOrchestrator:
    def __init__(self, llm_adapters: List[LLMAdapterInterface], config: ConfigManager):
        self.llm_adapters = llm_adapters
        self.config = config
        self.transcript = []
        self.current_turn = 0

    def start_debate(self, topic: str):
        self.transcript.append(f"Debate started on topic: {topic}")
        rounds = self.config.get('rounds', 3)

        for round_number in range(rounds):
            for adapter in self.llm_adapters:
                context = self._get_context()
                response = adapter.generate_response(topic, context)
                self.transcript.append(f"{adapter.name} (Round {round_number + 1}): {response}")

        self.transcript.append("Debate ended.")

    def _get_context(self) -> str:
        return '\n'.join(self.transcript)

    def get_transcript(self) -> List[str]:
        return self.transcript
