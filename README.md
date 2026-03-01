# LiteMind V3 (ULTRA)

LiteMind is an elite, autonomous AI assistant integrated with Telegram, designed for advanced multi-platform control (PC & Android). Version 3 introduces high-level system monitoring, vision capabilities, and deep file system integration.

## 🚀 Key Features

- **🧠 Long-Term RAG Memory**: Uses a Vector Database (SQLite + Google Embeddings) to remember past interactions and user preferences.
- **👁️ Vision System**: Take screenshots of your PC or Android device in real-time.
- **📊 System Diagnostic**: Monitor CPU, RAM, Disk, and Battery usage directly from Telegram.
- **📂 File Toolkit**: Search, list, and read files in your project directory autonomously.
- **🤖 Android Automation**: Full ADB support to control your mobile device, open apps, and perform clicks.
- **🌐 Research Engine**: Advanced web scraping and internet search capabilities.

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ashik2770/LiteMind.git
   cd LiteMind
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the agent**:
   Run the setup UI to enter your API keys and Telegram bot token:
   ```bash
   python config_ui.py
   ```

4. **Start the Agent**:
   ```bash
   python main.py
   ```

## ⌨️ Telegram Commands

- `/start` or `/help` - Show the interactive capabilities menu.
- `/sys` - Get an instant system health report.
- `/clear` - Wipe short-term conversation context.

## 🛡️ Security

LiteMind includes strictly enforced safety protocols. It will reject hazardous commands (e.g., `rm -rf /`) and requires an `owner_id` check for all incoming messages to prevent unauthorized access.

---

*Powered by LiteMind Personal Computing Intelligence.*
