from flask import Flask, render_template, request, jsonify
from groq import Groq
import os
import json
import time

app = Flask(__name__)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
conversation_history = {}

# ── Chat history storage setup ──
HISTORY_DIR = "chat_history"
os.makedirs(HISTORY_DIR, exist_ok=True)

def history_path(session_id):
    # Sanitize session_id to prevent path traversal
    safe_id = "".join(c for c in session_id if c.isalnum() or c in "-_")
    return os.path.join(HISTORY_DIR, f"{safe_id}.json")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    session_id = data.get("session_id", "default")

    if session_id not in conversation_history:
        conversation_history[session_id] = []

    conversation_history[session_id].append({
        "role": "user",
        "content": user_message
    })

    messages = [
        {"role": "system", "content": "You are a helpful, friendly, and knowledgeable AI assistant. Be concise but thorough."},
        *conversation_history[session_id]
    ]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=1024
    )

    reply = response.choices[0].message.content

    conversation_history[session_id].append({
        "role": "assistant",
        "content": reply
    })

    return jsonify({"reply": reply})


@app.route("/clear", methods=["POST"])
def clear():
    data = request.json
    session_id = data.get("session_id", "default")
    conversation_history.pop(session_id, None)
    return jsonify({"status": "cleared"})


# ── History routes ──

@app.route("/history/save", methods=["POST"])
def history_save():
    data = request.json
    session_id = data.get("session_id")
    if not session_id:
        return jsonify({"error": "Missing session_id"}), 400

    with open(history_path(session_id), "w") as f:
        json.dump({
            "session_id": session_id,
            "title": data.get("title", "New Chat"),
            "messages": data.get("messages", []),
            "updatedAt": int(time.time() * 1000)
        }, f)

    return jsonify({"ok": True})


@app.route("/history/list", methods=["GET"])
def history_list():
    chats = []
    for fname in os.listdir(HISTORY_DIR):
        if fname.endswith(".json"):
            try:
                with open(os.path.join(HISTORY_DIR, fname)) as f:
                    c = json.load(f)
                    chats.append({
                        "session_id": c["session_id"],
                        "title": c.get("title", "Untitled"),
                        "updatedAt": c.get("updatedAt", 0)
                    })
            except Exception:
                pass  # Skip corrupted files

    chats.sort(key=lambda x: x["updatedAt"], reverse=True)
    return jsonify(chats)


@app.route("/history/load", methods=["GET"])
def history_load():
    session_id = request.args.get("session_id")
    if not session_id:
        return jsonify({"error": "Missing session_id"}), 400

    path = history_path(session_id)
    if not os.path.exists(path):
        return jsonify({}), 404

    with open(path) as f:
        return jsonify(json.load(f))


@app.route("/history/delete", methods=["POST"])
def history_delete():
    session_id = request.json.get("session_id")
    if not session_id:
        return jsonify({"error": "Missing session_id"}), 400

    path = history_path(session_id)
    if os.path.exists(path):
        os.remove(path)

    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
