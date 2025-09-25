// Modern Health Chatbot Class
class HealthChatbot {
    constructor() {
        console.log('🚀 HealthChatbot constructor called');
        this.apiUrl = '/api/health';
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.chatMessages = document.getElementById('chatMessages');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.connectionStatus = document.getElementById('connectionStatus');
        this.isConnected = false;
        this.currentTab = 'chat';
        this.chatHistory = [];
        this.sessionId = this.generateSessionId();
        this.rasaStatus = 'checking';

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

    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    async init() {
        console.log('🔧 Initializing HealthChatbot...');
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

            console.log('🎉 HealthChatbot initialization completed successfully!');
        } catch (error) {
            console.error('❌ HealthChatbot initialization failed:', error);
        }
    }

    async checkRasaStatus() {
        try {
            const response = await fetch(`${this.apiUrl}/rasa/status`);
            const status = await response.json();
            this.rasaStatus = status.status;
            this.updateConnectionStatus();
        } catch (error) {
            console.error('RASA status check failed:', error);
            this.rasaStatus = 'offline';
            this.updateConnectionStatus();
        }
    }

    updateConnectionStatus() {
        const statusElement = document.getElementById('connectionStatus');
        const statusDot = document.querySelector('.status-dot');

        if (this.rasaStatus === 'online') {
            statusElement.textContent = 'RASA Connected';
            statusDot.className = 'status-dot online';
        } else if (this.rasaStatus === 'offline') {
            statusElement.textContent = 'RASA Offline (Fallback Mode)';
            statusDot.className = 'status-dot offline';
        } else {
            statusElement.textContent = 'Checking RASA...';
            statusDot.className = 'status-dot checking';
        }
    }

    setupEventListeners() {
        // Input events
        this.messageInput.addEventListener('input', () => {
            this.sendButton.disabled = !this.messageInput.value.trim();
            this.updateSuggestions();
        });

        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Enhanced keyboard shortcuts for quick actions
        document.addEventListener('keydown', (e) => {
            // Only trigger if not typing in input
            if (document.activeElement !== this.messageInput && e.ctrlKey) {
                switch(e.key) {
                    case '1':
                        e.preventDefault();
                        this.handleQuickAction('symptoms');
                        break;
                    case '2':
                        e.preventDefault();
                        this.handleQuickAction('vaccines');
                        break;
                    case '3':
                        e.preventDefault();
                        this.handleQuickAction('alerts');
                        break;
                    case '4':
                        e.preventDefault();
                        this.handleQuickAction('emergency');
                        break;
                    case '5':
                        e.preventDefault();
                        this.handleQuickAction('tips');
                        break;
                    case '6':
                        e.preventDefault();
                        this.handleQuickAction('hospitals');
                        break;
                }
            }
        });

        this.sendButton.addEventListener('click', () => this.sendMessage());

        // Chat messages scroll event for scroll button
        this.chatMessages.addEventListener('scroll', () => {
            this.handleScroll();
        });

        // Theme detection
        this.detectSystemTheme();

        // Mobile responsive
        this.handleMobileView();

        // Setup all button event listeners
        this.setupButtonListeners();

        // Add quick action help tooltip
        this.addQuickActionHelp();
    }

    setupButtonListeners() {
        // Clear chat button
        const clearBtn = document.querySelector('[onclick="clearChat()"]');
        if (clearBtn) {
            clearBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.clearChat();
            });
        }

        // Theme toggle button
        const themeBtn = document.querySelector('[onclick="toggleTheme()"]');
        if (themeBtn) {
            themeBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleTheme();
            });
        }

        // Export chat button
        const exportBtn = document.querySelector('[onclick="exportChat()"]');
        if (exportBtn) {
            exportBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.exportChat();
            });
        }

        // Quick action buttons
        document.querySelectorAll('[onclick^="sendQuickMessage"]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const message = btn.getAttribute('onclick').match(/'([^']+)'/)[1];
                this.sendQuickMessage(message);
            });
        });

        // Navigation buttons
        document.querySelectorAll('[onclick^="setActiveTab"]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const tabName = btn.getAttribute('onclick').match(/'([^']+)'/)[1];
                this.setActiveTab(tabName);
            });
        });

        // Sidebar toggle
        const sidebarToggle = document.querySelector('[onclick="toggleSidebar()"]');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleSidebar();
            });
        }

        // Settings toggle
        const settingsBtn = document.querySelector('[onclick="toggleSettings()"]');
        if (settingsBtn) {
            settingsBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleSettings();
            });
        }

        // Voice input button
        const voiceBtn = document.querySelector('[onclick="startVoiceInput()"]');
        if (voiceBtn) {
            voiceBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.startVoiceInput();
            });
        }

        // Quick actions collapse
        const collapseBtn = document.querySelector('[onclick="toggleQuickActions()"]');
        if (collapseBtn) {
            collapseBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleQuickActions();
            });
        }

        // Scroll to bottom button
        const scrollBtn = document.getElementById('scrollToBottom');
        if (scrollBtn) {
            scrollBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.scrollToBottom();
            });
        }
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

    showTypingIndicator() {
        this.typingIndicator.style.display = 'flex';
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        this.typingIndicator.style.display = 'none';
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;

        // Add user message to chat
        this.addMessage(message, 'user');
        this.messageInput.value = '';
        this.sendButton.disabled = true;

        // Show typing indicator
        this.showTyping();

        try {
            // Send to RASA-powered backend
            const response = await fetch(`${this.apiUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    sender: 'user',
                    session_id: this.sessionId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // Hide typing indicator
            this.hideTyping();

            // Add bot response with enhanced formatting
            this.addBotMessage(data);

            // Save to chat history
            this.chatHistory.push({
                user: message,
                bot: data.response,
                timestamp: new Date().toISOString(),
                source: data.source
            });

            this.saveChatHistory();

        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTyping();

            // Fallback response
            this.addMessage(
                "I'm having trouble connecting to the server. Please check your connection and try again. For medical emergencies, please call your local emergency number immediately.",
                'bot'
            );
        }
    }

    addBotMessage(data) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot-message';

        const timestamp = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});

        let sourceIndicator = '';
        if (data.source === 'rasa') {
            sourceIndicator = '<span class="source-indicator rasa" title="Powered by RASA AI">🤖 RASA</span>';
        } else if (data.source === 'fallback') {
            sourceIndicator = '<span class="source-indicator fallback" title="Fallback response">⚡ Fallback</span>';
        }

        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="message-header">
                    <span class="sender-name">HealthBot AI</span>
                    <span class="message-time">${timestamp}</span>
                    ${sourceIndicator}
                </div>
                <div class="message-text">
                    ${this.formatBotResponse(data.response)}
                </div>
                ${this.renderButtons(data.buttons)}
                ${this.renderQuickReplies(data.quick_replies)}
            </div>
        `;

        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    formatBotResponse(text) {
        // Enhanced text formatting for better readability
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // Bold text
            .replace(/\*(.*?)\*/g, '<em>$1</em>')              // Italic text
            .replace(/`(.*?)`/g, '<code>$1</code>')            // Inline code
            .replace(/\n/g, '<br>')                            // Line breaks
            .replace(/•/g, '•')                                // Bullet points
            .replace(/🚨/g, '<span class="emergency-icon">🚨</span>')  // Emergency icons
            .replace(/💉/g, '<span class="vaccine-icon">💉</span>')    // Vaccine icons
            .replace(/🏥/g, '<span class="hospital-icon">🏥</span>')   // Hospital icons;
    }

    renderButtons(buttons) {
        if (!buttons || buttons.length === 0) return '';

        const buttonsHtml = buttons.map(button =>
            `<button class="response-button" onclick="window.chatbot.handleButtonClick('${button.payload}', '${button.title}')">
                ${button.title}
            </button>`
        ).join('');

        return `<div class="response-buttons">${buttonsHtml}</div>`;
    }

    renderQuickReplies(quickReplies) {
        if (!quickReplies || quickReplies.length === 0) return '';

        const repliesHtml = quickReplies.map(reply =>
            `<span class="quick-reply" onclick="window.chatbot.sendQuickReply('${reply}')">
                ${reply}
            </span>`
        ).join('');

        return `<div class="quick-replies">${repliesHtml}</div>`;
    }

    handleButtonClick(payload, title) {
        // Handle button clicks from RASA responses
        this.messageInput.value = payload;
        this.sendMessage();
    }

    sendQuickReply(reply) {
        // Handle quick reply clicks
        this.messageInput.value = reply;
        this.sendMessage();
    }

    addMessage(text, sender, intent = null, confidence = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

        // Determine message type for styling
        if (intent === 'ask_emergency' || text.includes('🚨')) {
            messageDiv.classList.add('emergency-message');
        } else if (intent === 'error') {
            messageDiv.classList.add('error-message');
        } else if (intent && confidence && confidence > 0.8) {
            messageDiv.classList.add('success-message');
        }

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';

        const content = document.createElement('div');
        content.className = 'message-content';

        // Add message header for better UX
        const header = document.createElement('div');
        header.className = 'message-header';
        header.innerHTML = `
            <span class="sender-name">${sender === 'user' ? 'You' : 'HealthBot AI'}</span>
            <span class="message-time">${this.getCurrentTime()}</span>
        `;

        const messageText = document.createElement('div');
        messageText.className = 'message-text';
        messageText.innerHTML = this.formatMessage(text);

        content.appendChild(header);
        content.appendChild(messageText);
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);

        // Add to chat and scroll
        this.chatMessages.appendChild(messageDiv);

        // Check if user is near bottom before auto-scrolling
        const { scrollTop, scrollHeight, clientHeight } = this.chatMessages;
        const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;

        if (isNearBottom || sender === 'user') {
            // Auto-scroll if user is near bottom or if it's user's message
            this.scrollToBottom();
        } else {
            // Show scroll button if user is not at bottom
            this.showScrollButton();
        }

        // Store in history
        this.chatHistory.push({
            text,
            sender,
            intent,
            confidence,
            timestamp: new Date().toISOString()
        });

        // Add entrance animation
        requestAnimationFrame(() => {
            messageDiv.style.opacity = '1';
            messageDiv.style.transform = 'translateY(0)';
        });
    }

    formatMessage(text) {
        // Convert line breaks to <br> tags
        let formatted = text.replace(/\n/g, '<br>');

        // Convert bullet points to proper HTML lists
        if (formatted.includes('•')) {
            const lines = formatted.split('<br>');
            let inList = false;
            let result = [];

            for (let line of lines) {
                if (line.trim().startsWith('•')) {
                    if (!inList) {
                        result.push('<ul>');
                        inList = true;
                    }
                    result.push(`<li>${line.replace('•', '').trim()}</li>`);
                } else {
                    if (inList) {
                        result.push('</ul>');
                        inList = false;
                    }
                    if (line.trim()) {
                        result.push(`<p>${line}</p>`);
                    }
                }
            }

            if (inList) {
                result.push('</ul>');
            }

            formatted = result.join('');
        } else {
            // Wrap in paragraphs
            const paragraphs = formatted.split('<br><br>');
            formatted = paragraphs.map(p => p.trim() ? `<p>${p}</p>` : '').join('');
        }

        // Format numbers to Indian numbering system
        formatted = this.formatIndianNumbers(formatted);

        // Make URLs clickable
        formatted = formatted.replace(
            /(https?:\/\/[^\s]+)/g,
            '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
        );

        // Format emergency numbers (but not convert to Indian format)
        formatted = formatted.replace(
            /(\d{3}|\d{4})/g,
            '<strong>$1</strong>'
        );

        return formatted;
    }

    // New method to format numbers in Indian numbering system
    formatIndianNumbers(text) {
        // Regular expression to match numbers (excluding phone numbers and URLs)
        const numberRegex = /(?<!\d)[1-9]\d{2,}(?!\.\w)/g;

        return text.replace(numberRegex, (match) => {
            // Skip if it's likely a phone number, year, or emergency number
            if (match.length <= 4 || /^(19|20)\d{2}$/.test(match)) {
                return match;
            }

            return this.convertToIndianFormat(match);
        });
    }

    // Convert number to Indian format (lakhs and crores)
    convertToIndianFormat(number) {
        const num = parseInt(number);

        if (num < 1000) {
            return num.toString();
        }

        // Convert to Indian numbering system
        const numStr = num.toString();
        let result = '';
        let count = 0;

        // Process from right to left
        for (let i = numStr.length - 1; i >= 0; i--) {
            if (count === 3 || (count > 3 && (count - 3) % 2 === 0)) {
                result = ',' + result;
            }
            result = numStr[i] + result;
            count++;
        }

        return result;
    }

    // Add method to format currency in Indian style
    formatIndianCurrency(amount) {
        const formatted = this.convertToIndianFormat(amount);
        return `₹${formatted}`;
    }

    getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
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

// Global scroll to bottom function
window.scrollToBottom = function() {
    if (window.chatbot) {
        window.chatbot.scrollToBottom();
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

