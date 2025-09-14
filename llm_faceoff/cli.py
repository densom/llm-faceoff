"""Command line interface for the LLM debate system."""

import asyncio
import json
import os
from pathlib import Path
from typing import List, Optional

import rich.console
import rich.table
from rich.console import Console
from rich.prompt import Confirm, Prompt

from .config import get_available_formats, get_format_description, settings
from .core import DebateConfig, DebateRole, DebateSession, Participant
from .core.debate_controller import BasicDebateController
from .core.message_processor import MessageProcessor
from .output import BasicTranscriptGenerator


class DebateCLI:
    """Command line interface for debates."""

    def __init__(self):
        """Initialize the CLI."""
        self.console = Console()
        self.controller = BasicDebateController()
        self.processor = MessageProcessor()
        self.transcript_generator = BasicTranscriptGenerator()

    async def run_interactive(self) -> None:
        """Run interactive debate setup."""
        self.console.print("[bold blue]🎯 LLM Debate System[/bold blue]", justify="center")
        self.console.print("Welcome to the LLM Debate System!", style="green")
        self.console.print()

        if not self._check_api_keys():
            return

        session = await self._setup_debate_session()
        if not session:
            return

        self.console.print(f"\\n[bold]Starting debate: {session.config.topic}[/bold]")
        await self._run_debate(session)

    async def run_quick_debate(
        self,
        topic: str,
        format_name: str = "oxford",
        max_turns: int = 6,
    ) -> Optional[str]:
        """Run a quick debate with default settings."""
        if not self._check_api_keys():
            return None

        session = self._create_default_session(topic, format_name, max_turns)
        self.console.print(f"[bold]Quick debate: {topic}[/bold]")

        await self._run_debate(session)
        return await self._save_transcript(session)

    def list_formats(self) -> None:
        """List available debate formats."""
        table = rich.table.Table(title="Available Debate Formats")
        table.add_column("Format", style="cyan")
        table.add_column("Description", style="magenta")

        for format_name in get_available_formats():
            description = get_format_description(format_name)
            table.add_row(format_name, description)

        self.console.print(table)

    def _check_api_keys(self) -> bool:
        """Check if required API keys are available."""
        api_status = settings.validate_api_keys()

        if not any(api_status.values()):
            self.console.print(
                "[bold red]Error: No API keys found![/bold red]\\n"
                "Please set OPENAI_API_KEY or CLAUDE_API_KEY in your environment.",
                style="red"
            )
            return False

        missing_keys = [provider for provider, available in api_status.items() if not available]
        if missing_keys:
            self.console.print(
                f"[yellow]Warning: Missing API keys for: {', '.join(missing_keys)}[/yellow]"
            )

        return True

    async def _setup_debate_session(self) -> Optional[DebateSession]:
        """Interactive debate session setup."""
        self.list_formats()
        self.console.print()

        format_name = Prompt.ask(
            "Select debate format",
            choices=get_available_formats(),
            default="oxford"
        )

        topic = Prompt.ask("Enter debate topic", default="Artificial intelligence will benefit humanity more than it harms it")

        max_turns = int(Prompt.ask("Maximum turns", default="8"))

        participants = await self._setup_participants()
        if len(participants) < 2:
            self.console.print("[red]Need at least 2 participants for a debate.[/red]")
            return None

        config = DebateConfig(
            topic=topic,
            format=format_name,
            max_turns=max_turns,
            max_response_length=settings.default_max_response_length,
        )

        session = DebateSession(config=config, participants=participants)
        return session

    async def _setup_participants(self) -> List[Participant]:
        """Setup debate participants."""
        participants = []
        available_providers = ["openai", "anthropic"]
        available_models = {
            "openai": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            "anthropic": ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"]
        }

        self.console.print("\\n[bold]Setting up participants:[/bold]")

        for i in range(2):
            role = DebateRole.PROPOSITION if i == 0 else DebateRole.OPPOSITION
            role_name = "Proposition (FOR)" if i == 0 else "Opposition (AGAINST)"

            self.console.print(f"\\n[cyan]Participant {i+1} - {role_name}:[/cyan]")

            provider = Prompt.ask(
                "Provider",
                choices=available_providers,
                default=available_providers[i % len(available_providers)]
            )

            models = available_models.get(provider, [])
            model = Prompt.ask(
                "Model",
                choices=models,
                default=models[0] if models else ""
            )

            name = Prompt.ask("Name (optional)", default=f"{provider.title()}-{role.value}")

            participant = Participant(
                name=name,
                provider=provider,
                model=model,
                role=role,
            )

            participants.append(participant)

        return participants

    def _create_default_session(self, topic: str, format_name: str, max_turns: int) -> DebateSession:
        """Create a debate session with default participants."""
        config = DebateConfig(
            topic=topic,
            format=format_name,
            max_turns=max_turns,
            max_response_length=settings.default_max_response_length,
        )

        participants = [
            Participant(
                name="GPT-4 (Proposition)",
                provider="openai",
                model="gpt-4",
                role=DebateRole.PROPOSITION,
            ),
            Participant(
                name="Claude (Opposition)",
                provider="anthropic",
                model="claude-3-5-sonnet-20241022",
                role=DebateRole.OPPOSITION,
            ),
        ]

        return DebateSession(config=config, participants=participants)

    async def _run_debate(self, session: DebateSession) -> None:
        """Run the actual debate."""
        try:
            await self.controller.start_debate(session)

            while session.status.value == "in_progress" and session.current_turn <= session.config.max_turns:
                current_participant = self.controller.get_current_participant(session)
                if not current_participant:
                    break

                self.console.print(f"\\n[bold cyan]Turn {session.current_turn} - {current_participant.name}[/bold cyan]")

                message = await self.controller.process_turn(session)

                self.console.print(f"[dim]{current_participant.name}:[/dim]")
                self.console.print(message.content)
                self.console.print("[dim]" + "="*50 + "[/dim]")

            await self.controller.end_debate(session)
            self.console.print("\\n[bold green]Debate completed![/bold green]")

        except Exception as e:
            self.console.print(f"[bold red]Error during debate: {str(e)}[/bold red]")

    async def _save_transcript(self, session: DebateSession) -> Optional[str]:
        """Save debate transcript."""
        if not settings.save_transcripts:
            return None

        output_dir = Path(settings.output_directory)
        output_dir.mkdir(exist_ok=True)

        timestamp = session.created_at.strftime("%Y%m%d_%H%M%S")
        topic_slug = "".join(c if c.isalnum() else "_" for c in session.config.topic[:50])
        base_filename = f"debate_{timestamp}_{topic_slug}"

        saved_files = []

        if settings.transcript_format in ("markdown", "all"):
            markdown_content = self.transcript_generator.generate_markdown(session)
            markdown_file = output_dir / f"{base_filename}.md"
            markdown_file.write_text(markdown_content, encoding="utf-8")
            saved_files.append(str(markdown_file))

        if settings.transcript_format in ("json", "all"):
            json_content = self.transcript_generator.generate_json(session)
            json_file = output_dir / f"{base_filename}.json"
            json_file.write_text(json.dumps(json_content, indent=2), encoding="utf-8")
            saved_files.append(str(json_file))

        if settings.transcript_format in ("html", "all"):
            html_content = self.transcript_generator.generate_html(session)
            html_file = output_dir / f"{base_filename}.html"
            html_file.write_text(html_content, encoding="utf-8")
            saved_files.append(str(html_file))

        if saved_files:
            self.console.print(f"\\n[green]Transcripts saved:[/green]")
            for file_path in saved_files:
                self.console.print(f"  📄 {file_path}")
            return saved_files[0]

        return None


async def main():
    """Main CLI entry point."""
    import sys

    cli = DebateCLI()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "formats":
            cli.list_formats()
        elif command == "quick" and len(sys.argv) > 2:
            topic = " ".join(sys.argv[2:])
            await cli.run_quick_debate(topic)
        else:
            print("Usage:")
            print("  python -m llm_faceoff.cli                 # Interactive mode")
            print("  python -m llm_faceoff.cli formats         # List debate formats")
            print("  python -m llm_faceoff.cli quick <topic>   # Quick debate")
    else:
        await cli.run_interactive()


if __name__ == "__main__":
    asyncio.run(main())