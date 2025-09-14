import unittest
from llm_faceoff.llms.claude_adapter import ClaudeAdapter

class TestClaudeAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = ClaudeAdapter()

    def test_generate_response(self):
        topic = "Is AI beneficial to society?"
        context = ""
        response = self.adapter.generate_response(topic, context)
        print("Claude Adapter Response:", response)
        self.assertIsInstance(response, str)
        self.assertNotIn("error", response.lower())

if __name__ == '__main__':
    unittest.main()
