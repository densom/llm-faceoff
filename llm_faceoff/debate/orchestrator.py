from typing import List
from llm_faceoff.llms.adapter_interface import LLMAdapterInterface
from llm_faceoff.config import ConfigManager
from llm_faceoff.debate.logger import DebateLogger

class DebateOrchestrator:
    def __init__(self, llm_adapters: List[LLMAdapterInterface], config: ConfigManager):
        self.llm_adapters = llm_adapters
        self.config = config
        self.logger = DebateLogger()
        self.current_turn = 0

    def start_debate(self, topic: str):
        self.logger.log(f"Debate started on topic: {topic}")
        rounds = self.config.get('rounds', 3)

        # Opening statements
        for adapter in self.llm_adapters:
            response = adapter.generate_response(topic, '')
            self.logger.log(f"{adapter.name} (Opening): {response}")

        # Rebuttal rounds
        for round_number in range(1, rounds):
            for adapter in self.llm_adapters:
                context = self.logger.get_transcript()
                context_str = '\n'.join(context)
                response = adapter.generate_response(topic, context_str)
                self.logger.log(f"{adapter.name} (Rebuttal Round {round_number}): {response}")

        # Closing statements
        for adapter in self.llm_adapters:
            context = self.logger.get_transcript()
            context_str = '\n'.join(context)
            response = adapter.generate_response(topic, context_str)
            self.logger.log(f"{adapter.name} (Closing): {response}")

        self.logger.log("Debate ended.")

    def get_transcript(self) -> List[str]:
        return self.logger.get_transcript()
