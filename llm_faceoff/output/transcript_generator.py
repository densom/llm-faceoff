"""Transcript generation for debate sessions."""

import json
from datetime import datetime
from typing import Any, Dict

from ..core.types import DebateSession, MessageType


class BasicTranscriptGenerator:
    """Basic implementation of transcript generator."""

    def generate_markdown(self, session: DebateSession) -> str:
        """Generate a well-organized markdown transcript."""
        lines = []

        # Header with clean title and key metadata
        lines.append(f"# 🎯 {session.config.topic}")
        lines.append("")
        lines.append("## 📋 Debate Information")
        lines.append("")
        lines.append(f"| Field | Value |")
        lines.append(f"|-------|-------|")
        lines.append(f"| **Format** | {session.config.format.title()} |")
        lines.append(f"| **Status** | {session.status.value.title().replace('_', ' ')} |")
        lines.append(f"| **Started** | {session.started_at.strftime('%Y-%m-%d at %H:%M:%S') if session.started_at else 'Not started'} |")
        if session.completed_at:
            lines.append(f"| **Completed** | {session.completed_at.strftime('%Y-%m-%d at %H:%M:%S')} |")
        lines.append(f"| **Max Turns** | {session.config.max_turns} |")
        lines.append(f"| **Turn Limit** | {session.config.max_response_length} characters |")
        lines.append("")

        # Participants with role-specific formatting
        lines.append("## 👥 Participants")
        lines.append("")

        for participant in session.participants:
            role_display = participant.role.value.replace('_', ' ').title()
            role_emoji = self._get_role_emoji(participant.role)
            participant_name = participant.name or f"{participant.provider.title()}-{participant.model}"

            lines.append(f"### {role_emoji} {participant_name}")
            lines.append(f"- **Role:** {role_display}")
            lines.append(f"- **Provider:** {participant.provider.title()}")
            lines.append(f"- **Model:** {participant.model}")
            lines.append("")

        # Rules if any
        if session.config.rules:
            lines.append("## 📜 Debate Rules")
            lines.append("")
            for rule_key, rule_value in session.config.rules.items():
                lines.append(f"- **{rule_key.replace('_', ' ').title()}:** {rule_value}")
            lines.append("")

        # Main transcript with improved formatting
        lines.append("## 💬 Debate Transcript")
        lines.append("")

        if not session.messages:
            lines.append("*No messages yet - debate has not begun.*")
            lines.append("")
        else:
            for i, message in enumerate(session.messages, 1):
                participant = self._get_participant_by_id(session, message.participant_id)
                participant_name = participant.name if participant else "System"
                if not participant_name or participant_name == "Unnamed":
                    participant_name = f"{participant.provider.title()}-{participant.model}" if participant else "System"

                message_type = message.message_type.value.replace('_', ' ').title()
                timestamp = message.timestamp.strftime('%H:%M:%S')

                # Role-specific formatting
                role_emoji = self._get_role_emoji(participant.role) if participant else "🤖"

                lines.append(f"### Turn {i}: {role_emoji} {participant_name}")
                lines.append("")
                lines.append(f"**{message_type}** • ⏰ {timestamp}")
                lines.append("")

                # Format the message content with proper line breaks and structure
                formatted_content = self._format_message_content(message.content)
                lines.append(formatted_content)
                lines.append("")

                # Add separator between messages (except for the last one)
                if i < len(session.messages):
                    lines.append("---")
                    lines.append("")

        # Summary with enhanced statistics
        self._add_enhanced_session_summary(lines, session)

        return "\n".join(lines)

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

    def _get_role_emoji(self, role: Any) -> str:
        """Get emoji for participant role."""
        if hasattr(role, 'value'):
            role_value = role.value
        else:
            role_value = str(role).lower()

        role_emojis = {
            'proposition': '✅',
            'opposition': '❌',
            'moderator': '⚖️'
        }
        return role_emojis.get(role_value, '🎭')

    def _format_message_content(self, content: str) -> str:
        """Format message content for better readability."""
        if not content:
            return "*[No content]*"

        # Clean up the content
        formatted = content.strip()

        # Add proper paragraph breaks for very long content
        if len(formatted) > 500:
            # Split on double newlines and rejoin with proper markdown spacing
            paragraphs = [p.strip() for p in formatted.split('\n\n') if p.strip()]
            if len(paragraphs) > 1:
                formatted = '\n\n'.join(paragraphs)

        # Ensure content ends cleanly
        if not formatted.endswith('.') and not formatted.endswith('!') and not formatted.endswith('?'):
            formatted = formatted.rstrip() + '.'

        return formatted

    def _add_enhanced_session_summary(self, lines: list[str], session: DebateSession) -> None:
        """Add enhanced session summary to markdown."""
        stats = self._generate_statistics(session)

        lines.append("## 📊 Session Summary")
        lines.append("")

        # Overview statistics table
        lines.append("### Overview")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| **Total Messages** | {stats['total_messages']} |")
        lines.append(f"| **Total Participants** | {stats['total_participants']} |")
        lines.append(f"| **Duration** | {stats['duration_minutes']:.1f} minutes |")
        lines.append(f"| **Avg Message Length** | {stats['avg_message_length']:.0f} characters |")
        lines.append("")

        # Participant statistics
        if stats['participant_stats']:
            lines.append("### 👤 Participant Performance")
            lines.append("")

            for participant_name, pstats in stats['participant_stats'].items():
                # Find the participant to get their role
                participant_role = None
                for p in session.participants:
                    p_name = p.name or f"{p.provider.title()}-{p.model}"
                    if p_name == participant_name:
                        participant_role = p.role
                        break

                role_emoji = self._get_role_emoji(participant_role) if participant_role else "🎭"

                lines.append(f"#### {role_emoji} {participant_name}")
                lines.append("")
                lines.append("| Metric | Value |")
                lines.append("|--------|-------|")
                lines.append(f"| **Messages** | {pstats['message_count']} |")
                lines.append(f"| **Total Characters** | {pstats['total_chars']:,} |")
                lines.append(f"| **Avg Characters** | {pstats['avg_chars']:.0f} |")
                lines.append("")

        # Completion status
        if session.status.value == 'completed':
            lines.append("### ✅ Debate Complete")
            lines.append("")
            lines.append("This debate has concluded successfully.")
        elif session.status.value == 'in_progress':
            lines.append("### ⏳ Debate In Progress")
            lines.append("")
            lines.append(f"Current turn: {session.current_turn + 1}")
        elif session.status.value == 'aborted':
            lines.append("### ❌ Debate Aborted")
            lines.append("")
            lines.append("This debate was terminated before completion.")

        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}*")

    def _add_session_summary(self, lines: list[str], session: DebateSession) -> None:
        """Add session summary to markdown (legacy method for compatibility)."""
        self._add_enhanced_session_summary(lines, session)

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