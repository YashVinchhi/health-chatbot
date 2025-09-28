# Health Chatbot

A multilingual health chatbot system for preventive healthcare and vaccination awareness using WhatsApp/SMS.

## Features

- Multilingual support (English, Hindi, and local languages)
- WhatsApp and SMS integration
- Vaccination schedule reminders
- Disease outbreak alerts
- Preventive health information
- Symptom-based guidance

## Tech Stack

- **NLP/Dialogue Management**: Rasa
- **Backend**: FastAPI
- **Database**: PostgreSQL
- **Messaging**: WhatsApp Business API, SMS Gateway
- **Deployment**: Docker, Nginx
- **Monitoring**: Grafana, Prometheus

## Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and fill in your credentials
3. Install dependencies: `pip install -r requirements.txt`
4. Run with Docker: `docker-compose up`

## Development

```bash
# Train Rasa model
./scripts/train_bot.sh

# Run locally
./scripts/run_local.sh

# Run tests
pytest backend/tests/
```

## Project Structure

```
health-chatbot/
├── rasa_bot/          # Rasa NLP & dialogue management
├── backend/           # FastAPI server & integrations
├── scripts/           # Automation scripts
├── infra/            # Deployment & monitoring
└── docs/             # Documentation
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Ollama LLM Mode (Alternative to Rasa)

An experimental local LLM pathway using [Ollama](https://ollama.com/) has been added. When enabled, the backend bypasses Rasa and uses a local model (default `llama3`) for intent + answer generation in structured JSON.

### Enable
Set the following environment variables (e.g. in `.env`):
```
USE_LLM=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```
Run Ollama locally and pull a model first:
```
ollama pull llama3
```
Then start only backend + frontend (you can skip all Rasa services). Requests to `/api/health/chat` will return `source: "llm"`.

### Fallback & Safety
If the LLM call fails or returns malformed JSON, a deterministic safety fallback answer is returned (`source: llm_fallback_*`). Emergency guidance always instructs users to call local emergency numbers (e.g., 108 in India) instead of generating speculative advice.

### Switching Back to Rasa
Unset `USE_LLM` or set it to `false` to restore the original Rasa pipeline without changing any client code.
