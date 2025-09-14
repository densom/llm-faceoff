"""Transcript generation for debate sessions."""

import json
from datetime import datetime
from typing import Any, Dict

from ..core.types import DebateSession, MessageType


class BasicTranscriptGenerator:
    """Basic implementation of transcript generator."""

    def generate_markdown(self, session: DebateSession) -> str:
        """Generate a markdown transcript."""
        lines = []

        lines.append(f"# Debate Transcript: {session.config.topic}")
        lines.append(f"**Format:** {session.config.format}")
        lines.append(f"**Started:** {session.started_at.strftime('%Y-%m-%d %H:%M:%S') if session.started_at else 'N/A'}")
        lines.append(f"**Status:** {session.status.value}")
        lines.append("")

        lines.append("## Participants")
        for i, participant in enumerate(session.participants, 1):
            role_display = participant.role.value.replace('_', ' ').title()
            lines.append(f"{i}. **{participant.name or 'Unnamed'}** ({participant.provider} {participant.model}) - {role_display}")
        lines.append("")

        lines.append("## Debate Transcript")
        lines.append("")

        for i, message in enumerate(session.messages, 1):
            participant = self._get_participant_by_id(session, message.participant_id)
            participant_name = participant.name if participant else "System"
            provider_info = f"({participant.provider} {participant.model})" if participant else ""

            message_type = message.message_type.value.replace('_', ' ').title()
            timestamp = message.timestamp.strftime('%H:%M:%S')

            lines.append(f"### Turn {i} - {participant_name} {provider_info}")
            lines.append(f"**Type:** {message_type} | **Time:** {timestamp}")
            lines.append("")
            lines.append(message.content)
            lines.append("")
            lines.append("---")
            lines.append("")

        self._add_session_summary(lines, session)

        return "\\n".join(lines)

    def generate_json(self, session: DebateSession) -> Dict[str, Any]:
        """Generate a JSON transcript."""
        data = {
            "session_id": str(session.id),
            "config": {
                "topic": session.config.topic,
                "format": session.config.format,
                "max_turns": session.config.max_turns,
                "max_response_length": session.config.max_response_length,
                "rules": session.config.rules,
            },
            "participants": [
                {
                    "id": str(p.id),
                    "name": p.name,
                    "provider": p.provider,
                    "model": p.model,
                    "role": p.role.value,
                }
                for p in session.participants
            ],
            "status": session.status.value,
            "created_at": session.created_at.isoformat(),
            "started_at": session.started_at.isoformat() if session.started_at else None,
            "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            "current_turn": session.current_turn,
            "messages": [
                {
                    "id": str(m.id),
                    "participant_id": str(m.participant_id),
                    "content": m.content,
                    "type": m.message_type.value,
                    "timestamp": m.timestamp.isoformat(),
                    "metadata": m.metadata,
                }
                for m in session.messages
            ],
            "statistics": self._generate_statistics(session),
        }

        return data

    def generate_html(self, session: DebateSession) -> str:
        """Generate an HTML transcript."""
        html_parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<meta charset='UTF-8'>",
            f"<title>Debate: {session.config.topic}</title>",
            "<style>",
            self._get_html_styles(),
            "</style>",
            "</head>",
            "<body>",
            "<div class='container'>",
        ]

        html_parts.extend([
            f"<h1>Debate Transcript: {session.config.topic}</h1>",
            "<div class='metadata'>",
            f"<p><strong>Format:</strong> {session.config.format}</p>",
            f"<p><strong>Started:</strong> {session.started_at.strftime('%Y-%m-%d %H:%M:%S') if session.started_at else 'N/A'}</p>",
            f"<p><strong>Status:</strong> {session.status.value}</p>",
            "</div>",
        ])

        html_parts.append("<h2>Participants</h2>")
        html_parts.append("<div class='participants'>")
        for participant in session.participants:
            role_display = participant.role.value.replace('_', ' ').title()
            html_parts.append(
                f"<div class='participant'>"
                f"<strong>{participant.name or 'Unnamed'}</strong> "
                f"({participant.provider} {participant.model}) - {role_display}"
                f"</div>"
            )
        html_parts.append("</div>")

        html_parts.append("<h2>Transcript</h2>")
        html_parts.append("<div class='messages'>")

        for message in session.messages:
            participant = self._get_participant_by_id(session, message.participant_id)
            participant_name = participant.name if participant else "System"

            message_type = message.message_type.value.replace('_', ' ').title()
            timestamp = message.timestamp.strftime('%H:%M:%S')

            role_class = participant.role.value if participant else "system"

            html_parts.extend([
                f"<div class='message {role_class}'>",
                "<div class='message-header'>",
                f"<span class='participant-name'>{participant_name}</span>",
                f"<span class='message-type'>{message_type}</span>",
                f"<span class='timestamp'>{timestamp}</span>",
                "</div>",
                f"<div class='message-content'>{self._format_html_content(message.content)}</div>",
                "</div>",
            ])

        html_parts.extend([
            "</div>",
            self._generate_html_statistics(session),
            "</div>",
            "</body>",
            "</html>",
        ])

        return "\\n".join(html_parts)

    def _get_participant_by_id(self, session: DebateSession, participant_id: str) -> Any:
        """Get participant by ID."""
        for participant in session.participants:
            if str(participant.id) == str(participant_id):
                return participant
        return None

    def _add_session_summary(self, lines: list[str], session: DebateSession) -> None:
        """Add session summary to markdown."""
        stats = self._generate_statistics(session)

        lines.append("## Session Summary")
        lines.append("")
        lines.append(f"- **Total Messages:** {stats['total_messages']}")
        lines.append(f"- **Duration:** {stats['duration_minutes']:.1f} minutes")
        lines.append(f"- **Average Message Length:** {stats['avg_message_length']:.0f} characters")
        lines.append("")

        if stats['participant_stats']:
            lines.append("### Participant Statistics")
            for participant_name, pstats in stats['participant_stats'].items():
                lines.append(f"- **{participant_name}:** {pstats['message_count']} messages, {pstats['total_chars']} characters")
        lines.append("")

    def _generate_statistics(self, session: DebateSession) -> Dict[str, Any]:
        """Generate session statistics."""
        stats = {
            "total_messages": len(session.messages),
            "total_participants": len(session.participants),
            "duration_minutes": 0.0,
            "avg_message_length": 0.0,
            "participant_stats": {},
        }

        if session.started_at and session.completed_at:
            duration = session.completed_at - session.started_at
            stats["duration_minutes"] = duration.total_seconds() / 60

        if session.messages:
            total_chars = sum(len(msg.content) for msg in session.messages)
            stats["avg_message_length"] = total_chars / len(session.messages)

            for participant in session.participants:
                participant_messages = [msg for msg in session.messages if str(msg.participant_id) == str(participant.id)]
                participant_name = participant.name or f"{participant.provider}-{participant.model}"

                stats["participant_stats"][participant_name] = {
                    "message_count": len(participant_messages),
                    "total_chars": sum(len(msg.content) for msg in participant_messages),
                    "avg_chars": sum(len(msg.content) for msg in participant_messages) / len(participant_messages) if participant_messages else 0,
                }

        return stats

    def _get_html_styles(self) -> str:
        """Get CSS styles for HTML transcript."""
        return """
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
        .container { background: white; }
        h1 { color: #333; border-bottom: 2px solid #007acc; }
        h2 { color: #555; margin-top: 30px; }
        .metadata { background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .participants { margin: 15px 0; }
        .participant { padding: 8px; margin: 5px 0; background: #e8f4fd; border-radius: 3px; }
        .messages { margin: 20px 0; }
        .message { margin: 20px 0; padding: 15px; border-radius: 8px; border-left: 4px solid #ccc; }
        .message.proposition { border-left-color: #007acc; background: #f0f8ff; }
        .message.opposition { border-left-color: #ff6b35; background: #fff5f5; }
        .message.moderator { border-left-color: #28a745; background: #f0fff4; }
        .message-header { display: flex; justify-content: space-between; margin-bottom: 10px; font-weight: bold; }
        .participant-name { color: #333; }
        .message-type { color: #666; font-style: italic; }
        .timestamp { color: #999; font-size: 0.9em; }
        .message-content { line-height: 1.6; white-space: pre-wrap; }
        .statistics { background: #f8f9fa; padding: 20px; border-radius: 5px; margin-top: 30px; }
        """

    def _format_html_content(self, content: str) -> str:
        """Format content for HTML display."""
        import html
        return html.escape(content)

    def _generate_html_statistics(self, session: DebateSession) -> str:
        """Generate HTML statistics section."""
        stats = self._generate_statistics(session)

        html_parts = [
            "<div class='statistics'>",
            "<h3>Session Statistics</h3>",
            f"<p><strong>Total Messages:</strong> {stats['total_messages']}</p>",
            f"<p><strong>Duration:</strong> {stats['duration_minutes']:.1f} minutes</p>",
            f"<p><strong>Average Message Length:</strong> {stats['avg_message_length']:.0f} characters</p>",
        ]

        if stats['participant_stats']:
            html_parts.append("<h4>Participant Statistics</h4>")
            for participant_name, pstats in stats['participant_stats'].items():
                html_parts.append(
                    f"<p><strong>{participant_name}:</strong> "
                    f"{pstats['message_count']} messages, "
                    f"{pstats['total_chars']} characters</p>"
                )

        html_parts.append("</div>")
        return "\\n".join(html_parts)