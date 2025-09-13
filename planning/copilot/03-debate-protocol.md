# Debate Protocol and Rules

## Debate Structure
- **Opening Statements**: Each LLM presents its initial argument.
- **Rebuttal Rounds**: LLMs alternate turns to respond to each other.
- **Closing Statements**: Each LLM summarizes its position.

## Turn Management
- The orchestrator enforces turn order and time/length limits.
- Each LLM receives the full debate context for its turn.

## Evaluation
- Optionally, a third-party LLM or human can judge the debate.
- Criteria: argument quality, relevance, factual accuracy, etc.

## Logging
- All exchanges are timestamped and saved to a transcript.

---

Next: See `03-execution-roadmap.md` for implementation steps.
