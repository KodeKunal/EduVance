// js/ai_tutor.js

// Base URL of your backend API
const API_BASE_URL = 'https://your-backend-api.com/api';

// Function to send a message to the AI tutor
async function sendMessage(event) {
    event.preventDefault();

    const inputField = document.getElementById('ai-input');
    const message = inputField.value.trim();
    if (!message) return;

    appendMessage('user', message);
    inputField.value = '';

    const token = localStorage.getItem('token');

    try {
        const response = await fetch(`${API_BASE_URL}/ai/tutor`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ message })
        });

        const data = await response.json();

        if (response.ok) {
            appendMessage('ai', data.reply);
        } else {
            appendMessage('ai', 'Sorry, I could not process your request.');
        }
    } catch (error) {
        console.error('Error:', error);
        appendMessage('ai', 'An error occurred while communicating with the AI tutor.');
    }
}

// Function to append messages to the chat window
function appendMessage(role, content) {
    const chatWindow = document.getElementById('chat-window');
    const messageDiv = document.createElement('div');

    if (role === 'user') {
        messageDiv.className = 'flex items-end gap-3 justify-end';
        messageDiv.innerHTML = `
            <div class="flex flex-col gap-1 items-end">
                <p class="text-[#647987] text-xs font-normal">You</p>
                <p class="text-base font-normal px-4 py-3 bg-[#47a6e6] text-white rounded-xl">
                    ${content}
                </p>
            </div>
            <div
                class="bg-center bg-no-repeat aspect-square bg-cover rounded-full w-10 shrink-0"
                style='background-image: url("https://cdn.usegalileo.ai/stability/56422f9a-cd60-425d-b086-62a619d3102a.png");'
                aria-label="User Profile"
                role="img"
            ></div>
        `;
    } else if (role === 'ai') {
        messageDiv.className = 'flex items-end gap-3';
        messageDiv.innerHTML = `
            <div
                class="bg-center bg-no-repeat aspect-square bg-cover rounded-full w-10 shrink-0"
                style='background-image: url("https://cdn.usegalileo.ai/stability/46db6c1d-4af0-43a3-8803-419b979052c8.png");'
                aria-label="AI Tutor"
                role="img"
            ></div>
            <div class="flex flex-col gap-1 items-start">
                <p class="text-[#647987] text-xs font-normal">AI Tutor</p>
                <p class="text-base font-normal px-4 py-3 bg-[#f0f3f4] text-[#111517] rounded-xl">
                    ${content}
                </p>
            </div>
        `;
    }

    chatWindow.appendChild(messageDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

// Function to initialize AI Tutor chat
function initAITutor() {
    const chatForm = document.getElementById('ai-chat-form');
    if (chatForm) {
        chatForm.addEventListener('submit', sendMessage);
    }

    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'index.html';
    }
}

// Initialize AI Tutor on page load
document.addEventListener('DOMContentLoaded', initAITutor);
