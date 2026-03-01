import questionary
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.live import Live
from rich.status import Status
from rich import print as rprint
import json
import os
import time

console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_responsive_banner():
    """Returns a banner adapted to terminal width."""
    width = console.width
    if width < 50:
        return "[bold cyan]⚡ LiteMind ⚡[/]\n[dim]Ultra-Light Intelligence[/]"
    
    return """
 [bold cyan]██╗     ██╗████████╗███████╗███╗   ███╗██╗███╗   ██╗██████╗ [/]
 [cyan]██║     ██║╚══██╔══╝██╔════╝████╗ ████║██║████╗  ██║██╔══██╗[/]
 [blue]██║     ██║   ██║   █████╗  ██╔████╔██║██║██╔██╗ ██║██║  ██║[/]
 [blue]██║     ██║   ██║   ██╔══╝  ██║╚██╔╝██║██║██║╚██╗██║██║  ██║[/]
 [bold blue]███████╗██║   ██║   ███████╗██║ ╚═╝ ██║██║██║ ╚████║██████╔╝[/]
 [bold blue]╚══════╝╚═╝   ╚═╝   ╚══════╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝ [/]
    """

def run_setup():
    clear_screen()
    
    banner = get_responsive_banner()
    rprint(Panel(Align.center(banner), border_style="cyan", title="[bold green]System Configuration[/]"))
    
    config = {}

    rprint("\n" + "━" * console.width)
    rprint("[bold yellow]🧬 CORE INITIALIZATION[/]")
    rprint("━" * console.width + "\n")

    # Multi-Model Provider Selection
    provider = questionary.select(
        "🧠 Choose your AI Provider:",
        choices=[
            "Gemini (Free/Fast)", 
            "OpenAI", 
            "Grok", 
            "Hugging Face (Inference API)", 
            "OpenRouter (Anthropic/Others)", 
            "Ollama (Local/API)"
        ],
        style=questionary.Style([
            ('pointer', 'fg:cyan bold'),
            ('selected', 'fg:cyan bold'),
            ('question', 'bold'),
        ])
    ).ask()

    if not provider: return

    config['provider'] = provider

    rprint(f"\n[cyan]Selected Provider:[/] [bold]{provider}[/]\n")

    if provider == "Gemini (Free/Fast)":
        config['base_url'] = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
        config['model'] = "gemini-2.5-pro"
        config['api_key'] = questionary.password("🔑 Enter Gemini API Key:").ask()
        
    elif provider == "OpenAI":
        config['base_url'] = "https://api.openai.com/v1/chat/completions"
        config['model'] = questionary.text("Enter Model (e.g., gpt-4o):", default="gpt-4o").ask()
        config['api_key'] = questionary.password("🔑 Enter OpenAI API Key:").ask()

    elif provider == "Hugging Face (Inference API)":
        config['base_url'] = "https://api-inference.huggingface.co/v1/chat/completions"
        config['model'] = questionary.text("Enter HF Model ID (e.g., meta-llama/Llama-3.2-3B-Instruct):").ask()
        config['api_key'] = questionary.password("🔑 Enter Hugging Face API Token:").ask()

    elif provider == "OpenRouter (Anthropic/Others)":
        config['base_url'] = "https://openrouter.ai/api/v1/chat/completions"
        config['model'] = questionary.text("Enter OpenRouter Model (e.g., anthropic/claude-3.5-sonnet):").ask()
        config['api_key'] = questionary.password("🔑 Enter OpenRouter API Key:").ask()

    elif provider == "Ollama (Local/API)":
        config['base_url'] = questionary.text("Enter Ollama Endpoint:", default="http://localhost:11434/v1/chat/completions").ask()
        config['model'] = questionary.text("Enter Local Model Name (e.g., llama3):", default="llama3").ask()
        config['api_key'] = "ollama"

    else: # Grok
        config['base_url'] = "https://api.x.ai/v1/chat/completions"
        config['model'] = "grok-beta"
        config['api_key'] = questionary.password("🔑 Enter X.AI (Grok) API Key:").ask()

    rprint("\n[bold yellow]📡 TELEGRAM INTEGRATION[/]\n")
    config['telegram_token'] = questionary.password("🤖 Enter Telegram Bot Token:").ask()
    config['owner_id'] = questionary.text("👤 Enter your Telegram User ID (Numeric):").ask()

    with console.status("[bold green]Saving configurations to core memory...", spinner="dots"):
        time.sleep(1.5)
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)

    rprint("\n" + Panel.fit("[bold green]✅ LiteMind System Ready![/bold green]\n[dim]Run 'python main.py' to start.[/dim]", border_style="green"))
    return config

if __name__ == "__main__":
    run_setup()