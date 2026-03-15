<div align="center">

# ⬡ IntelliDesk AI

### AI-Powered Desktop Automation Assistant

*Command your PC with natural language. Work smarter, not harder.*

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Groq](https://img.shields.io/badge/Powered%20by-Groq-orange?style=for-the-badge)](https://groq.com)

[Features](#-features) • [Installation](#-quick-start) • [Commands](#-commands) • [Screenshots](#-screenshots)

</div>

---

## 🎯 What is IntelliDesk AI?

IntelliDesk AI is a **next-generation desktop automation assistant** that understands natural language in **English + Hinglish**, executes complex workflows, and provides a stunning **glassmorphic command palette UI** inspired by Raycast and Arc Browser.

**Talk to your PC like a human. Get things done in seconds.**

---

## 📸 Screenshots

### Command Palette UI
*Premium glassmorphic interface with acrylic blur*

![Command Palette](assets/palette.png)

### Multi-Step Automation
*Chain commands together seamlessly*

![Automation](assets/automation.gif)

### Code Generation
*AI-powered code writing with Ollama*

![Code Generation](assets/code_generation.png)

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🤖 AI Brain
- **Groq LLM** - Lightning-fast inference
- **Function Calling** - Smart intent detection
- **Hinglish Support** - Mix Hindi + English
- **Context Awareness** - Remembers conversation
- **Ollama Integration** - Local code generation

</td>
<td width="50%">

### 🎙️ Voice Control
- **Speech-to-Text** - Google Speech API
- **Text-to-Speech** - Natural Edge TTS
- **Continuous Listening** - Hands-free mode
- **Multi-language** - English + Hindi
- **Auto-stop** - When you stop speaking

</td>
</tr>
<tr>
<td width="50%">

### 🖥️ Desktop Automation
- **65+ Functions** - Apps, files, system, web
- **WhatsApp Messaging** - Send texts instantly
- **Email Integration** - Quick email sending
- **Window Management** - Minimize, maximize, close
- **Keyboard Shortcuts** - Automate keystrokes
- **Media Controls** - Play, pause, next, stop

</td>
<td width="50%">

### 🛡️ Sentry Mode
- **Motion Detection** - Webcam surveillance
- **Telegram Alerts** - Photo notifications
- **Auto-breaks** - Prevents overheating
- **Smart scheduling** - Set duration
- **Self-destruct** - Photos auto-delete

</td>
</tr>
<tr>
<td width="50%">

### 🎨 Premium UI
- **Glassmorphism** - Modern blur effects
- **Smooth Animations** - Buttery 60fps
- **Dark Theme** - Easy on eyes
- **Responsive** - Instant feedback
- **System Tray** - Background operation

</td>
<td width="50%">

### ⚡ Performance
- **Lightweight** - Minimal RAM usage
- **Fast Response** - Sub-second execution
- **Smart Loading** - Loads functions on-demand
- **Thread-safe** - Smooth multitasking
- **Error Recovery** - Graceful fallbacks

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Prerequisites

```bash
✅ Python 3.11 or higher
✅ Windows 10/11 (64-bit)
✅ Microphone (for voice commands)
✅ Webcam (for Sentry mode)
✅ Internet connection (for AI features)
Installation
1. Clone the repository

Bash

git clone https://github.com/abhaygupta56/IntelliDesk-AI.git
cd IntelliDesk-AI
2. Install dependencies

Bash

pip install -r requirements.txt
3. Configure environment

Create a .env file:

env

GROQ_API_KEY=your_groq_api_key_here          # Get from console.groq.com
TELEGRAM_BOT_TOKEN=your_bot_token_here       # From @BotFather (optional)
TELEGRAM_CHAT_ID=your_chat_id_here           # From @userinfobot (optional)
4. Run the app

Bash

python run.py
First time? Press Ctrl+Space to open the spotlight!

🎮 Hotkeys
<div align="center">
Key	Action	Description
Ctrl+Space	Toggle Spotlight	Open/close command palette
Enter	Execute	Run the command
F10	Stop Voice	Stop speaking
F11	Toggle Mic	Enable/disable voice input
F12	Toggle TTS	Enable/disable voice output
Esc	Close	Hide the spotlight
</div>
💬 Commands
🖥️ System Control
<table> <tr> <td width="50%">
English

Bash

open chrome
open notepad
close chrome
lock the system
shutdown computer
restart pc
sleep mode
volume up
volume down
brightness up
brightness down
mute volume
unmute volume
system info
</td> <td width="50%">
Hinglish

Bash

chrome kholo
notepad kholo
chrome band karo
system lock karo
computer band kar do
restart kar do
sleep mode
volume badhao
volume kam karo
brightness badhao
brightness kam karo
mute kar do
unmute karo
system info batao
</td> </tr> </table>
📸 Screenshots & Media
<table> <tr> <td width="50%">
English

Bash

take a screenshot
screenshot full screen
play music
pause music
next song
previous song
stop music
</td> <td width="50%">
Hinglish

Bash

screenshot le lo
puri screen ka screenshot lo
music chala
music roko
agla gaana
pichla gaana
music band karo
</td> </tr> </table>
📁 File Management
<table> <tr> <td width="50%">
English

Bash

create file notes.txt
create folder documents
delete file test.txt
delete folder temp
search files in documents
organize downloads
copy file to desktop
move file to downloads
rename file old.txt to new.txt
open file explorer
</td> <td width="50%">
Hinglish

Bash

file banao notes.txt
folder banao documents
file delete karo test.txt
folder delete karo temp
documents mein files search karo
downloads organize karo
file copy karo desktop pe
file move karo downloads mein
file ka naam badlo old.txt se new.txt
file explorer kholo
</td> </tr> </table>
🌐 Web & Search
<table> <tr> <td width="50%">
English

Bash

google search python tutorials
search AI on google
youtube search coding
play python tutorial on youtube
open youtube
open wikipedia
search on wikipedia
weather forecast
get weather
open website github.com
</td> <td width="50%">
Hinglish

Bash

google pe python search karo
AI search karo google pe
youtube pe coding search karo
python tutorial play karo youtube pe
youtube kholo
wikipedia kholo
wikipedia pe search karo
weather batao
mausam kya hai
website kholo github.com
</td> </tr> </table>
💬 WhatsApp Messaging
<table> <tr> <td width="50%">
English

Bash

send whatsapp to john saying hello
whatsapp john with message meeting at 5
message mom on whatsapp
whatsapp dad saying i'll be late
save whatsapp contact john 9876543210
list whatsapp contacts
send file to john on whatsapp
schedule whatsapp to john at 5 PM
</td> <td width="50%">
Hinglish

Bash

john ko whatsapp bhejo hello bol do
john ko message karo meeting 5 baje
mummy ko whatsapp pe message karo
papa ko bhejo main late hounga
john ka number save karo 9876543210
whatsapp contacts dikhao
john ko file bhejo whatsapp pe
john ko 5 baje whatsapp schedule karo
</td> </tr> </table>
Smart Features:

Auto-detects saved contacts
Asks for phone number if contact not found
Supports file sharing
Schedule messages for later
📧 Email
<table> <tr> <td width="50%">
English

Bash

send email to john
email mom with subject birthday
save email contact john john@email.com
list email contacts
check email config
</td> <td width="50%">
Hinglish

Bash

john ko email bhejo
mummy ko email karo birthday subject se
john ka email save karo
email contacts dikhao
email settings check karo
</td> </tr> </table>
⌨️ Keyboard Shortcuts
<table> <tr> <td width="50%">
English

Bash

type hello world
press enter
press escape
press f5
copy this
paste here
cut this
undo that
redo
select all
save file
find text
new tab
close tab
refresh page
</td> <td width="50%">
Hinglish

Bash

hello world type karo
enter dabao
escape press karo
f5 dabao
copy karo
paste karo yaha
cut karo
undo karo
redo karo
sab select karo
file save karo
text dhundo
naya tab kholo
tab band karo
page refresh karo
</td> </tr> </table>
🪟 Window Management
<table> <tr> <td width="50%">
English

Bash

minimize window
maximize chrome
close notepad
list all windows
focus chrome
switch to notepad
</td> <td width="50%">
Hinglish

Bash

window minimize karo
chrome maximize karo
notepad band karo
sare windows dikhao
chrome pe jao
notepad pe switch karo
</td> </tr> </table>
⏰ Reminders & Timers
<table> <tr> <td width="50%">
English

Bash

set timer for 5 minutes
start timer 30 seconds
stop timer
remind me in 10 minutes
remind me at 5 PM
show my reminders
</td> <td width="50%">
Hinglish

Bash

5 minute ka timer lagao
30 second ka timer start karo
timer band karo
10 minute baad yaad dilao
5 baje yaad dilao
mere reminders dikhao
</td> </tr> </table>
🧮 Utilities
<table> <tr> <td width="50%">
English

Bash

what time is it
what's the date
calculate 15 percent of 200
calculate 25 + 75
flip a coin
roll a dice
</td> <td width="50%">
Hinglish

Bash

time kya hai
date kya hai
200 ka 15 percent calculate karo
25 + 75 kitna hota hai
coin flip karo
dice roll karo
</td> </tr> </table>
💻 Code Generation
<table> <tr> <td width="50%">
English

Bash

write python code for bubble sort
generate code to reverse a string
write javascript code for calculator
create a function to find prime numbers
write code for binary search
</td> <td width="50%">
Hinglish

Bash

python code likh bubble sort ka
string reverse karne ka code banao
javascript mein calculator ka code likh
prime numbers find karne ka function likh
binary search ka code de
</td> </tr> </table>
Features:

Auto-detects programming language
Saves code to generated_codes/ folder
Supports: Python, JavaScript, Java, C++, C#, HTML, CSS
🛡️ Sentry Mode (Motion Detection)
<table> <tr> <td width="50%">
English

Bash

start sentry for 30 minutes
activate sentry mode
sentry status
stop sentry
</td> <td width="50%">
Hinglish

Bash

30 minute ke liye sentry chalu karo
sentry mode activate karo
sentry ka status batao
sentry band karo
</td> </tr> </table>
Features:

Webcam-based motion detection
Telegram photo alerts
Auto-breaks every 20 minutes
Max 120 minutes runtime
🔗 Multi-Step Automation
Chain multiple commands together:

Bash

# English
open chrome then search python tutorials
volume up then take screenshot then lock system
create file notes.txt then open notepad

# Hinglish
chrome kholo then google pe AI search karo
screenshot le lo then john ko whatsapp bhejo
file banao then notepad mein kholo

# Mix
open chrome then youtube pe python search karo
volume badhao then screenshot le lo then system lock karo
🛠️ Advanced Configuration
Environment Variables
Variable	Description	Default	Required
GROQ_API_KEY	Groq API key for LLM	-	✅ Yes
TELEGRAM_BOT_TOKEN	Telegram bot token for Sentry alerts	-	⚠️ Optional
TELEGRAM_CHAT_ID	Your Telegram chat ID	-	⚠️ Optional
OLLAMA_BASE_URL	Ollama server URL	http://localhost:11434	⚠️ Optional
OLLAMA_MODEL	Model for code generation	qwen2.5-coder:3b	⚠️ Optional
VOICE_ENABLED	Enable TTS by default	true	⚠️ Optional
VOICE_RATE	Speech rate (100-200)	150	⚠️ Optional
VOICE_GENDER	Voice gender	male	⚠️ Optional
CLI Mode
For terminal enthusiasts:

Bash

python run.py --cli
Features:

Terminal-based interface
Same AI capabilities
Voice support
Command history
📂 Project Structure
text

IntelliDesk-AI/
│
├── 📄 run.py                      # Application entry point
├── ⚙️ config.py                   # Configuration management
├── 📋 requirements.txt            # Python dependencies
├── 🔐 .env                        # Environment variables
│
├── 📁 src/
│   ├── 🤖 automation/             # 65+ automation functions
│   │   ├── system_ops.py          # System controls
│   │   ├── file_ops.py            # File management
│   │   ├── web_ops.py             # Web search & browsing
│   │   ├── whatsapp.py            # WhatsApp messaging
│   │   ├── email_ops.py           # Email integration
│   │   ├── keyboard_ops.py        # Keyboard shortcuts
│   │   ├── window_ops.py          # Window management
│   │   ├── media_ops.py           # Media controls
│   │   ├── reminder_ops.py        # Reminders & timers
│   │   ├── utility_ops.py         # Utilities
│   │   └── sentry_mode.py         # Motion detection
│   │
│   ├── 🧠 core/                   # Brain of the application
│   │   ├── conversation_manager.py    # Conversation orchestration
│   │   ├── groq_assistant.py          # Groq LLM integration
│   │   └── function_registry.py       # Function mapping
│   │
│   ├── 🎨 gui/                    # User interface
│   │   └── spotlight_app.py           # Glassmorphic command palette
│   │
│   ├── 🔮 llm/                    # LLM clients
│   │   ├── groq_client.py             # Groq API wrapper
│   │   └── ollama_client.py           # Ollama local inference
│   │
│   ├── 💾 database/               # Data persistence
│   │   └── db_manager.py              # SQLite operations
│   │
│   └── 🛠️ utils/                  # Utility modules
│       ├── voice_manager.py           # Text-to-Speech
│       ├── stt_manager.py             # Speech-to-Text
│       ├── telegram_notifier.py       # Telegram alerts
│       └── logger.py                  # Logging system
│
└── 📁 data/                       # Runtime data
    ├── intellidesk.db             # SQLite database
    └── logs/                      # Application logs

📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments
Groq - Lightning-fast LLM inference
Ollama - Local AI models
Edge TTS - Natural voice synthesis
CustomTkinter - Modern UI framework
OpenCV - Computer vision for Sentry mode
📧 Contact
Abhay Gupta

🐙 GitHub: @abhaygupta56
📧 Email: abhaygupta3347@gmail.com
<div align="center">
⭐ Star this repo if you find it useful!
IntelliDesk AI - Work smarter, not harder

Made with ❤️ and Python

</div> ```
