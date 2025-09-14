"""Demonstration script for the LLM Debate System."""

import asyncio
from llm_faceoff.cli import DebateCLI
from llm_faceoff.config import get_available_formats


async def demo():
    """Run a demonstration of the system."""
    print("LLM Debate System Demonstration")
    print("="*50)

    cli = DebateCLI()

    print("\\nAvailable debate formats:")
    cli.list_formats()

    print("\\n" + "="*50)
    print("The system is ready to run debates!")
    print("\\nTo use the system:")
    print("1. Set your API keys in .env file (copy from .env.example)")
    print("2. Run: python -m llm_faceoff.cli")
    print("3. Or run quick debate: python -m llm_faceoff.cli quick 'Your topic'")

    print("\\nExample commands:")
    print("  python -m llm_faceoff.cli formats")
    print("  python -m llm_faceoff.cli quick 'Should AI be regulated?'")
    print("  python main.py  # For interactive setup")


if __name__ == "__main__":
    asyncio.run(demo())