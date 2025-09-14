"""Main entry point for the LLM debate system."""

import asyncio

from llm_faceoff.cli import DebateCLI


def main():
    """Main entry point."""
    print("LLM Debate System")
    print("For interactive mode, use: python -m llm_faceoff.cli")
    print("For quick debate: python -m llm_faceoff.cli quick 'Your debate topic here'")


async def run_example_debate():
    """Run an example debate."""
    cli = DebateCLI()
    transcript_path = await cli.run_quick_debate(
        topic="Artificial intelligence will benefit humanity more than it harms it",
        format_name="oxford",
        max_turns=6
    )

    if transcript_path:
        print(f"\nDebate transcript saved to: {transcript_path}")
    else:
        print("\nDebate completed but transcript was not saved.")


if __name__ == "__main__":
    main()
    print("\\nRunning example debate...")
    asyncio.run(run_example_debate())
