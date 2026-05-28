const chatBox = document.querySelector(".chat-box");
const form = document.querySelector("#chat-form");
const input = document.querySelector("#message-input");
const button = document.querySelector("button");

const SESSION_KEY = "momo_session_id";

function getSessionId() {
    let sessionId = localStorage.getItem(SESSION_KEY);
    if (!sessionId) {
        sessionId = crypto.randomUUID();
        localStorage.setItem(SESSION_KEY, sessionId);
    }
    return sessionId;
}

function setSessionId(sessionId) {
    if (sessionId) {
        localStorage.setItem(SESSION_KEY, sessionId);
    }
}

function appendMessage(role, content) {
    const div = document.createElement("div");
    div.className = "message " + role;
    div.innerText = content;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
    return div;
}

let historyLoaded = false;

async function loadHistory() {
    if (historyLoaded) return;
    historyLoaded = true;

    const sessionId = getSessionId();

    try {
        const response = await fetch(
            `/history?session_id=${encodeURIComponent(sessionId)}`
        );
        const messages = await response.json();

        chatBox.innerHTML = "";

        messages.forEach((msg) => {
            appendMessage(msg.role, msg.content);
        });
    } catch (error) {
        console.error("History load error:", error);
    }
}

async function sendMessage(message) {
    const response = await fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            message,
            session_id: getSessionId(),
        }),
    });

    const result = await response.json();

    if (result.session_id) {
        setSessionId(result.session_id);
    }

    return result;
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const message = input.value.trim();
    if (!message) return;

    appendMessage("user", message);
    input.value = "";

    const loadingMsg = appendMessage("assistant", "Momo is thinking...");

    input.disabled = true;
    button.disabled = true;

    try {
        const result = await sendMessage(message);
        loadingMsg.innerText = result.reply || "（无回复）";
    } catch (error) {
        loadingMsg.innerText = "出错了，请稍后再试。";
        console.error(error);
    }

    input.disabled = false;
    button.disabled = false;
    input.focus();
});

loadHistory();
