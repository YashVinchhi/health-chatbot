# 🤖 RASA Interaction Guide - Health Chatbot

## 🚨 IMPORTANT: Port Configuration Fixed

**The issue you encountered was a port conflict!**
- Grafana (monitoring) was using port 3000
- Your frontend actually runs on port 3001
- When you went to localhost:3000, you saw Grafana's login page

## 🎯 How to Interact with RASA

### Method 1: Web Interface (Recommended for Users)
After running `start-rasa-gui.bat`, go to:
```
http://localhost:3001
```
This gives you a beautiful web interface where you can:
- Chat with the bot in multiple languages
- Get health advice and symptom analysis
- Find hospitals and vaccination info

### Method 2: Direct RASA API (For Developers)
RASA server runs on:
```
http://localhost:5005
```

Test RASA directly with curl or Postman:
```bash
# Check if RASA is running
curl http://localhost:5005/status

# Send a message to RASA
curl -X POST http://localhost:5005/webhooks/rest/webhook \
  -H "Content-Type: application/json" \
  -d '{"sender": "test", "message": "Hello"}'
```

### Method 3: Backend API Integration
The backend integrates with RASA and provides additional health services:
```
http://localhost:8000/docs
```

## 🔧 Current Port Allocation

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| Frontend Web UI | 3001 | http://localhost:3001 | Main chat interface |
| RASA Server | 5005 | http://localhost:5005 | Core AI chatbot |
| RASA Actions | 5055 | http://localhost:5055 | Custom actions |
| Backend API | 8000 | http://localhost:8000 | Health services |
| PostgreSQL | 5432 | localhost:5432 | Database |
| Prometheus | 9090 | http://localhost:9090 | Monitoring |
| Grafana | 3000 | http://localhost:3000 | Dashboards |
| Kafka | 9092 | localhost:9092 | Message queue |

## 🚀 Step-by-Step Usage

### For Regular Users:
1. Run `start-rasa-gui.bat`
2. Wait for all services to start (about 30-60 seconds)
3. Go to `http://localhost:3001`
4. Start chatting with the health bot!

### For Developers:
1. Use `http://localhost:8000/docs` for API documentation
2. Use `http://localhost:5005` for direct RASA API access
3. Use `http://localhost:9090` for Prometheus metrics
4. Use `http://localhost:3000` for Grafana dashboards (login: admin/admin)

## 💬 Test Messages

Try these messages in the web interface:

**English:**
- "Hello"
- "I have a fever"
- "Find hospitals in Delhi"
- "COVID vaccine information"

**Hindi:**
- "नमस्ते"
- "मुझे बुखार है"
- "दिल्ली में अस्पताल ढूंढें"

**Emergency:**
- "Emergency help needed"
- "I need immediate medical attention"

## 🐛 Troubleshooting

### If you see Grafana login page:
- You're going to the wrong URL
- Use `http://localhost:3001` instead of `http://localhost:3000`

### If services won't start:
- Check if ports are already in use
- Close any existing Python/RASA processes
- Restart the bat file

### If RASA doesn't respond:
- Wait for model training to complete
- Check `http://localhost:5005/status`
- Look for errors in the terminal windows

## 🔄 Docker vs Local Setup

**Local Setup (Recommended for Development):**
- Use `start-rasa-gui.bat`
- All services run locally
- Easy to debug and modify

**Docker Setup (For Production):**
- Use `start-docker.bat`
- All services in containers
- Better for deployment

## 🎯 Direct RASA Commands

If you want to interact with RASA directly via command line:

```bash
# Navigate to RASA directory
cd rasa_bot

# Train the model
rasa train

# Run RASA server
rasa run --enable-api --cors "*" --port 5005

# Run RASA actions
rasa run actions --port 5055

# Interactive chat (command line)
rasa shell
```
