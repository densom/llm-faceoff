from llm_faceoff.llms.openai_adapter import OpenAIAdapter
from llm_faceoff.llms.claude_adapter import ClaudeAdapter
from llm_faceoff.debate.orchestrator import DebateOrchestrator
from llm_faceoff.config import ConfigManager


def main():
    print("Hello from llm-faceoff!")

    openai_adapter = OpenAIAdapter()
    claude_adapter = ClaudeAdapter()
    config = ConfigManager({'rounds': 3})

    orchestrator = DebateOrchestrator([openai_adapter, claude_adapter], config)
    topic = "Is AI beneficial to society?"
    orchestrator.start_debate(topic)

    transcript = orchestrator.get_transcript()
    print("\nDebate Transcript:")
    for line in transcript:
        print(line)


if __name__ == "__main__":
    main()
