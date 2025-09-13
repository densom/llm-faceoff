# Requirements and Constraints

## Functional Requirements
- Support for multiple LLMs (initially Microsoft Copilot and Claude; extensible to others).
- Structured debate rounds with configurable topics and rules.
- Logging and transcript generation for each debate.
- Ability to configure debate parameters (turns, time limits, etc.).

## Non-Functional Requirements
- Modular and extensible codebase (Python).
- Easy to add new LLM providers.
- Clear documentation and reproducibility.

## Constraints
- The solution must be written in **Python**.
- Only **markdown files** are produced during planning, and must reside in the `./planning/copilot` directory.
- The initial LLMs are **Microsoft Copilot** and **Claude**.
- The **`uv` tool** is used for Python dependency management (not `pip`). `uv init` has already been run.
- Execution phase will be defined after planning is complete.

---

Next: See `01-architecture.md` for system design.
