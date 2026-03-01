import requests
import urllib.parse
from bs4 import BeautifulSoup
import re
import subprocess
import os
import platform
import psutil
import json
import time
from PIL import ImageGrab  # For PC screenshots
from datetime import datetime

# ==========================================
# 1. Device Detection Logic
# ==========================================
def get_device_info():
    """Detects if the environment is Android (Termux) or PC (Windows/Linux/Mac)"""
    if 'ANDROID_ROOT' in os.environ or 'ANDROID_DATA' in os.environ:
        return "Android"
    return platform.system()

DEVICE_OS = get_device_info()

# ==========================================
# 2. General Tools (Works everywhere)
# ==========================================
def search_internet(query: str) -> str:
    """Searches DuckDuckGo for real-time information."""
    try:
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        results =[f"Snippet: {a.text.strip()} \nURL: {a.get('href', '')}" for a in soup.find_all('a', class_='result__snippet', limit=4)]
        return "\n\n".join(results) if results else "No clear results found."
    except Exception as e:
        return f"Search failed: {str(e)}"

def fetch_webpage(url: str) -> str:
    """Extracts main text content from a given URL."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.extract()
        text = re.sub(r'\s+', ' ', soup.get_text(separator=' ', strip=True))
        return text[:4000] + ("..." if len(text) > 4000 else "")
    except Exception as e:
        return f"Failed to read webpage: {str(e)}"

# ==========================================
# 3. PC Specific Tools
# ==========================================
def execute_pc_command(command: str) -> str:
    """Executes a terminal/CMD command on PC."""
    if DEVICE_OS == "Android": return "Error: This tool is for PC only."
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=15)
        return result.stdout.strip() if result.returncode == 0 else f"Error: {result.stderr.strip()}"
    except Exception as e:
        return str(e)

def get_system_stats() -> str:
    """Gets CPU, RAM, Disk and Battery usage."""
    try:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        battery = psutil.sensors_battery()
        batt_str = f"{battery.percent}% {'(Charging)' if battery.power_plugged else '(Discharging)'}" if battery else "N/A"
        
        return f"💻 System Stats:\n- CPU: {cpu}%\n- RAM: {ram}%\n- Disk: {disk}%\n- Battery: {batt_str}"
    except Exception as e:
        return f"Failed to get stats: {str(e)}"

def take_screenshot() -> str:
    """Captures the current screen and saves it as 'screenshot.png'."""
    try:
        if DEVICE_OS == "Android":
            subprocess.run("adb shell screencap -p /sdcard/screenshot.png", shell=True)
            subprocess.run("adb pull /sdcard/screenshot.png .", shell=True)
            return "Android screenshot captured and pulled to local directory."
        else:
            snapshot = ImageGrab.grab()
            snapshot.save("screenshot.png")
            return "PC screenshot captured and saved as 'screenshot.png'."
    except Exception as e:
        return f"Screenshot failed: {str(e)}"

# ==========================================
# 4. File Management Tools
# ==========================================
def list_files(path: str = ".") -> str:
    """Lists files in the specified directory."""
    try:
        files = os.listdir(path)
        return "\n".join(files) if files else "Directory is empty."
    except Exception as e:
        return f"Error listing files: {str(e)}"

def read_file_content(filepath: str) -> str:
    """Reads the content of a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()[:5000] # Cap to avoid context overflow
    except Exception as e:
        return f"Error reading file: {str(e)}"

# ==========================================
# 5. Android / ADB Specific Tools
# ==========================================
def adb_execute(command: str) -> str:
    """Executes an ADB shell command on Android."""
    try:
        full_cmd = f"adb shell {command}"
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=15)
        return result.stdout.strip() if result.returncode == 0 else f"Error: {result.stderr.strip()}"
    except Exception as e:
        return str(e)


# Build dynamic Schema based on Device
AVAILABLE_TOOLS = {
    "search_internet": search_internet,
    "fetch_webpage": fetch_webpage,
    "get_system_stats": get_system_stats,
    "take_screenshot": take_screenshot,
    "list_files": list_files,
    "read_file_content": read_file_content,
}

AI_TOOL_SCHEMA =[
    {
        "type": "function", "function": {"name": "search_internet", "description": "Search the web.",
        "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}
    },
    {
        "type": "function", "function": {"name": "fetch_webpage", "description": "Read URL content.",
        "parameters": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}}
    },
    {
        "type": "function", "function": {"name": "get_system_stats", "description": "Get CPU, RAM, and Disk usage.",
        "parameters": {"type": "object", "properties": {}}}
    },
    {
        "type": "function", "function": {"name": "take_screenshot", "description": "Capture the current screen of PC or Android.",
        "parameters": {"type": "object", "properties": {}}}
    },
    {
        "type": "function", "function": {"name": "list_files", "description": "List files in a directory.",
        "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": []}}
    },
    {
        "type": "function", "function": {"name": "read_file_content", "description": "Read content from a file.",
        "parameters": {"type": "object", "properties": {"filepath": {"type": "string"}}, "required": ["filepath"]}}
    }
]

# Add conditional tools
if DEVICE_OS == "Android":
    AVAILABLE_TOOLS["adb_execute"] = adb_execute
    AI_TOOL_SCHEMA.append({
        "type": "function", "function": {"name": "adb_execute", "description": "Execute Android ADB commands.",
        "parameters": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}}
    })
else:
    AVAILABLE_TOOLS["execute_pc_command"] = execute_pc_command
    AI_TOOL_SCHEMA.append({
        "type": "function", "function": {"name": "execute_pc_command", "description": "Run shell/CMD commands on the PC.",
        "parameters": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}}
    })