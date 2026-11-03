# Contributing to Meyme (30 Days of AI Voice Agents)

Thank you for contributing! Whether you are adding new persona skills, optimizing latency, or improving frontend audio visualizers, contributions are welcome.

## Getting Started Locally

1. **Clone & install:**
   ```bash
   git clone https://github.com/atharhive/30-days-of-ai-voice-agents.git
   cd 30-days-of-ai-voice-agents
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Environment Configuration:**
   Copy `.env.example` to `.env` and supply your API keys:
   ```bash
   cp .env.example .env
   ```

3. **Run the server:**
   ```bash
   python main.py
   ```
   Open `http://localhost:8000` to interact with Meyme.

## Development Guidelines
- Follow PEP 8 guidelines for Python code.
- Keep WebSocket streaming latency minimal.
- Test error fallbacks when third-party STT/TTS services fail.

## Maintainer Responsiveness SLA
We aim to respond to issues and review pull requests within **24 hours**.
