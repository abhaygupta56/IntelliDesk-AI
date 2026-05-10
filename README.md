<div align="center">

<img src="assets/logo.png" alt="IntelliDesk AI Logo" width="80" height="80">

# IntelliDesk AI

AI-powered desktop automation for Windows — control your PC with voice or text (English & Hinglish).

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D6?style=flat-square&logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![License: MIT](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)](LICENSE)

Quick start · Features · Commands · Configuration · Project Structure

</div>

---

## What it does

IntelliDesk AI converts natural language (typed or spoken) into desktop actions: open apps, manage files, control windows and media, send WhatsApp messages and email, run multi-step automations, generate code locally, and monitor your room via webcam alerts.

Press `Ctrl+Space` to open the spotlight command palette (GUI). Use `--cli` for a terminal interface.

---

## Highlights

- Groq LLM for intent parsing and function calling
- Local code generation via Ollama (optional)
- English + Hinglish support
- Voice I/O (STT + Edge TTS) with keyboard hotkeys
- Sentry mode: webcam motion detection + Telegram alerts
- 60+ automation functions: file ops, system control, WhatsApp, email, reminders, media, keyboard, windows

---

## Quick Start

Prerequisites:

- Python 3.11+
- Windows 10 / 11 (64-bit)
- (Optional) Microphone for voice, Webcam for Sentry

Clone and install:

```bash
git clone https://github.com/abhaygupta56/IntelliDesk-AI.git
cd IntelliDesk-AI
python -m pip install -r requirements.txt
```

Create a `.env` file in the project root and add required keys:

```env
# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder:3b
EMAIL_ADDRESS=you@example.com
EMAIL_PASSWORD=supersecret
```

Run the app (GUI):

```bash
python run.py
```

CLI mode:

```bash
python run.py --cli
```

---

## Hotkeys

- `Ctrl+Space` — Open/close command palette
- `F11` — Toggle microphone
- `F12` — Toggle text-to-speech
- `F10` — Stop voice output
- `Esc` — Hide palette

---

## Example Commands

English / Hinglish examples:

- `open chrome` / `chrome kholo`
- `send whatsapp to john saying hello` / `john ko whatsapp bhejo hello bol do`
- `create file notes.txt` / `file banao notes.txt`
- Multi-step: `open chrome then search python tutorials`

Code generation example:

- `write python code for bubble sort` (saved to `generated_codes/`)

---

## Configuration (important `.env` variables)

| Variable | Description | Required |
|---|---:|:---:|
| `GROQ_API_KEY` | Groq API key for LLM intent parsing | ✅ |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token for Sentry alerts | Optional |
| `TELEGRAM_CHAT_ID` | Telegram chat id for alerts | Optional |
| `OLLAMA_BASE_URL` | Ollama server URL (default `http://localhost:11434`) | Optional |
| `OLLAMA_MODEL` | Model name for code gen (default `qwen2.5-coder:3b`) | Optional |
| `EMAIL_ADDRESS` / `EMAIL_PASSWORD` | For email sending features | Optional |

Note: Keep `.env` out of source control.

---

## Dependencies

Key packages are listed in `requirements.txt`, including `groq`, `customtkinter`, `edge-tts`, `opencv-python`, `python-telegram-bot`, and more.

---

## Project Layout

```
IntelliDesk-AI/
├── run.py                  # Entry point (GUI default, use --cli for CLI)
├── config.py               # App configuration & validation
├── requirements.txt
├── README.md
├── .env                   # Local secrets (not committed)
└── src/
    ├── automation/        # Desktop automation functions (system, file, web, whatsapp, email, media, etc.)
    ├── core/              # Routing, function registry, conversation & agent managers
    ├── gui/               # Spotlight app (glassmorphic UI)
    ├── llm/               # Groq and Ollama clients
    ├── database/          # SQLite persistence (data/intellidesk.db)
    └── utils/             # voice, stt, telegram notifier, logger
```

---

## Sentry Mode

Use the sentry features to monitor motion and receive Telegram alerts. Example commands:

- `start sentry for 30 minutes`
- `sentry status`
- `stop sentry`

Requires `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` to send alerts.

---

## Development & Contributing

- Create a feature branch and open a PR against `main`.
- Keep secrets out of commits; use `.env` and `.gitignore` for DB temp files.
- Run the app locally with `python run.py` and test core flows.

There are no automated tests in the repo — please add unit tests where appropriate.

---

## License & Author

MIT License — see `LICENSE`.

Made by Abhay Gupta — https://github.com/abhaygupta56 — abhaygupta3347@gmail.com
