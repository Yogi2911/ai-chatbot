
const chatLog = document.getElementById("chat-log");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");

console.log("SCRIPT LOADED");
console.log("chatForm:", chatForm);
console.log("chatInput:", chatInput);
console.log("chatLog:", chatLog);

// Compatible session ID
const sessionId =
  Date.now().toString() +
  "-" +
  Math.random().toString(36).substring(2);

function appendMessage(text, sender) {
  const div = document.createElement("div");
  div.className = `msg ${sender}`;
  div.textContent = text;
  chatLog.appendChild(div);
  chatLog.scrollTop = chatLog.scrollHeight;
}

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  console.log("SUBMIT EVENT FIRED");

  const message = chatInput.value.trim();

  if (!message) return;

  console.log("MESSAGE:", message);

  appendMessage(message, "user");

  chatInput.value = "";
  chatInput.disabled = true;

  try {
    console.log("SENDING REQUEST...");

    const res = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        message: message,
        session_id: sessionId
      })
    });

    console.log("RESPONSE STATUS:", res.status);

    const data = await res.json();

    console.log("RESPONSE DATA:", data);

    if (data.error) {
      appendMessage(`Error: ${data.error}`, "bot");
    } else {
      appendMessage(data.reply, "bot");
    }

  } catch (err) {
    console.error("REQUEST ERROR:", err);
    appendMessage("Network error — please try again.", "bot");
  } finally {
    chatInput.disabled = false;
    chatInput.focus();
  }
});
