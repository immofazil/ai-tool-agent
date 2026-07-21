const SESSION_ID = "capstone-session-" + Math.floor(Math.random() * 100000);

async function sendMessage() {
    const inputField = document.getElementById('user-input');
    const tokenField = document.getElementById('bearer-token');
    const message = inputField.value.trim();
    const token = tokenField.value.trim();

    if (!message) return;

    // Render User Message
    renderMessage(message, 'user');
    inputField.value = '';

    try {
        const response = await fetch('http://localhost:8000/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                session_id: SESSION_ID,
                message: message
            })
        });

        const data = await response.json();

        // Handle Guardrail & Status Code Responses
        if (!response.ok) {
            let errorText = data.detail || "Service error occurred.";
            if (response.status === 401) errorText = "Guardrail Triggered: 401 Unauthorized (Invalid Token).";
            if (response.status === 429) errorText = "Guardrail Triggered: 429 Rate Limit Exceeded (Max 5 req/min).";
            if (response.status === 422) errorText = "Guardrail Triggered: 422 Validation Error (Empty or long payload).";
            
            renderMessage(`⚠️ ${errorText}`, 'error');
            return;
        }

        // Format bot response with tool badges
        let botHtml = data.response;
        if (data.tool_executed) {
            botHtml = `<span class="badge">🛠️ Tool Executed: ${data.tool_executed}</span><br>` + botHtml;
        }

        renderMessage(botHtml, 'bot', true);

    } catch (err) {
        renderMessage("Network Error: Unable to connect to the backend API server.", 'error');
    }
}

function renderMessage(content, sender, isHtml = false) {
    const chatBox = document.getElementById('chat-box');
    const div = document.createElement('div');
    div.classList.add('msg', sender);

    if (isHtml) {
        div.innerHTML = content;
    } else {
        div.textContent = content;
    }

    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

document.getElementById('user-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});