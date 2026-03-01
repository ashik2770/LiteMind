import os
import telebot
from rich.console import Console
from rich.panel import Panel
from config_ui import run_setup
from agent import LiteMindCore

console = Console()

if not os.path.exists("config.json"):
    run_setup()

try:
    agent = LiteMindCore()
    bot = telebot.TeleBot(agent.config["telegram_token"])
    owner_id = str(agent.config.get("owner_id", ""))
except Exception as e:
    console.print(f"[bold red]Initialization Error:[/] {e}")
    exit()

console.clear()
console.print(Panel("[bold cyan]LiteMind V3 (ULTRA) is ONLINE and secured...[/bold cyan]\n[dim]Advanced Toolkits & ADB Protocols Active.[/dim]\n[dim]Press Ctrl+C to shutdown.[/dim]", border_style="cyan"))

def is_owner(message):
    # Security Check: Only allow owner to communicate
    if owner_id and str(message.chat.id) != owner_id:
        console.print(f"[bold red]Unauthorized access attempt by ID: {message.chat.id}[/]")
        bot.reply_to(message, "⛔ Access Denied. You are not authorized to use this AI.")
        return False
    return True

@bot.message_handler(commands=['start', 'help'])
def start_cmd(message):
    if not is_owner(message): return
    help_text = (
        "⚡ **LiteMind V3: Personal Computing Intelligence**\n\n"
        "**Commands:**\n"
        "• `/start` / `/help` - Show this menu\n"
        "• `/clear` - Clear short-term memory\n"
        "• `/sys` - Instant system diagnostic\n\n"
        "**Capabilities:**\n"
        "• 🌐 Web Browsing & Research\n"
        "• 📁 File Management & Code Review\n"
        "• 📸 Vision (Screenshot PC/Android)\n"
        "• ⚙️ System Monitoring & Control\n"
        "• 🧠 Long-Term RAG Memory\n"
        "• 🤖 Mobile Automation (ADB)"
    )
    bot.reply_to(message, help_text, parse_mode="Markdown")

@bot.message_handler(commands=['sys'])
def sys_cmd(message):
    if not is_owner(message): return
    from tools import get_system_stats
    stats = get_system_stats()
    bot.reply_to(message, f"📊 **System Status Report**\n\n{stats}", parse_mode="Markdown")

@bot.message_handler(commands=['clear'])
def clear_cmd(message):
    if not is_owner(message): return
    # Clears Short Term Context by deleting rows in history table
    agent.memory.cursor.execute("DELETE FROM history")
    agent.memory.conn.commit()
    bot.reply_to(message, "🧹 Short-term conversation memory cleared. Vector Long-Term memory remains intact.")

@bot.message_handler(func=lambda m: True)
def chat_handler(message):
    if not is_owner(message): return
    
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        console.print(f"[bold blue]User:[/] {message.text}")
        
        reply = agent.process_query(message.text)
        
        # Try sending as Markdown, if fails (due to unescaped chars), send as plain text
        try:
            bot.reply_to(message, reply, parse_mode="Markdown")
        except telebot.apihelper.ApiTelegramException:
            bot.reply_to(message, reply)
            
        console.print(f"[bold green]Agent:[/] {reply}\n")
    except Exception as e:
        error_msg = f"⚠️ System Exception: {str(e)}"
        bot.reply_to(message, error_msg)
        console.print(f"[bold red]{error_msg}[/]")

if __name__ == "__main__":
    bot.infinity_polling()