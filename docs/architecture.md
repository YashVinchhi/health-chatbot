# System Architecture

## Overview

The Health Chatbot system consists of several interconnected components:

```
User → WhatsApp/SMS → FastAPI Backend → Rasa NLP → Database
                                     ↓
                              External APIs
```

## Components

### 1. Frontend Interfaces
- WhatsApp Business API
- SMS Gateway
- Support for both push and pull messaging

### 2. Backend Server (FastAPI)
- REST API endpoints
- Message routing
- User management
- Alert scheduling

### 3. Rasa NLP Engine
- Intent classification
- Entity extraction
- Dialogue management
- Multi-language support

### 4. Database (PostgreSQL)
- User profiles
- Conversation history
- Alert configurations
- Health data cache

### 5. External Integrations
- CoWIN API
- IDSP Reports
- WHO/MoHFW Data

## Data Flow

1. User sends message via WhatsApp/SMS
2. Message routed to FastAPI backend
3. Rasa processes natural language
4. Backend fetches required data
5. Response sent back to user

## Deployment

- Docker containers for each component
- Nginx as reverse proxy
- Prometheus/Grafana for monitoring
- Regular database backups