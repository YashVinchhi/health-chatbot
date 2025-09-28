// Modern Health Chatbot Class
class HealthChatbot {
    constructor() {
        console.log('🚀 HealthChatbot constructor called - Enhanced Session Memory Mode');
        // Dynamically determine backend base (prevents hitting static server for API calls)
        const backendHost = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
            ? 'http://localhost:8000'
            : window.location.origin; // In production assume same origin reverse proxy
        this.apiBase = backendHost;
        this.apiUrl = this.apiBase + '/api/health'; // CHANGED from relative '/api/health'
        console.log('🔗 Backend API base set to:', this.apiUrl);
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.chatMessages = document.getElementById('chatMessages');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.connectionStatus = document.getElementById('connectionStatus');
        this.isConnected = false;
        this.currentTab = 'chat';
        this.chatHistory = [];
        this.sessionId = this.getOrCreateSessionId();
        this.rasaStatus = 'checking';
        this.currentLanguage = 'en'; // Will be auto-detected
        this.conversationContext = {}; // Store conversation context
        this.lastMessageTime = null;

        // Debug: Check if required elements exist
        console.log('🔍 Required elements check:', {
            messageInput: !!this.messageInput,
            sendButton: !!this.sendButton,
            chatMessages: !!this.chatMessages,
            typingIndicator: !!this.typingIndicator,
            connectionStatus: !!this.connectionStatus
        });

        this.init();
    }

    getOrCreateSessionId() {
        // Try to get existing session ID from localStorage for session persistence
        let sessionId = localStorage.getItem('healthbot_session_id');

        // Check if session is still valid (within 24 hours)
        const sessionCreated = localStorage.getItem('healthbot_session_created');
        const now = Date.now();
        const sessionAge = now - parseInt(sessionCreated || '0');
        const maxSessionAge = 24 * 60 * 60 * 1000; // 24 hours

        if (!sessionId || sessionAge > maxSessionAge) {
            // Create new session
            sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('healthbot_session_id', sessionId);
            localStorage.setItem('healthbot_session_created', now.toString());
            console.log('🆕 Created new session:', sessionId);
        } else {
            console.log('♻️ Using existing session:', sessionId);
        }

        return sessionId;
    }

    async init() {
        console.log('🔧 Initializing HealthChatbot with RASA integration...');
        try {
            this.setupEventListeners();
            console.log('✅ Event listeners setup completed');

            await this.checkConnection();
            console.log('✅ Connection check completed');

            await this.checkRasaStatus();
            console.log('✅ RASA status check completed');

            this.enableInput();
            console.log('✅ Input enabled');

            this.initializeTheme();
            console.log('✅ Theme initialized');

            this.loadChatHistory();
            console.log('✅ Chat history loaded');

            // Show welcome message with multilingual support
            this.showWelcomeMessage();

            console.log('🎉 HealthChatbot initialization completed successfully!');
        } catch (error) {
            console.error('❌ HealthChatbot initialization failed:', error);
        }
    }

    showWelcomeMessage() {
        // Check if we have previous conversation context
        const hasHistory = this.chatHistory.length > 0;

        let welcomeMessage;
        if (hasHistory) {
            welcomeMessage = {
                response: `👋 **Welcome back to HealthBot AI!**

I remember our previous conversation. I can continue helping you with your health questions in multiple languages:

• **English** - "How is my fever now?"
• **हिंदी** - "अब मेरा बुखार कैसा है?"  
• **తెలుగు** - "ఇప్పుడు నా జ్వరం ఎలా ఉంది?"
• **தமிழ்** - "இப்ப என் காய்ச்சல் எப்படி இருக்கு?"
• **বাংলা** - "এখন আমার জ্বর কেমন?"

What would you like to know today?`,
                source: 'system',
                buttons: [],
                quick_replies: ['Continue Previous Topic', 'New Health Question', 'Find Hospitals', 'Emergency Help']
            };
        } else {
            welcomeMessage = {
                response: `👋 **Welcome to HealthBot AI!**

I'm your multilingual health assistant with memory! I can help you in:
• **English** - "I have fever"
• **हिंदी** - "मुझे बुखार है"  
• **తెలుగు** - "నాకు జ్వరం వచ్చింది"
• **தமிழ்** - "எனக்கு காய்ச்சல் வந்துருச்சு"
• **বাংলা** - "আমার জ্বর হয়েছে"

🩺 **I can help with:**
• Symptom analysis & guidance (with memory of previous symptoms)
• Hospital & doctor finder
• Vaccination information
• Medicine information
• Emergency contacts

**I'll remember our conversation to provide better help!**

**Emergency: Call 108 immediately for medical emergencies**

What can I help you with today?`,
                source: 'system',
                buttons: [],
                quick_replies: ['Find Hospitals', 'Vaccination Info', 'Symptom Checker', 'Emergency Help']
            };
        }

        this.displayMessage(welcomeMessage, 'bot');
    }

    async checkRasaStatus() {
        try {
            console.log('🔍 Checking RASA server status...');
            const response = await fetch(`${this.apiUrl}/rasa/status`);
            const status = await response.json();

            console.log('📊 RASA Status Response:', status);

            this.rasaStatus = status.status || 'offline';
            this.updateConnectionStatus(status);

            // Get model information
            if (this.rasaStatus === 'online') {
                const modelInfo = await fetch(`${this.apiUrl}/rasa/model/info`);
                const modelData = await modelInfo.json();
                console.log('🤖 Model Info:', modelData);
            }

        } catch (error) {
            console.error('❌ RASA status check failed:', error);
            this.rasaStatus = 'offline';
            this.updateConnectionStatus({ status: 'offline', error: error.message });
        }
    }

    updateConnectionStatus(statusData = {}) {
        const statusElement = document.getElementById('connectionStatus');
        const statusDot = document.querySelector('.status-dot');

        if (!statusElement || !statusDot) return;

        if (this.rasaStatus === 'online') {
            statusElement.innerHTML = `
                <span>🤖 RASA Connected</span>
                <small>Multilingual AI Active</small>
            `;
            statusDot.className = 'status-dot online';

            // Show model information
            if (statusData.model_file) {
                statusElement.title = `Model: ${statusData.model_file}\nActions: ${statusData.actions_server ? 'Online' : 'Offline'}`;
            }
        } else if (this.rasaStatus === 'offline') {
            statusElement.innerHTML = `
                <span>🔄 Fallback Mode</span>
                <small>Basic responses active</small>
            `;
            statusDot.className = 'status-dot offline';
            statusElement.title = `RASA offline: ${statusData.error || 'Server unavailable'}`;
        } else {
            statusElement.innerHTML = `
                <span>⏳ Connecting...</span>
                <small>Checking RASA server</small>
            `;
            statusDot.className = 'status-dot checking';
        }
    }

    setupEventListeners() {
        console.log('🔧 Setting up event listeners...');

        // Message input event listeners
        if (this.messageInput) {
            // Enable input immediately
            this.messageInput.disabled = false;

            // Enable send button when there's text - FIXED
            this.messageInput.addEventListener('input', (e) => {
                const hasText = e.target.value.trim().length > 0;
                this.sendButton.disabled = !hasText;

                // Add visual feedback
                if (hasText) {
                    this.sendButton.classList.add('enabled');
                    this.sendButton.classList.remove('disabled');
                } else {
                    this.sendButton.classList.remove('enabled');
                    this.sendButton.classList.add('disabled');
                }

                // Update suggestions based on input
                this.updateSuggestions();
            });

            // Handle Enter key press - FIXED
            this.messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    const message = this.messageInput.value.trim();
                    if (message) {
                        this.sendMessage();
                    }
                }
            });

            // Handle Escape key to clear input
            this.messageInput.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    this.messageInput.value = '';
                    this.sendButton.disabled = true;
                    this.sendButton.classList.remove('enabled');
                    this.sendButton.classList.add('disabled');
                }
            });

            // Focus input after page load
            setTimeout(() => {
                this.messageInput.focus();
            }, 500);
        }

        // Send button click - FIXED
        if (this.sendButton) {
            this.sendButton.addEventListener('click', (e) => {
                e.preventDefault();
                const message = this.messageInput.value.trim();
                if (message && !this.sendButton.disabled) {
                    this.sendMessage();
                }
            });
        }

        // Language detection for better UX
        if (this.messageInput) {
            this.messageInput.addEventListener('input', (e) => {
                this.detectLanguage(e.target.value);
            });
        }

        // Scroll behavior for chat messages - FIXED
        if (this.chatMessages) {
            this.chatMessages.addEventListener('scroll', () => {
                this.handleScroll();
            });
        }

        // Quick reply buttons (will be added dynamically) - FIXED
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('quick-reply-btn')) {
                e.preventDefault();
                const messageText = e.target.textContent.trim();
                if (messageText) {
                    this.sendMessage(messageText);
                }
            }
        });

        // Handle scroll to bottom button - FIXED
        const scrollButton = document.getElementById('scrollToBottom');
        if (scrollButton) {
            scrollButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.scrollToBottom();
            });
        }

        // Prevent form submission on Enter in input fields
        document.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && e.target.tagName === 'INPUT' && e.target.type === 'text') {
                e.preventDefault();
            }
        });
    }

    detectLanguage(text) {
        // Simple language detection based on script
        if (/[\u0900-\u097F]/.test(text)) {
            this.currentLanguage = 'hi'; // Hindi
        } else if (/[\u0C00-\u0C7F]/.test(text)) {
            this.currentLanguage = 'te'; // Telugu
        } else if (/[\u0B80-\u0BFF]/.test(text)) {
            this.currentLanguage = 'ta'; // Tamil
        } else if (/[\u0980-\u09FF]/.test(text)) {
            this.currentLanguage = 'bn'; // Bengali
        } else {
            this.currentLanguage = 'en'; // English
        }
    }

    async sendMessage(messageText = null) {
        const message = messageText || this.messageInput.value.trim();
        if (!message) return;

        console.log(`📤 Sending message: "${message}" (Language: ${this.currentLanguage})`);

        // Clear input and disable send button
        this.messageInput.value = '';
        this.sendButton.disabled = true;

        // Display user message
        this.displayMessage({ response: message, source: 'user' }, 'user');

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Send to enhanced RASA-integrated backend
            const response = await fetch(`${this.apiUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId,
                    sender: 'user'
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('📥 Received response:', data);

            this.hideTypingIndicator();
            this.displayMessage(data, 'bot');

            // Store in chat history
            this.chatHistory.push(
                { message, sender: 'user', timestamp: new Date().toISOString() },
                { message: data.response, sender: 'bot', timestamp: data.timestamp, source: data.source }
            );

            this.saveChatHistory();

        } catch (error) {
            console.error('❌ Error sending message:', error);
            this.hideTypingIndicator();

            // Show error message
            this.displayMessage({
                response: "I'm experiencing some technical difficulties. For medical emergencies, please call 108 immediately.",
                source: 'error',
                quick_replies: ['Try Again', 'Emergency: 108', 'Contact Support']
            }, 'bot');
        }
    }

    displayMessage(messageData, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;

        let sourceIndicator = '';
        if (sender === 'bot') {
            switch (messageData.source) {
                case 'rasa':
                    sourceIndicator = '<span class="source-indicator rasa">🤖 AI</span>';
                    break;
                case 'fallback':
                case 'fallback_connection':
                case 'fallback_timeout':
                    sourceIndicator = '<span class="source-indicator fallback">⚡ Fallback</span>';
                    break;
                case 'error':
                    sourceIndicator = '<span class="source-indicator error">⚠️ Error</span>';
                    break;
                default:
                    sourceIndicator = '<span class="source-indicator system">📋 System</span>';
            }
        }

        // Enhanced message formatting with markdown-like support
        let formattedResponse = this.formatMessage(messageData.response || messageData.message || '');

        messageDiv.innerHTML = `
            <div class="message-content">
                ${sourceIndicator}
                <div class="message-text">${formattedResponse}</div>
                ${messageData.buttons ? this.createButtons(messageData.buttons) : ''}
                ${messageData.quick_replies ? this.createQuickReplies(messageData.quick_replies) : ''}
                <div class="message-time">${this.formatTime(messageData.timestamp)}</div>
            </div>
        `;

        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();

        // Add intent and confidence info for debugging (only in development)
        if (messageData.intent && messageData.confidence !== undefined && window.location.hostname === 'localhost') {
            const debugInfo = document.createElement('div');
            debugInfo.className = 'debug-info';
            debugInfo.innerHTML = `
                <small>Intent: ${messageData.intent} (${(messageData.confidence * 100).toFixed(1)}%)</small>
            `;
            messageDiv.appendChild(debugInfo);
        }
    }

    formatMessage(text) {
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold
            .replace(/\*(.*?)\*/g, '<em>$1</em>') // Italic
            .replace(/^• (.*$)/gm, '<li>$1</li>') // Bullet points
            .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>') // Wrap bullets in ul
            .replace(/\n/g, '<br>') // Line breaks
            .replace(/🚨 \*\*URGENT:\*\*/g, '<span class="urgent">🚨 <strong>URGENT:</strong></span>') // Urgent styling
            .replace(/(\d{3})/g, '<span class="phone-number">$1</span>'); // Phone number styling
    }

    createButtons(buttons) {
        if (!buttons || buttons.length === 0) return '';

        return `
            <div class="message-buttons">
                ${buttons.map(button => `
                    <button class="message-btn" onclick="healthChatbot.sendMessage('${button.payload || button.title}')">
                        ${button.title}
                    </button>
                `).join('')}
            </div>
        `;
    }

    createQuickReplies(quickReplies) {
        if (!quickReplies || quickReplies.length === 0) return '';

        return `
            <div class="quick-replies">
                <div class="quick-replies-label">Quick actions:</div>
                ${quickReplies.map(reply => `
                    <button class="quick-reply-btn" onclick="healthChatbot.sendMessage('${reply}')">
                        ${reply}
                    </button>
                `).join('')}
            </div>
        `;
    }

    formatTime(timestamp) {
        if (!timestamp) return '';
        const date = new Date(timestamp);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    showTypingIndicator() {
        if (this.typingIndicator) {
            this.typingIndicator.style.display = 'flex';
            this.scrollToBottomSafely();
        }
    }

    hideTypingIndicator() {
        if (this.typingIndicator) {
            this.typingIndicator.style.display = 'none';
        }
    }

    scrollToBottomSafely() {
        if (this.chatMessages) {
            // Use requestAnimationFrame for smoother scrolling
            requestAnimationFrame(() => {
                this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
            });
        }
    }

    // Remove the duplicate scrollToBottom method and use only this one
    scrollToBottom() {
        this.scrollToBottomSafely();
    }


    async checkConnection() {
        try {
            console.log('🔄 Checking backend connection...');
            const response = await fetch(`${this.apiUrl}/health-tips`);
            console.log('📡 Response status:', response.status);

            if (response.ok) {
                const data = await response.json();
                console.log('✅ Backend connected successfully:', data);
                this.setConnectionStatus(true, 'Connected');
            } else {
                console.log('❌ Backend returned error:', response.status);
                this.setConnectionStatus(false, 'Service unavailable');
            }
        } catch (error) {
            console.error('❌ Connection check failed:', error);
            console.log('🔧 Trying fallback connection test...');

            // Try a simpler endpoint
            try {
                const testResponse = await fetch('/api/health/test');
                if (testResponse.ok) {
                    console.log('✅ Fallback connection successful');
                    this.setConnectionStatus(true, 'Connected (fallback)');
                } else {
                    this.setConnectionStatus(false, 'Connection failed');
                }
            } catch (fallbackError) {
                console.error('❌ Fallback also failed:', fallbackError);
                this.setConnectionStatus(false, 'Backend offline');
            }
        }
    }

    setConnectionStatus(connected, message) {
        this.isConnected = connected;
        this.connectionStatus.textContent = message;
        const statusDot = document.querySelector('.status-dot');
        statusDot.className = `status-dot ${connected ? 'online' : 'offline'}`;

        // Update main status
        const mainStatus = document.getElementById('status');
        if (mainStatus) {
            mainStatus.textContent = connected ? 'Online' : 'Offline';
        }
    }

    enableInput() {
        this.messageInput.disabled = false;
        this.messageInput.focus();
    }

    // Enhanced scroll to bottom with intelligent behavior - auto-hide after scrolling
    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
            this.hideScrollButton(); // Auto-hide after scrolling to bottom as per spec
        }, 100);
    }

    // Handle scroll event to show/hide scroll button - following project specifications
    handleScroll() {
        const scrollButton = document.getElementById('scrollToBottom');
        if (!scrollButton) return;

        const { scrollTop, scrollHeight, clientHeight } = this.chatMessages;
        const isNearBottom = scrollHeight - scrollTop - clientHeight < 100; // Within 100px as per spec

        // Smart behavior: show when user scrolls up from bottom, hide when near bottom
        if (isNearBottom) {
            this.hideScrollButton();
        } else {
            this.showScrollButton();
        }
    }

    // Show scroll to bottom button with smooth animation
    showScrollButton() {
        const scrollButton = document.getElementById('scrollToBottom');
        if (scrollButton && !scrollButton.classList.contains('show')) {
            scrollButton.classList.add('show');
        }
    }

    // Hide scroll to bottom button with smooth animation
    hideScrollButton() {
        const scrollButton = document.getElementById('scrollToBottom');
        if (scrollButton && scrollButton.classList.contains('show')) {
            scrollButton.classList.remove('show');
        }
    }

    // Enhanced quick action functionality with comprehensive features
    sendQuickMessage(message) {
        // Validate input
        if (!message || !message.trim()) {
            console.warn('Quick message is empty');
            return;
        }

        // Set input value and send message
        this.messageInput.value = message;

        // Add visual feedback for quick action
        this.addQuickActionFeedback(message);

        // Send the message
        this.sendMessage();
    }

    // Add visual feedback when quick action is used
    addQuickActionFeedback(message) {
        // Find the clicked button based on message content
        const quickBtns = document.querySelectorAll('.quick-btn');
        let clickedBtn = null;

        quickBtns.forEach(btn => {
            const onclick = btn.getAttribute('onclick');
            if (onclick && onclick.includes(message)) {
                clickedBtn = btn;
            }
        });

        if (clickedBtn) {
            // Add visual feedback
            clickedBtn.classList.add('quick-action-active');

            // Remove feedback after animation
            setTimeout(() => {
                clickedBtn.classList.remove('quick-action-active');
            }, 300);
        }
    }

    clearChat() {
        // Keep only the welcome message
        const messages = this.chatMessages.querySelectorAll('.message');
        for (let i = 1; i < messages.length; i++) {
            messages[i].remove();
        }
        this.chatHistory = [];
        this.saveChatHistory();
    }

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

        this.setTheme(newTheme);
    }

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);

        // Update theme icon
        const themeIcon = document.getElementById('theme-icon');
        if (themeIcon) {
            themeIcon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }

        // Update theme buttons in settings
        document.querySelectorAll('.theme-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.theme === theme);
        });
    }

    initializeTheme() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        this.setTheme(savedTheme);
    }

    detectSystemTheme() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            if (!localStorage.getItem('theme')) {
                this.setTheme('dark');
            }
        }

        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
            if (!localStorage.getItem('theme')) {
                this.setTheme(e.matches ? 'dark' : 'light');
            }
        });
    }

    updateSuggestions() {
        const input = this.messageInput.value.toLowerCase();
        const suggestions = document.getElementById('inputSuggestions');

        if (!suggestions) return;

        const allSuggestions = [
            'I have a fever',
            'COVID symptoms',
            'Vaccination schedule',
            'Health tips',
            'Emergency help',
            'I feel sick',
            'Headache relief',
            'Nearby hospitals'
        ];

        const filtered = allSuggestions.filter(s =>
            s.toLowerCase().includes(input) && s.toLowerCase() !== input
        ).slice(0, 3);

        suggestions.innerHTML = filtered.map(s =>
            `<span class="suggestion" onclick="applySuggestion('${s}')">${s}</span>`
        ).join('');
    }

    saveChatHistory() {
        localStorage.setItem('healthbot_history', JSON.stringify(this.chatHistory));
    }

    loadChatHistory() {
        const saved = localStorage.getItem('healthbot_history');
        if (saved) {
            this.chatHistory = JSON.parse(saved);
        }
    }

    exportChat() {
        const chatData = {
            timestamp: new Date().toISOString(),
            messages: this.chatHistory
        };

        const blob = new Blob([JSON.stringify(chatData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = `healthbot-chat-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    handleMobileView() {
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.createElement('div');
        overlay.className = 'mobile-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 999;
            display: none;
        `;
        document.body.appendChild(overlay);

        overlay.addEventListener('click', () => {
            sidebar.classList.remove('open');
            overlay.style.display = 'none';
        });
    }

    // Enhanced tab functionality
    setActiveTab(tabName) {
        // Remove active class from all nav items
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });

        // Add active class to clicked nav item
        const clickedItem = document.querySelector(`[onclick*="setActiveTab('${tabName}')"]`);
        if (clickedItem) {
            clickedItem.classList.add('active');
        }

        // Hide all tab contents
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });

        // Show selected tab content
        const selectedTab = document.getElementById(`${tabName}-tab`);
        if (selectedTab) {
            selectedTab.classList.add('active');
        }

        this.currentTab = tabName;
    }

    // Enhanced sidebar functionality
    toggleSidebar() {
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.querySelector('.mobile-overlay');

        sidebar.classList.toggle('open');
        if (overlay) {
            overlay.style.display = sidebar.classList.contains('open') ? 'block' : 'none';
        }
    }

    // Enhanced quick actions
    toggleQuickActions() {
        const quickActions = document.getElementById('quickActions');
        const collapseBtn = document.querySelector('.collapse-btn i');

        if (quickActions.style.display === 'none') {
            quickActions.style.display = 'grid';
            collapseBtn.className = 'fas fa-chevron-up';
        } else {
            quickActions.style.display = 'none';
            collapseBtn.className = 'fas fa-chevron-down';
        }
    }

    // Enhanced quick actions with intelligent responses
    handleQuickAction(actionType) {
        let message = '';
        let followUpSuggestions = [];

        switch(actionType) {
            case 'symptoms':
                message = 'I have symptoms that I need help with';
                followUpSuggestions = [
                    'I have a fever',
                    'I have a headache',
                    'I feel nauseous',
                    'I have chest pain'
                ];
                break;

            case 'vaccines':
                message = 'Tell me about vaccinations';
                followUpSuggestions = [
                    'COVID-19 vaccine info',
                    'Flu shot schedule',
                    'Travel vaccines',
                    'Childhood immunizations'
                ];
                break;

            case 'alerts':
                message = 'Any health alerts in my area?';
                followUpSuggestions = [
                    'Air quality today',
                    'Disease outbreaks',
                    'Weather health warnings',
                    'Food safety alerts'
                ];
                break;

            case 'emergency':
                message = 'I need emergency health assistance';
                followUpSuggestions = [
                    'Call 911',
                    'Nearest hospital',
                    'First aid guidance',
                    'Poison control'
                ];
                break;

            case 'tips':
                message = 'Give me health tips for today';
                followUpSuggestions = [
                    'Exercise tips',
                    'Nutrition advice',
                    'Sleep hygiene',
                    'Mental health tips'
                ];
                break;

            case 'hospitals':
                message = 'Find hospitals near my location';
                this.requestLocationForHospitals();
                return;

            default:
                message = 'How can I help you with your health today?';
        }

        this.sendQuickMessage(message);
        this.updateSuggestionsWithFollowUp(followUpSuggestions);
    }

    // Request location for hospital search with enhanced error handling
    requestLocationForHospitals() {
        if ('geolocation' in navigator) {
            // Show loading message
            this.addMessage(
                'Getting your location to find nearby hospitals... 📍',
                'bot',
                'location_request'
            );

            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const { latitude, longitude } = position.coords;
                    this.sendQuickMessage(`Find hospitals near coordinates: ${latitude.toFixed(4)}, ${longitude.toFixed(4)}`);
                },
                (error) => {
                    let errorMessage = 'Unable to get your location. ';
                    switch(error.code) {
                        case error.PERMISSION_DENIED:
                            errorMessage += 'Please enable location access in your browser settings.';
                            break;
                        case error.POSITION_UNAVAILABLE:
                            errorMessage += 'Location information is unavailable.';
                            break;
                        case error.TIMEOUT:
                            errorMessage += 'Location request timed out.';
                            break;
                    }

                    this.addMessage(errorMessage + ' Searching for general hospital information instead.', 'bot', 'location_error');
                    this.sendQuickMessage('Find hospitals in my area');
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 300000
                }
            );
        } else {
            this.addMessage(
                'Geolocation is not supported by this browser. Searching for general hospital information.',
                'bot',
                'location_unsupported'
            );
            this.sendQuickMessage('Find hospitals in my area');
        }
    }

    // Update suggestions with follow-up options
    updateSuggestionsWithFollowUp(suggestions) {
        if (suggestions.length === 0) return;

        const suggestionsContainer = document.getElementById('inputSuggestions');
        if (suggestionsContainer) {
            suggestionsContainer.innerHTML = suggestions.map(suggestion =>
                `<span class="suggestion" onclick="applySuggestion('${suggestion}')">${suggestion}</span>`
            ).join('');

            // Auto-clear suggestions after 10 seconds
            setTimeout(() => {
                if (suggestionsContainer) {
                    suggestionsContainer.innerHTML = '';
                }
            }, 10000);
        }
    }

    // Enhanced settings functionality
    toggleSettings() {
        const modal = document.getElementById('settingsModal');
        modal.classList.toggle('active');
    }

    // Add quick action help tooltip
    addQuickActionHelp() {
        const quickActionsPanel = document.querySelector('.quick-actions-panel');
        if (quickActionsPanel) {
            const helpText = document.createElement('div');
            helpText.className = 'quick-actions-help';
            helpText.innerHTML = `
                <i class="fas fa-keyboard"></i>
                <span>Tip: Use Ctrl+1-6 for quick shortcuts</span>
            `;
            quickActionsPanel.appendChild(helpText);
        }
    }

    // Enhanced voice input with better error handling
    startVoiceInput() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = 'en-US';
            recognition.continuous = false;
            recognition.interimResults = false;

            const micIcon = document.querySelector('[onclick="startVoiceInput()"] i');

            recognition.onstart = () => {
                if (micIcon) micIcon.className = 'fas fa-microphone-slash';
                this.addMessage('🎤 Listening... Speak now!', 'bot', 'voice_listening');
                console.log('🎤 Voice recognition started');
            };

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                this.messageInput.value = transcript;
                this.sendButton.disabled = false;
                this.addMessage(`🎤 Voice input: "${transcript}"`, 'bot', 'voice_result');
                console.log('🎤 Voice input:', transcript);

                // Auto-send after a short delay
                setTimeout(() => {
                    this.sendMessage();
                }, 1000);
            };

            recognition.onend = () => {
                if (micIcon) micIcon.className = 'fas fa-microphone';
                console.log('🎤 Voice recognition ended');
            };

            recognition.onerror = (event) => {
                if (micIcon) micIcon.className = 'fas fa-microphone';
                console.error('🎤 Voice recognition error:', event.error);

                let errorMessage = 'Voice recognition error: ';
                switch(event.error) {
                    case 'not-allowed':
                        errorMessage += 'Microphone access denied. Please allow microphone access.';
                        break;
                    case 'no-speech':
                        errorMessage += 'No speech detected. Please try again.';
                        break;
                    case 'network':
                        errorMessage += 'Network error. Please check your connection.';
                        break;
                    default:
                        errorMessage += 'Please try again or type your message.';
                }

                this.addMessage(errorMessage, 'bot', 'voice_error');
            };

            recognition.start();
        } else {
            this.addMessage(
                "Voice recognition is not supported in this browser. Please type your message instead.",
                'bot',
                'voice_unsupported'
            );
        }
    }
}

// Global functions for HTML onclick handlers
function sendQuickMessage(message) {
    if (window.chatbot) {
        window.chatbot.sendQuickMessage(message);
    }
}

function clearChat() {
    if (window.chatbot) {
        window.chatbot.clearChat();
    }
}

function toggleTheme() {
    if (window.chatbot) {
        window.chatbot.toggleTheme();
    }
}

function exportChat() {
    if (window.chatbot) {
        window.chatbot.exportChat();
    }
}

function applySuggestion(text) {
    const input = document.getElementById('messageInput');
    if (input) {
        input.value = text;
        input.focus();
        if (window.chatbot) {
            window.chatbot.sendButton.disabled = false;
        }
    }
}

function setActiveTab(tabName) {
    if (window.chatbot) {
        window.chatbot.setActiveTab(tabName);
    }
}

function toggleSidebar() {
    if (window.chatbot) {
        window.chatbot.toggleSidebar();
    }
}

function toggleQuickActions() {
    if (window.chatbot) {
        window.chatbot.toggleQuickActions();
    }
}

function toggleSettings() {
    if (window.chatbot) {
        window.chatbot.toggleSettings();
    }
}

function startVoiceInput() {
    if (window.chatbot) {
        window.chatbot.startVoiceInput();
    }
}

// Backup global functions (in case onclick attributes are still used)
window.sendQuickMessage = function(message) {
    if (window.chatbot) {
        window.chatbot.sendQuickMessage(message);
    }
};

window.clearChat = function() {
    if (window.chatbot) {
        window.chatbot.clearChat();
    }
};

window.toggleTheme = function() {
    if (window.chatbot) {
        window.chatbot.toggleTheme();
    }
};

window.exportChat = function() {
    if (window.chatbot) {
        window.chatbot.exportChat();
    }
};

window.applySuggestion = function(text) {
    const input = document.getElementById('messageInput');
    if (input) {
        input.value = text;
        input.focus();
        if (window.chatbot) {
            window.chatbot.sendButton.disabled = false;
        }
    }
};

window.setActiveTab = function(tabName) {
    if (window.chatbot) {
        window.chatbot.setActiveTab(tabName);
    }
};

window.toggleSidebar = function() {
    if (window.chatbot) {
        window.chatbot.toggleSidebar();
    }
};

window.toggleQuickActions = function() {
    if (window.chatbot) {
        window.chatbot.toggleQuickActions();
    }
};

window.toggleSettings = function() {
    if (window.chatbot) {
        window.chatbot.toggleSettings();
    }
};

window.startVoiceInput = function() {
    if (window.chatbot) {
        window.chatbot.startVoiceInput();
    }
};

window.attachFile = function() {
    alert('File attachment feature coming soon! 📎\n\nThis feature will allow you to:\n• Upload medical reports\n• Share health documents\n• Attach images for analysis');
};

window.handleKeyPress = function(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        if (window.chatbot) {
            window.chatbot.sendMessage();
        }
    }
};

window.sendMessage = function() {
    if (window.chatbot) {
        window.chatbot.sendMessage();
    }
};

// Additional global functions for new features
window.findNearestHospital = function() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                if (window.chatbot) {
                    window.chatbot.sendQuickMessage(`Find hospitals near my location: ${lat.toFixed(4)}, ${lon.toFixed(4)}`);
                }
            },
            function(error) {
                console.error('Geolocation error:', error);
                if (window.chatbot) {
                    window.chatbot.sendQuickMessage('Find nearest hospital to my area');
                }
            }
        );
    } else {
        if (window.chatbot) {
            window.chatbot.sendQuickMessage('Find nearest hospital to my area');
        }
    }
};

window.searchHospitals = function() {
    const location = document.getElementById('locationInput').value;
    if (location.trim()) {
        if (window.chatbot) {
            window.chatbot.sendQuickMessage(`Find hospitals near ${location}`);
        }
    } else {
        alert('Please enter a location to search for hospitals');
    }
};

window.getDirections = function(hospitalName) {
    const message = `Get directions to ${hospitalName}`;
    if (window.chatbot) {
        window.chatbot.sendQuickMessage(message);
    }
};

window.callHospital = function(phoneNumber) {
    if (confirm(`Call ${phoneNumber}?`)) {
        window.open(`tel:${phoneNumber}`);
    }
};

// Global utility functions for Indian number formatting
window.formatIndianNumber = function(number) {
    if (window.chatbot) {
        return window.chatbot.convertToIndianFormat(number.toString());
    }
    return number.toString();
};

window.formatIndianCurrency = function(amount) {
    if (window.chatbot) {
        return window.chatbot.formatIndianCurrency(amount.toString());
    }
    return `₹${amount}`;
};

// Enhanced quick action global function
window.handleQuickAction = function(actionType) {
    if (window.chatbot) {
        window.chatbot.handleQuickAction(actionType);
    }
};

// Enhanced location request function
window.requestLocationForHospitals = function() {
    if (window.chatbot) {
        window.chatbot.requestLocationForHospitals();
    }
};

// Add demonstration of Indian number formatting in console
window.demonstrateIndianNumbering = function() {
    const examples = [
        { number: '1000', description: 'One Thousand' },
        { number: '10000', description: 'Ten Thousand' },
        { number: '100000', description: 'One Lakh' },
        { number: '1000000', description: 'Ten Lakh' },
        { number: '10000000', description: 'One Crore' },
        { number: '100000000', description: 'Ten Crore' }
    ];

    console.log('🔢 Indian Number Formatting Examples:');
    examples.forEach(example => {
        const formatted = window.formatIndianNumber(example.number);
        console.log(`${example.number} → ${formatted} (${example.description})`);
    });

    console.log('\n💰 Indian Currency Formatting Examples:');
    examples.forEach(example => {
        const formatted = window.formatIndianCurrency(example.number);
        console.log(`${example.number} → ${formatted} (${example.description})`);
    });
};

// Initialize the chatbot when the page loads
document.addEventListener('DOMContentLoaded', function() {
    window.chatbot = new HealthChatbot();

    // Setup theme button handlers in settings modal
    document.querySelectorAll('.theme-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const theme = btn.dataset.theme;
            if (theme !== 'auto') {
                window.chatbot.setTheme(theme);
            }
        });
    });

    // Setup suggestion clicks
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('suggestion')) {
            const text = e.target.textContent;
            window.applySuggestion(text);
        }
    });

    // Setup modal close functionality
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            e.target.classList.remove('active');
        }
    });

    console.log('🏥 HealthBot AI initialized successfully!');
    console.log('💡 All buttons should now be working!');
    console.log('🔧 Try clicking any button - they are now properly connected');
    console.log('🔢 Indian number formatting is now active!');

    // Demonstrate Indian number formatting
    if (window.demonstrateIndianNumbering) {
        window.demonstrateIndianNumbering();
    }

    // Add a welcome message with Indian number formatting example
    setTimeout(() => {
        if (window.chatbot) {
            const exampleMessage = `Welcome to HealthBot AI! 🇮🇳

I now support Indian number formatting:
• ${window.formatIndianNumber('100000')} patients served
• ${window.formatIndianCurrency('500000')} in healthcare savings
• ${window.formatIndianNumber('25000')} consultations completed

Try asking about health costs and I'll format numbers in Indian style!`;

            // Only add if no other messages exist besides welcome
            const messages = document.querySelectorAll('.message');
            if (messages.length <= 1) {
                setTimeout(() => {
                    window.chatbot.addMessage(exampleMessage, 'bot', 'welcome_indian_numbers');
                }, 2000);
            }
        }
    }, 3000);
});
