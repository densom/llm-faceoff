"""Message processing system for handling debate communications."""

import re
from typing import Dict, List, Optional

from .types import DebateMessage, DebateSession, MessageType


class MessageProcessor:
    """Processes and validates debate messages."""

    def __init__(self):
        """Initialize message processor."""
        self.max_message_length = 5000
        self.min_message_length = 10

    def validate_message(self, message: DebateMessage, session: DebateSession) -> tuple[bool, Optional[str]]:
        """Validate a debate message."""
        if not message.content.strip():
            return False, "Message content cannot be empty"

        if len(message.content) > session.config.max_response_length:
            return False, f"Message exceeds maximum length of {session.config.max_response_length} characters"

        if len(message.content) < self.min_message_length:
            return False, f"Message must be at least {self.min_message_length} characters"

        if not self._is_appropriate_content(message.content):
            return False, "Message contains inappropriate content"

        return True, None

    def filter_message_content(self, content: str) -> str:
        """Filter and clean message content."""
        content = content.strip()
        content = self._remove_system_artifacts(content)
        content = self._normalize_whitespace(content)
        content = self._remove_markdown_artifacts(content)

        return content

    def extract_key_points(self, message: DebateMessage) -> List[str]:
        """Extract key points from a message."""
        content = message.content.lower()
        sentences = re.split(r'[.!?]+', content)

        key_indicators = [
            "first", "second", "third", "finally", "in conclusion",
            "however", "therefore", "furthermore", "moreover",
            "the main point", "key argument", "important to note",
        ]

        key_points = []
        for sentence in sentences:
            sentence = sentence.strip()
            if any(indicator in sentence for indicator in key_indicators):
                key_points.append(sentence.capitalize() + ".")

        return key_points[:5]

    def summarize_conversation(self, session: DebateSession, max_messages: int = 10) -> str:
        """Create a summary of recent conversation."""
        recent_messages = session.messages[-max_messages:]
        summary_parts = []

        for message in recent_messages:
            participant = self._get_participant_name(session, message.participant_id)
            message_type = message.message_type.value.replace('_', ' ').title()
            summary_parts.append(f"{participant} ({message_type}): {message.content[:100]}...")

        return "\\n".join(summary_parts)

    def check_conversation_coherence(self, session: DebateSession) -> Dict[str, any]:
        """Check if conversation is staying on topic and coherent."""
        if len(session.messages) < 2:
            return {"coherent": True, "score": 1.0, "issues": []}

        topic_keywords = self._extract_topic_keywords(session.config.topic)
        recent_messages = session.messages[-5:]

        topic_relevance_scores = []
        for message in recent_messages:
            if message.message_type != MessageType.MODERATOR_COMMENT:
                score = self._calculate_topic_relevance(message.content, topic_keywords)
                topic_relevance_scores.append(score)

        avg_relevance = sum(topic_relevance_scores) / len(topic_relevance_scores) if topic_relevance_scores else 0

        issues = []
        if avg_relevance < 0.3:
            issues.append("Conversation appears to be drifting off-topic")

        if self._detect_repetition(recent_messages):
            issues.append("Detected repetitive arguments")

        return {
            "coherent": len(issues) == 0,
            "topic_relevance_score": avg_relevance,
            "issues": issues,
        }

    def _is_appropriate_content(self, content: str) -> bool:
        """Check if content is appropriate for debate."""
        inappropriate_patterns = [
            r'\\b(hate|attack|destroy)\\b',
            r'\\b(stupid|idiot|moron)\\b',
            r'personal attacks?',
        ]

        for pattern in inappropriate_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return False

        return True

    def _remove_system_artifacts(self, content: str) -> str:
        """Remove system artifacts from content."""
        patterns = [
            r'^(Assistant|AI|System):\\s*',
            r'<\\|.*?\\|>',
            r'\\[SYSTEM\\].*?\\[/SYSTEM\\]',
        ]

        for pattern in patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.MULTILINE)

        return content

    def _normalize_whitespace(self, content: str) -> str:
        """Normalize whitespace in content."""
        content = re.sub(r'\\s+', ' ', content)
        content = re.sub(r'\\n\\s*\\n\\s*\\n+', '\\n\\n', content)
        return content.strip()

    def _remove_markdown_artifacts(self, content: str) -> str:
        """Remove problematic markdown artifacts."""
        patterns = [
            r'```[\\w]*\\n?',  # Code blocks
            r'#{1,6}\\s*',      # Headers
        ]

        for pattern in patterns:
            content = re.sub(pattern, '', content)

        return content

    def _extract_topic_keywords(self, topic: str) -> List[str]:
        """Extract keywords from debate topic."""
        stop_words = {'the', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}

        words = re.findall(r'\\b\\w+\\b', topic.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]

        return keywords

    def _calculate_topic_relevance(self, content: str, topic_keywords: List[str]) -> float:
        """Calculate how relevant message content is to the topic."""
        if not topic_keywords:
            return 1.0

        content_words = re.findall(r'\\b\\w+\\b', content.lower())
        matches = sum(1 for word in content_words if word in topic_keywords)

        return min(matches / len(topic_keywords), 1.0)

    def _detect_repetition(self, messages: List[DebateMessage]) -> bool:
        """Detect if recent messages are repetitive."""
        if len(messages) < 3:
            return False

        contents = [msg.content.lower() for msg in messages[-3:]]
        for i, content1 in enumerate(contents):
            for content2 in contents[i+1:]:
                similarity = self._calculate_similarity(content1, content2)
                if similarity > 0.7:
                    return True

        return False

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple similarity between two texts."""
        words1 = set(re.findall(r'\\b\\w+\\b', text1.lower()))
        words2 = set(re.findall(r'\\b\\w+\\b', text2.lower()))

        if not words1 or not words2:
            return 0.0

        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        return intersection / union if union > 0 else 0.0

    def _get_participant_name(self, session: DebateSession, participant_id: str) -> str:
        """Get participant name by ID."""
        for participant in session.participants:
            if str(participant.id) == str(participant_id):
                return participant.name or f"{participant.provider}-{participant.model}"
        return "Unknown"