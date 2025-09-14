import unittest
from llm_faceoff.debate.orchestrator import DebateOrchestrator
from llm_faceoff.llms.copilot_adapter import CopilotAdapter
from llm_faceoff.llms.claude_adapter import ClaudeAdapter
from llm_faceoff.config import ConfigManager

class TestDebateOrchestrator(unittest.TestCase):
    def setUp(self):
        self.copilot = CopilotAdapter()
        self.claude = ClaudeAdapter()
        self.config = ConfigManager({'rounds': 3})
        self.orchestrator = DebateOrchestrator([self.copilot, self.claude], self.config)

    def test_debate_flow(self):
        topic = "Is AI beneficial to society?"
        self.orchestrator.start_debate(topic)
        transcript = self.orchestrator.get_transcript()

        # Check that debate started and ended messages are present
        self.assertIn(f"Debate started on topic: {topic}", transcript[0])
        self.assertIn("Debate ended.", transcript[-1])

        # Check that each LLM has opening, rebuttal, and closing statements
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

if __name__ == '__main__':
    unittest.main()
