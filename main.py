import os
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

    # Save formatted markdown output to outputs directory
    # The output format follows the requirements specified in docs/requirements/debate-output.md
    output_dir = os.path.join(os.getcwd(), 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'debate_transcript.md')

    markdown_output = orchestrator.get_formatted_output('markdown')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_output)

    print(f"\nDebate transcript saved to {output_path}")


if __name__ == "__main__":
    main()
