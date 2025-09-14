import unittest
from unittest.mock import MagicMock
from llm_faceoff.debate.orchestrator import DebateOrchestrator
from llm_faceoff.config import ConfigManager
from llm_faceoff.llms.adapter_interface import LLMAdapterInterface
from typing import Optional, List, Dict, Any

# Mock adapters to replace missing CopilotAdapter and ClaudeAdapter
class MockAdapter(LLMAdapterInterface):
    def __init__(self, name: str):
        super().__init__(name)

    def generate_response(self, topic: str, context: str) -> str:
        return f"Response from {self.name} on topic {topic}"

# Extend DebateOrchestrator to add session data attributes for testing with explicit typing
class TestableDebateOrchestrator(DebateOrchestrator):
    def __init__(self, llm_adapters, config):
        super().__init__(llm_adapters, config)
        self.session_id: Optional[str] = None
        self.participants: List[Dict[str, Any]] = []
        self.status: Optional[str] = None
        self.created_at: Optional[str] = None
        self.started_at: Optional[str] = None
        self.completed_at: Optional[str] = None
        self.current_turn: int = 0
        self.messages: List[Dict[str, Any]] = []
        self.statistics: Dict[str, Any] = {}

class TestDebateOrchestrator(unittest.TestCase):
    def setUp(self):
        self.copilot = MockAdapter('Microsoft Copilot')
        self.claude = MockAdapter('Claude')
        self.config = ConfigManager({'rounds': 3})
        self.orchestrator = TestableDebateOrchestrator([self.copilot, self.claude], self.config)

    def test_debate_flow(self):
        topic = "Is AI beneficial to society?"
        self.orchestrator.start_debate(topic)
        transcript = self.orchestrator.get_transcript()

        self.assertIn(f"Debate started on topic: {topic}", transcript[0])
        self.assertIn("Debate ended.", transcript[-1])

        copilot_opening = any("Microsoft Copilot (Opening):" in line for line in transcript)
        claude_opening = any("Claude (Opening):" in line for line in transcript)
        copilot_rebuttal = any("Microsoft Copilot (Rebuttal Round" in line for line in transcript)
        claude_rebuttal = any("Claude (Rebuttal Round" in line for line in transcript)
        copilot_closing = any("Microsoft Copilot (Closing):" in line for line in transcript)
        claude_closing = any("Claude (Closing):" in line for line in transcript)

        self.assertTrue(copilot_opening)
        self.assertTrue(claude_opening)
        self.assertTrue(copilot_rebuttal)
        self.assertTrue(claude_rebuttal)
        self.assertTrue(copilot_closing)
        self.assertTrue(claude_closing)

class TestDebateOutputFormatting(unittest.TestCase):
    def setUp(self):
        test_adapter = MockAdapter('TestAdapter')
        test_config = ConfigManager({
            'topic': 'Test Topic',
            'format': 'standard',
            'rules': {'max_turns': 5}
        })
        self.orchestrator = TestableDebateOrchestrator([test_adapter], test_config)

        self.orchestrator.session_id = 'test-session'
        self.orchestrator.participants = [
            {'id': 'p1', 'name': 'Alice', 'provider': 'ProviderA', 'model': 'ModelX', 'role': 'proposition'},
            {'id': 'p2', 'name': 'Bob', 'provider': 'ProviderB', 'model': 'ModelY', 'role': 'opposition'},
            {'id': 'mod', 'name': 'Mod', 'provider': 'ProviderM', 'model': 'ModelZ', 'role': 'moderator'},
        ]
        self.orchestrator.status = 'active'
        self.orchestrator.created_at = '2025-09-14T00:00:00Z'
        self.orchestrator.started_at = '2025-09-14T01:00:00Z'
        self.orchestrator.completed_at = None
        self.orchestrator.current_turn = 3
        self.orchestrator.messages = [
            {'id': 'm1', 'participant_id': 'p1', 'content': 'Opening statement by Alice', 'type': 'Opening Statement', 'timestamp': '2025-09-14T01:01:00Z', 'metadata': {}},
            {'id': 'm2', 'participant_id': 'p2', 'content': 'Opening statement by Bob', 'type': 'Opening Statement', 'timestamp': '2025-09-14T01:02:00Z', 'metadata': {}},
            {'id': 'm3', 'participant_id': 'mod', 'content': 'Moderator comment', 'type': 'Moderator Comment', 'timestamp': '2025-09-14T01:03:00Z', 'metadata': {}},
        ]
        self.orchestrator.statistics = {
            'total_messages': 3,
            'total_participants': 3,
            'duration_minutes': 10,
            'avg_message_length': 25,
            'participant_stats': {
                'p1': {'message_count': 1, 'total_characters': 25, 'avg_characters': 25},
                'p2': {'message_count': 1, 'total_characters': 25, 'avg_characters': 25},
                'mod': {'message_count': 1, 'total_characters': 17, 'avg_characters': 17},
            }
        }

    def test_markdown_output(self):
        output = self.orchestrator.get_formatted_output('markdown')
        self.assertIn('# Test Topic', output)
        self.assertIn('## Participants', output)
        self.assertIn('### ✅ Alice', output)
        self.assertIn('### ❌ Bob', output)
        self.assertIn('### ⚖️ Mod', output)
        self.assertIn('## Transcript', output)
        self.assertIn('Opening statement by Alice.', output)
        self.assertIn('Moderator comment.', output)
        self.assertIn('## Summary', output)

    def test_json_output(self):
        output = self.orchestrator.get_formatted_output('json')
        self.assertIn('"topic": "Test Topic"', output)
        self.assertIn('"status": "active"', output)
        self.assertIn('"total_messages": 3', output)

    def test_html_output(self):
        output = self.orchestrator.get_formatted_output('html')
        self.assertIn('<h1>Test Topic</h1>', output)
        self.assertIn('<h2>Participants</h2>', output)
        self.assertIn('<h3 class=', output)
        self.assertIn('Opening statement by Alice.', output)
        self.assertIn('Moderator comment.', output)
        self.assertIn('<h2>Summary</h2>', output)

if __name__ == '__main__':
    unittest.main()
