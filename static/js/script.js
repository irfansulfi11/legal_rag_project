// Legal RAG Chatbot Frontend Logic

class LegalChatBot {
    constructor() {
        // DOM Element Selectors
        this.chatMessages = document.getElementById('chatMessages');
        this.questionInput = document.getElementById('questionInput');
        this.sendButton = document.getElementById('sendButton');
        this.statusAlert = document.getElementById('statusAlert');
        this.statusMessage = document.getElementById('statusMessage');

        // State Management
        this.isSystemReady = false;
        this.isProcessing = false;
        this.currentBotMessageElement = null;
    }

    /**
     * Initializes all event listeners and starts the system status check.
     */
    initialize() {
        // Event Listeners
        document.getElementById('chatForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });

        document.querySelectorAll('.quick-question').forEach(button => {
            button.addEventListener('click', (e) => {
                const question = e.target.getAttribute('data-question');
                this.questionInput.value = question;
                this.sendMessage();
            });
        });

        this.questionInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Initial actions
        this.addWelcomeMessage();
        this.checkSystemStatus();
    }

    /**
     * Periodically checks the backend /status endpoint until the RAG engine is ready.
     */
    async checkSystemStatus() {
        try {
            const response = await fetch('/status');
            const data = await response.json();

            if (data.status === 'ready') {
                this.isSystemReady = true;
                this.updateStatusAlert('success', `<i class="fas fa-check-circle me-2"></i>${data.message}`);
                this.updateUI(false); // Enable UI
                setTimeout(() => { this.statusAlert.style.display = 'none'; }, 3000);
            } else if (data.status === 'error') {
                this.updateStatusAlert('danger', `<i class="fas fa-exclamation-triangle me-2"></i>${data.message}`);
            } else {
                this.updateStatusAlert('info', `<i class="fas fa-spinner fa-spin me-2"></i>${data.message}`);
                setTimeout(() => this.checkSystemStatus(), 3000); // Check again in 3 seconds
            }
        } catch (error) {
            this.updateStatusAlert('danger', '<i class="fas fa-shield-virus me-2"></i>Could not connect to the server. Please refresh the page.');
        }
    }

    /**
     * Handles the entire process of sending a user's question and receiving a response.
     */
    sendMessage() {
        if (!this.isSystemReady || this.isProcessing) return;

        const question = this.questionInput.value.trim();
        if (!question) return;

        this.isProcessing = true;
        this.updateUI(true);
        this.addMessage(question, 'user');
        this.questionInput.value = '';

        // Add a placeholder for the bot's response
        this.addMessage('', 'bot', true);

        // --- CORRECTED: Use EventSource with a GET request and URL parameters ---
        const url = `/ask_stream?question=${encodeURIComponent(question)}`;
        const eventSource = new EventSource(url);

        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);

            if (data.type === 'chunk' && data.content) {
                // Append the content chunk to the bot's message bubble
                this.currentBotMessageElement.innerHTML += this.formatMessageChunk(data.content);
                this.scrollToBottom();
            } else if (data.type === 'end') {
                // Stream has ended, finalize the process
                this.finalizeResponse();
                eventSource.close();
            } else if (data.type === 'error') {
                this.currentBotMessageElement.innerHTML = `<p class="text-danger">An error occurred: ${data.error}</p>`;
                this.finalizeResponse();
                eventSource.close();
            }
        };

        eventSource.onerror = (err) => {
            console.error("EventSource failed:", err);
            this.currentBotMessageElement.innerHTML = `<p class="text-danger">A network error occurred. Could not complete the request.</p>`;
            this.finalizeResponse();
            eventSource.close();
        };
    }

    /**
     * Finalizes the bot's response and re-enables the UI.
     */
    finalizeResponse() {
        this.isProcessing = false;
        this.updateUI(false);
        this.currentBotMessageElement = null; // Clear the reference
    }

    /**
     * Adds a message to the chat interface.
     */
    addMessage(content, sender, isStreaming = false) {
        // Remove the welcome screen if it exists
        const welcomeScreen = this.chatMessages.querySelector('.welcome-screen');
        if (welcomeScreen) {
            welcomeScreen.remove();
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

        const timeString = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-${sender === 'user' ? 'user-tie' : 'robot'}"></i>
            </div>
            <div class="message-content">
                <div class="message-bubble">
                    ${isStreaming ? '<div class="typing-dots"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>' : this.formatMessageChunk(content)}
                </div>
                <div class="message-time">${timeString}</div>
            </div>
        `;

        this.chatMessages.appendChild(messageDiv);

        if (isStreaming) {
            this.currentBotMessageElement = messageDiv.querySelector('.message-bubble');
            this.currentBotMessageElement.innerHTML = ''; // Clear the typing indicator
        }

        this.scrollToBottom();
    }
    
    /**
     * Adds the initial welcome message to the chat.
     */
    addWelcomeMessage() {
        // This function is now handled by the welcome screen in index.html, 
        // but we'll leave the method in case it's needed for a "new chat" button.
        // It's called during initialization but won't do anything if the welcome screen is already there.
    }

    /**
     * Formats a chunk of text for display, handling newlines and basic markdown.
     */
    formatMessageChunk(content) {
        return content
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
    }

    /**
     * Updates the UI elements based on the processing state.
     */
    updateUI(isProcessing) {
        this.isProcessing = isProcessing;
        this.questionInput.disabled = isProcessing || !this.isSystemReady;
        this.sendButton.disabled = isProcessing || !this.isSystemReady;

        if (isProcessing) {
            this.sendButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        } else {
            this.sendButton.innerHTML = '<i class="fas fa-arrow-up"></i>';
        }
    }

    /**
     * Updates the top status alert bar.
     */
    updateStatusAlert(type, message) {
        this.statusAlert.className = `alert alert-${type} alert-dismissible fade show`;
        this.statusMessage.innerHTML = message;
        this.statusAlert.style.display = 'block';
    }

    /**
     * Scrolls the chat container to the bottom.
     */
    scrollToBottom() {
        // MODIFIED: Use requestAnimationFrame for reliable scrolling
        requestAnimationFrame(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        });
    }
}

// Initialize the chatbot when the DOM is fully loaded.
document.addEventListener('DOMContentLoaded', () => {
    const chatBot = new LegalChatBot();
    chatBot.initialize();
});