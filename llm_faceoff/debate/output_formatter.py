import json
from datetime import datetime
from typing import Any, Dict, List, Optional


class DebateOutputFormatter:
    def __init__(self, session_data: Dict[str, Any]):
        self.session_data = session_data

    def to_markdown(self) -> str:
        raise NotImplementedError

    def to_json(self) -> str:
        raise NotImplementedError

    def to_html(self) -> str:
        raise NotImplementedError


class MarkdownFormatter(DebateOutputFormatter):
    def to_markdown(self) -> str:
        # Implement Markdown output formatting according to requirements
        md = []
        # Title Section
        md.append(f"# {self.session_data.get('config', {}).get('topic', 'Debate Topic')}\n")

        # Metadata table
        config = self.session_data.get('config', {})
        md.append("| Field | Value |")
        md.append("|---|---|")
        md.append(f"| Format | {config.get('format', '')} |")
        md.append(f"| Status | {self.session_data.get('status', '')} |")
        md.append(f"| Started At | {self.session_data.get('started_at', 'N/A')} |")
        md.append(f"| Completed At | {self.session_data.get('completed_at', 'N/A')} |\n")

        # Participants Section
        md.append("## Participants\n")
        participants = self.session_data.get('participants', [])
        role_emoji = {'proposition': '✅', 'opposition': '❌', 'moderator': '⚖️'}
        for p in participants:
            name = p.get('name')
            if not name or name.lower() == 'unnamed':
                name = f"{p.get('provider', '')}-{p.get('model', '')}"
            emoji = role_emoji.get(p.get('role', '').lower(), '')
            md.append(f"### {emoji} {name}")
            md.append(f"- Role: **{p.get('role', '')}**")
            md.append(f"- Provider: **{p.get('provider', '')}**")
            md.append(f"- Model: **{p.get('model', '')}**\n")

        # Rules Section
        rules = config.get('rules', {})
        if rules:
            md.append("## Rules\n")
            for key, value in rules.items():
                md.append(f"- **{key}**: {value}")
            md.append("")

        # Transcript Section
        md.append("## Transcript\n")
        messages = self.session_data.get('messages', [])
        turn_number = 1
        for msg in messages:
            participant = next((p for p in participants if p.get('id') == msg.get('participant_id')), None)
            if participant:
                name = participant.get('name')
                if not name or name.lower() == 'unnamed':
                    name = f"{participant.get('provider', '')}-{participant.get('model', '')}"
                role = participant.get('role', '')
            else:
                name = "Unknown"
                role = "unknown"

            timestamp = msg.get('timestamp', 'N/A')
            msg_type = msg.get('type', 'Message')
            content = msg.get('content', '')
            # Append terminal punctuation if missing
            if content and content[-1] not in '.!?':
                content += '.'

            md.append(f"### Turn {turn_number} - {msg_type}")
            md.append(f"**{name} ({role})** at *{timestamp}*:")
            md.append(content)
            md.append('---')
            turn_number += 1

        # Summary Section
        md.append("## Summary\n")
        stats = self.session_data.get('statistics', {})
        md.append("| Statistic | Value |")
        md.append("|---|---|")
        md.append(f"| Total Messages | {stats.get('total_messages', 0):,} |")
        md.append(f"| Total Participants | {stats.get('total_participants', 0):,} |")
        md.append(f"| Duration (minutes) | {stats.get('duration_minutes', 0):,} |")
        md.append(f"| Average Message Length | {stats.get('avg_message_length', 0):,} |")

        md.append("\n### Participant Performance Metrics")
        participant_stats = stats.get('participant_stats', {})
        for pid, pstats in participant_stats.items():
            participant = next((p for p in participants if p.get('id') == pid), None)
            if participant:
                name = participant.get('name')
                if not name or name.lower() == 'unnamed':
                    name = f"{participant.get('provider', '')}-{participant.get('model', '')}"
            else:
                name = "Unknown"

            md.append(f"- **{name}**")
            md.append(f"  - Message Count: {pstats.get('message_count', 0):,}")
            md.append(f"  - Total Characters: {pstats.get('total_characters', 0):,}")
            md.append(f"  - Average Characters: {pstats.get('avg_characters', 0):,}\n")

        md.append(f"*Generated on {datetime.utcnow().isoformat()} UTC*")

        return '\n'.join(md)


class JSONFormatter(DebateOutputFormatter):
    def to_json(self) -> str:
        # Implement JSON output formatting according to requirements
        return json.dumps(self.session_data, indent=2, ensure_ascii=False)


class HTMLFormatter(DebateOutputFormatter):
    def to_html(self) -> str:
        # Implement HTML output formatting according to requirements
        html = []
        html.append("<!DOCTYPE html>")
        html.append("<html lang=\"en\">")
        html.append("<head>")
        html.append("<meta charset=\"UTF-8\">")
        html.append("<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">")
        html.append(f"<title>{self.session_data.get('config', {}).get('topic', 'Debate Transcript')}</title>")
        # Basic embedded CSS for styling
        html.append("<style>")
        html.append("body { font-family: Arial, sans-serif; margin: 20px; padding: 0; background: #f9f9f9; color: #333; }")
        html.append("h1, h2, h3 { color: #2c3e50; }")
        html.append("table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }")
        html.append("th, td { border: 1px solid #ddd; padding: 8px; }")
        html.append("th { background-color: #3498db; color: white; }")
        html.append("tr:nth-child(even) { background-color: #f2f2f2; }")
        html.append(".role-proposition { color: green; font-weight: bold; }")
        html.append(".role-opposition { color: red; font-weight: bold; }")
        html.append(".role-moderator { color: orange; font-weight: bold; }")
        html.append(".message { border-bottom: 1px solid #ccc; padding: 10px 0; }")
        html.append(".timestamp { font-style: italic; color: #666; }")
        html.append("</style>")
        html.append("</head>")
        html.append("<body>")

        # Title Section
        html.append(f"<h1>{self.session_data.get('config', {}).get('topic', 'Debate Topic')}</h1>")

        # Metadata Table
        html.append("<table>")
        html.append("<tr><th>Field</th><th>Value</th></tr>")
        config = self.session_data.get('config', {})
        html.append(f"<tr><td>Format</td><td>{config.get('format', '')}</td></tr>")
        html.append(f"<tr><td>Status</td><td>{self.session_data.get('status', '')}</td></tr>")
        html.append(f"<tr><td>Started At</td><td>{self.session_data.get('started_at', 'N/A')}</td></tr>")
        html.append(f"<tr><td>Completed At</td><td>{self.session_data.get('completed_at', 'N/A')}</td></tr>")
        html.append("</table>")

        # Participants Section
        html.append("<h2>Participants</h2>")
        participants = self.session_data.get('participants', [])
        role_class = {'proposition': 'role-proposition', 'opposition': 'role-opposition', 'moderator': 'role-moderator'}
        for p in participants:
            name = p.get('name')
            if not name or name.lower() == 'unnamed':
                name = f"{p.get('provider', '')}-{p.get('model', '')}"
            role = p.get('role', '').lower()
            css_class = role_class.get(role, '')
            html.append(f"<h3 class='{css_class}'>{name}</h3>")
            html.append(f"<p>Role: <strong>{p.get('role', '')}</strong></p>")
            html.append(f"<p>Provider: <strong>{p.get('provider', '')}</strong></p>")
            html.append(f"<p>Model: <strong>{p.get('model', '')}</strong></p>")

        # Rules Section
        rules = config.get('rules', {})
        if rules:
            html.append("<h2>Rules</h2>")
            html.append("<ul>")
            for key, value in rules.items():
                html.append(f"<li><strong>{key}</strong>: {value}</li>")
            html.append("</ul>")

        # Transcript Section
        html.append("<h2>Transcript</h2>")
        messages = self.session_data.get('messages', [])
        for idx, msg in enumerate(messages, start=1):
            participant = next((p for p in participants if p.get('id') == msg.get('participant_id')), None)
            if participant:
                name = participant.get('name')
                if not name or name.lower() == 'unnamed':
                    name = f"{participant.get('provider', '')}-{participant.get('model', '')}"
                role = participant.get('role', '').lower()
            else:
                name = "Unknown"
                role = "unknown"

            html.append(f"<div class='message'>")
            html.append(f"<h3>Turn {idx} - {msg.get('type', 'Message')}</h3>")
            html.append(f"<p class='{role}'><strong>{name} ({role.capitalize()})</strong> <span class='timestamp'>at {msg.get('timestamp', 'N/A')}</span></p>")
            content = msg.get('content', '')
            # Escape HTML special characters
            content = (content.replace('&', '&amp;')
                              .replace('<', '&lt;')
                              .replace('>', '&gt;'))
            # Append terminal punctuation if missing
            if content and content[-1] not in '.!?':
                content += '.'
            html.append(f"<p>{content}</p>")
            html.append("</div>")

        # Summary Section
        html.append("<h2>Summary</h2>")
        stats = self.session_data.get('statistics', {})
        html.append("<table>")
        html.append("<tr><th>Statistic</th><th>Value</th></tr>")
        html.append(f"<tr><td>Total Messages</td><td>{stats.get('total_messages', 0):,}</td></tr>")
        html.append(f"<tr><td>Total Participants</td><td>{stats.get('total_participants', 0):,}</td></tr>")
        html.append(f"<tr><td>Duration (minutes)</td><td>{stats.get('duration_minutes', 0):,}</td></tr>")
        html.append(f"<tr><td>Average Message Length</td><td>{stats.get('avg_message_length', 0):,}</td></tr>")
        html.append("</table>")

        html.append("<h3>Participant Performance Metrics</h3>")
        participant_stats = stats.get('participant_stats', {})
        for pid, pstats in participant_stats.items():
            participant = next((p for p in participants if p.get('id') == pid), None)
            if participant:
                name = participant.get('name')
                if not name or name.lower() == 'unnamed':
                    name = f"{participant.get('provider', '')}-{participant.get('model', '')}"
            else:
                name = "Unknown"

            html.append(f"<p><strong>{name}</strong></p>")
            html.append(f"<ul>")
            html.append(f"<li>Message Count: {pstats.get('message_count', 0):,}</li>")
            html.append(f"<li>Total Characters: {pstats.get('total_characters', 0):,}</li>")
            html.append(f"<li>Average Characters: {pstats.get('avg_characters', 0):,}</li>")
            html.append(f"</ul>")

        html.append(f"<p><em>Generated on {datetime.utcnow().isoformat()} UTC</em></p>")

        html.append("</body>")
        html.append("</html>")

        return '\n'.join(html)