import os
import logging
from flask import Flask, request, jsonify, render_template
from google import genai
from google.genai import types

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# API key is read from environment variable — never hardcode it.
# Set GEMINI_API_KEY in your environment / cloud secret config.
API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL_NAME = os.environ.get("MODEL_NAME", "gemini-3.6-flash")  

SYSTEM_PROMPT = (
    "You are a helpful, friendly assistant embedded in a web app. "
    "Keep answers concise and clear."
)

client = genai.Client(api_key=API_KEY) if API_KEY else None

# In-memory conversation store (per session_id).
# For production, swap this for Redis / Firestore / a database.
conversations = {}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    """Health check endpoint used by cloud load balancers."""
    return jsonify({"status": "ok"}), 200


@app.route("/api/chat", methods=["POST"])
def chat():
    if client is None:
        return jsonify({"error": "Server missing GEMINI_API_KEY"}), 500

    data = request.get_json(force=True)
    user_message = (data.get("message") or "").strip()
    session_id = data.get("session_id", "default")

    if not user_message:
        return jsonify({"error": "message is required"}), 400

    # Gemini history format: [{"role": "user"/"model", "parts": [{"text": ...}]}, ...]
    history = conversations.setdefault(session_id, [])

    # Cap history length to control token usage.
    trimmed_history = history[-20:]

    try:
        chat_session = client.chats.create(
            model=MODEL_NAME,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
            history=trimmed_history,
        )
        response = chat_session.send_message(user_message)
        reply_text = response.text
    except Exception as e:
        logger.exception("Gemini API call failed")
        return jsonify({"error": str(e)}), 502

    history.append({"role": "user", "parts": [{"text": user_message}]})
    history.append({"role": "model", "parts": [{"text": reply_text}]})
    conversations[session_id] = history

    return jsonify({"reply": reply_text})


@app.route("/api/reset", methods=["POST"])
def reset():
    session_id = (request.get_json(force=True) or {}).get("session_id", "default")
    conversations.pop(session_id, None)
    return jsonify({"status": "reset"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
