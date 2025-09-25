🏥 QUICK START GUIDE - RASA Health Chatbot
============================================

## 🚀 IMMEDIATE STEPS TO GET STARTED

### Step 1: Install RASA (REQUIRED)
Open Command Prompt as Administrator and run:
```cmd
pip install rasa
pip install rasa-sdk
pip install requests
pip install aiohttp
```

### Step 2: Start Your RASA Health Chatbot
Simply double-click this file in Windows Explorer:
```
start-rasa.bat
```

Or run from Command Prompt:
```cmd
start-rasa.bat
```

### Step 3: Open Your Browser
Visit: http://localhost:8000

### Step 4: Test the AI Chat
Try these example messages:
- "Hello"
- "I have a fever"  
- "Tell me about COVID vaccines"
- "Find hospitals near me"
- "I need emergency help"

## ✅ WHAT TO EXPECT

### When Everything Works:
1. Command Prompt windows will open for each service
2. You'll see "RASA Connected" status in the chat
3. Responses will show "🤖 RASA" indicator
4. Interactive buttons and suggestions will appear

### If RASA is Offline:
- Status shows "RASA Offline (Fallback Mode)"
- Responses show "⚡ Fallback" indicator  
- Basic responses still work

## 🆘 QUICK TROUBLESHOOTING

### Problem: "rasa command not found"
Solution: Install RASA first
```cmd
pip install rasa rasa-sdk
```

### Problem: Port already in use
Solution: Close other applications using ports 5005, 5055, 8000

### Problem: Python not found
Solution: Install Python 3.8+ from python.org

## 🎯 SUCCESS INDICATORS

✅ Backend running on http://localhost:8000
✅ RASA server on http://localhost:5005  
✅ Actions server on http://localhost:5055
✅ Chat shows "🤖 RASA" responses
✅ Interactive buttons work

## 📞 TEST COMMANDS

Try these to verify RASA is working:
1. "I have symptoms" → Should ask follow-up questions
2. "Emergency help" → Should show Indian emergency numbers
3. "COVID vaccine info" → Should mention CoWIN portal
4. "Hospitals in Delhi" → Should list hospital information

Your AI health chatbot is ready! 🚀
