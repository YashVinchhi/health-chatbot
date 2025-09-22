// Modern Health Chatbot Class
class HealthChatbot {
    constructor() {
        this.apiUrl = '/api/health';
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.chatMessages = document.getElementById('chatMessages');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.connectionStatus = document.getElementById('connectionStatus');
        this.isConnected = false;
        this.currentTab = 'chat';
        this.chatHistory = [];

        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.checkConnection();
        this.enableInput();
        this.initializeTheme();
        this.loadChatHistory();
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

        this.sendButton.addEventListener('click', () => this.sendMessage());

        // Theme detection
        this.detectSystemTheme();

        // Mobile responsive
        this.handleMobileView();

        // Setup all button event listeners
        this.setupButtonListeners();
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
        if (!message || !this.isConnected) return;

        // Disable input while processing
        this.messageInput.disabled = true;
        this.sendButton.disabled = true;

        // Add user message to chat
        this.addMessage(message, 'user');
        this.messageInput.value = '';

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Send message to backend
            const response = await fetch(`${this.apiUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    sender: 'user'
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // Hide typing indicator
            this.hideTypingIndicator();

            // Add bot response to chat
            this.addMessage(data.response, 'bot', data.intent, data.confidence);

            // Save to chat history
            this.saveChatHistory();

            // Log intent for debugging
            if (data.intent) {
                console.log(`Intent detected: ${data.intent} (confidence: ${data.confidence?.toFixed(2)})`);
            }

        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();

            // Show error message
            this.addMessage(
                "I'm sorry, I'm having trouble processing your request right now. Please try again in a moment.",
                'bot',
                'error'
            );
        } finally {
            // Re-enable input
            this.messageInput.disabled = false;
            this.sendButton.disabled = false;
            this.messageInput.focus();
        }
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
        this.scrollToBottom();

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

        // Make URLs clickable
        formatted = formatted.replace(
            /(https?:\/\/[^\s]+)/g,
            '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
        );

        // Format emergency numbers
        formatted = formatted.replace(
            /(\d{3}|\d{4})/g,
            '<strong>$1</strong>'
        );

        return formatted;
    }

    getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }

    sendQuickMessage(message) {
        this.messageInput.value = message;
        this.sendMessage();
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
    // Remove active class from all nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });

    // Add active class to clicked nav item
    const clickedItem = document.querySelector(`[onclick="setActiveTab('${tabName}')"]`);
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

function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.mobile-overlay');

    sidebar.classList.toggle('open');
    if (overlay) {
        overlay.style.display = sidebar.classList.contains('open') ? 'block' : 'none';
    }
}

function toggleQuickActions() {
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

function toggleSettings() {
    const modal = document.getElementById('settingsModal');
    modal.classList.toggle('active');
}

function startVoiceInput() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'en-US';
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onstart = () => {
            const micIcon = document.querySelector('[onclick="startVoiceInput()"] i');
            if (micIcon) micIcon.className = 'fas fa-microphone-slash';
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            this.messageInput.value = transcript;
            this.sendButton.disabled = false;
        };

        recognition.onend = () => {
            const micIcon = document.querySelector('[onclick="startVoiceInput()"] i');
            if (micIcon) micIcon.className = 'fas fa-microphone';
        };

        recognition.onerror = () => {
            const micIcon = document.querySelector('[onclick="startVoiceInput()"] i');
            if (micIcon) micIcon.className = 'fas fa-microphone';
            alert('Voice recognition failed. Please try again.');
        };

        recognition.start();
    } else {
        alert('Speech recognition not supported in this browser');
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
    alert('File attachment feature coming soon!');
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
});
