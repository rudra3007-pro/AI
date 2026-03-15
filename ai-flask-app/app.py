from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from groq import Groq
from authlib.integrations.flask_client import OAuth
import os
import json
import time

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-to-a-random-string")

# ── Groq client ──
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
conversation_history = {}

# ── Google OAuth ──
oauth = OAuth(app)
google = oauth.register(
    name="google",
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

# ── Chat history storage ──
HISTORY_DIR = "chat_history"
os.makedirs(HISTORY_DIR, exist_ok=True)

def safe_id(s):
    return "".join(c for c in s if c.isalnum() or c in "-_@.")

def user_history_dir(user_email):
    """Each user gets their own subfolder."""
    path = os.path.join(HISTORY_DIR, safe_id(user_email))
    os.makedirs(path, exist_ok=True)
    return path

def history_path(user_email, session_id):
    return os.path.join(user_history_dir(user_email), f"{safe_id(session_id)}.json")

def get_current_user():
    return session.get("user")

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not get_current_user():
            return jsonify({"error": "Not logged in", "redirect": "/login"}), 401
        return f(*args, **kwargs)
    return decorated


# ── Auth routes ──

@app.route("/login")
def login():
    redirect_uri = url_for("callback", _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route("/callback")
def callback():
    token = google.authorize_access_token()
    user_info = token.get("userinfo")
    session["user"] = {
        "email": user_info["email"],
        "name": user_info.get("name", user_info["email"]),
        "picture": user_info.get("picture", "")
    }
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/me")
def me():
    user = get_current_user()
    if user:
        return jsonify(user)
    return jsonify(None)


# ── Main app routes ──

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
@login_required
def chat():
    data = request.json
    user_message = data.get("message", "")
    session_id = data.get("session_id", "default")
    user_email = get_current_user()["email"]

    key = f"{user_email}:{session_id}"
    if key not in conversation_history:
        conversation_history[key] = []

    conversation_history[key].append({
        "role": "user",
        "content": user_message
    })

    messages = [
        {"role": "system", "content": "You are a helpful, friendly, and knowledgeable AI assistant. Be concise but thorough."},
        *conversation_history[key]
    ]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=1024
    )

    reply = response.choices[0].message.content

    conversation_history[key].append({
        "role": "assistant",
        "content": reply
    })

    return jsonify({"reply": reply})

@app.route("/clear", methods=["POST"])
@login_required
def clear():
    data = request.json
    session_id = data.get("session_id", "default")
    user_email = get_current_user()["email"]
    key = f"{user_email}:{session_id}"
    conversation_history.pop(key, None)
    return jsonify({"status": "cleared"})


# ── History routes ──

@app.route("/history/save", methods=["POST"])
@login_required
def history_save():
    data = request.json
    session_id = data.get("session_id")
    if not session_id:
        return jsonify({"error": "Missing session_id"}), 400

    user_email = get_current_user()["email"]
    with open(history_path(user_email, session_id), "w") as f:
        json.dump({
            "session_id": session_id,
            "title": data.get("title", "New Chat"),
            "messages": data.get("messages", []),
            "updatedAt": int(time.time() * 1000)
        }, f)

    return jsonify({"ok": True})

@app.route("/history/list", methods=["GET"])
@login_required
def history_list():
    user_email = get_current_user()["email"]
    folder = user_history_dir(user_email)
    chats = []
    for fname in os.listdir(folder):
        if fname.endswith(".json"):
            try:
                with open(os.path.join(folder, fname)) as f:
                    c = json.load(f)
                    chats.append({
                        "session_id": c["session_id"],
                        "title": c.get("title", "Untitled"),
                        "updatedAt": c.get("updatedAt", 0)
                    })
            except Exception:
                pass
    chats.sort(key=lambda x: x["updatedAt"], reverse=True)
    return jsonify(chats)

@app.route("/history/load", methods=["GET"])
@login_required
def history_load():
    session_id = request.args.get("session_id")
    if not session_id:
        return jsonify({"error": "Missing session_id"}), 400

    user_email = get_current_user()["email"]
    path = history_path(user_email, session_id)
    if not os.path.exists(path):
        return jsonify({}), 404

    with open(path) as f:
        return jsonify(json.load(f))

@app.route("/history/delete", methods=["POST"])
@login_required
def history_delete():
    session_id = request.json.get("session_id")
    if not session_id:
        return jsonify({"error": "Missing session_id"}), 400

    user_email = get_current_user()["email"]
    path = history_path(user_email, session_id)
    if os.path.exists(path):
        os.remove(path)

    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
