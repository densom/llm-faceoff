# Requirements and Constraints

## Functional Requirements
- Support for multiple LLMs (e.g., OpenAI, Anthropic, local models).
- Structured debate rounds with configurable topics and rules.
- Logging and transcript generation for each debate.
- Ability to configure debate parameters (turns, time limits, etc.).

## Non-Functional Requirements
- Modular and extensible codebase.
- Easy to add new LLM providers.
- Clear documentation and reproducibility.

## Constraints
- Output must be markdown files during planning.
- All planning markdown files must reside in the `./planning/copilot` directory.
- Execution phase will be defined after planning is complete.

---

Next: See `01-architecture.md` for system design.
