# Nexus AI 🤖

A clean, minimal AI chat app built with **Flask** and **Groq** (Llama 3.3 70B). Inspired by the simplicity of ChatGPT and Claude.

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0+-black?style=flat-square&logo=flask)
![Groq](https://img.shields.io/badge/Powered%20by-Groq-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

## Features

- 💬 Multi-turn conversation with memory per session
- 🎤 Voice input via microphone (speech-to-text)
- 🌙 Clean dark UI
- ⚡ Fast responses via Groq API (completely free)
- 🔄 New chat / clear conversation

## Demo

> Ask anything — code, writing, explanations, analysis and more.

## Getting Started

### Prerequisites

- Python 3.8+
- A free [Groq API key](https://console.groq.com)

### Installation

1. **Clone the repo**
   ```bash
   git clone https://github.com/yourusername/nexus-ai.git
   cd nexus-ai
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Add your Groq API key**

   Open `app.py` and replace the placeholder on line 5:
   ```python
   client = Groq(api_key="YOUR_GROQ_API_KEY_HERE")
   ```

4. **Run the app**
   ```bash
   python app.py
   ```

5. **Open in browser**
   ```
   http://localhost:5000
   ```

## Project Structure

```
nexus-ai/
├── app.py              # Flask backend
├── requirements.txt    # Dependencies
├── templates/
│   └── index.html      # Frontend UI
└── README.md
```

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python + Flask |
| AI Model | Llama 3.3 70B |
| API Provider | Groq (free tier) |
| Frontend | Vanilla HTML/CSS/JS |
| Voice Input | Web Speech API |

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Serves the chat UI |
| POST | `/chat` | Sends a message and returns AI reply |
| POST | `/clear` | Clears conversation history for a session |

## Voice Input

Click the **microphone** button in the input box to speak your message. It automatically sends once you stop talking. Works in **Chrome and Edge** only (Firefox does not support the Web Speech API).

## Free Tier Limits (Groq)

- 30 requests per minute
- 14,400 requests per day
- No credit card required

## Contributing

Pull requests are welcome! Feel free to open an issue for bugs or feature requests.

## License

MIT License — use it however you like.

---

Built with ❤️ using Flask + Groq
