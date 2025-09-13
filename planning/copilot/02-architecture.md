# System Architecture

## High-Level Components
- **Debate Orchestrator**: Manages debate flow, rounds, and rules.
- **LLM Adapter Interface**: Abstracts communication with different LLM providers.
- **Debate Logger**: Captures and stores debate transcripts.
- **Configuration Manager**: Handles debate settings and parameters.

## Data Flow
1. User configures debate (topic, LLMs, rules).
2. Orchestrator initiates debate and alternates turns between LLMs.
3. Each LLM response is logged.
4. Debate ends after set rounds or conditions.
5. Results and transcripts are saved for analysis.

## Extensibility
- New LLMs can be added by implementing the Adapter Interface.
- Debate formats and rules can be extended via configuration.

---

Next: See `02-debate-protocol.md` for debate structure and rules.
