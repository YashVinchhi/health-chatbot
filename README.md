
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
=======
# health-chatbot
>>>>>>> b6193b6252525f113f7278f4b231f3a652dede1c
