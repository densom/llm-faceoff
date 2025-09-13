# LLM Faceoff

This project enables different Large Language Models (LLMs) to debate with each other. It is written in Python and designed to be extensible to multiple LLM providers.

## Project Setup

- Python environment is managed using the `uv` tool (not `pip`).
- The initial supported LLMs are Microsoft Copilot and Claude.

## Getting Started

1. Ensure you have run `uv init` to initialize the environment.
2. Install dependencies with `uv install`.
3. Run the main program with `python main.py`.

## Project Structure

- `main.py`: Entry point for running debates.
- `llm_faceoff/`: Core package containing debate orchestrator, LLM adapters, logger, and configuration.
- `planning/`: Markdown files documenting planning and architecture.

## Contributing

Contributions are welcome! Please adhere to the following guidelines:

- Discuss any major changes or enhancements via issues or pull requests.
- Ensure code is well-documented and tested.
- Follow the existing code style and conventions.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by the need for robust evaluation of LLMs in interactive settings.
- Thanks to the contributors and the open-source community.

---