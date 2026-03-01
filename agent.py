import json
import requests
import time
from tools import AI_TOOL_SCHEMA, AVAILABLE_TOOLS, DEVICE_OS
from system_prompt import generate_system_prompt
from memory import EnhancedVectorMemory

class LiteMindCore:
    def __init__(self):
        with open("config.json", "r") as f:
            self.config = json.load(f)

        self.api_key = self.config.get("api_key", "")
        self.base_url = self.config["base_url"]
        self.model = self.config["model"]
        self.provider = self.config.get("provider", "Unknown")
        
        # We need a gemini API key for Vector DB embeddings. 
        # If user is using Ollama, they need to supply a gemini key for memory separately, or we fallback.
        # Assuming for now self.api_key handles both or memory will gracefully fail if invalid.
        self.memory = EnhancedVectorMemory(self.api_key)
        
        self.tools = AI_TOOL_SCHEMA +[{
            "type": "function",
            "function": {
                "name": "save_to_long_term_memory",
                "description": "Saves critical facts to memory database.",
                "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}
            }
        }]
        
        self.available_tools = AVAILABLE_TOOLS.copy()
        self.available_tools["save_to_long_term_memory"] = self.memory.save_memory

    def call_llm(self, messages, max_retries=3):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # OpenRouter specific headers
        if "openrouter" in self.provider.lower():
            headers["HTTP-Referer"] = "https://github.com/litemind"
            headers["X-Title"] = "LiteMind"

        payload = {
            "model": self.model,
            "messages": messages,
            "tools": self.tools,
            "tool_choice": "auto"
        }
        
        for attempt in range(max_retries):
            try:
                res = requests.post(self.base_url, headers=headers, json=payload, timeout=60)
                if res.status_code == 200:
                    return res.json()
                elif res.status_code == 429:
                    print(f"⏳ Rate limit hit. Retrying... ({attempt+1}/{max_retries})")
                    time.sleep(5)
                else:
                    raise Exception(f"API Error {res.status_code}: {res.text}")
            except requests.exceptions.Timeout:
                print(f"⏳ Request Timeout. Retrying... ({attempt+1}/{max_retries})")
                
        raise Exception("API Failed after max retries.")

    def process_query(self, user_text):
        safe_user_text = f"<user_input>\n{user_text}\n</user_input>"
        
        relevant_past = self.memory.search_memory(user_text)
        sys_msg = generate_system_prompt(relevant_past, list(self.available_tools.keys()))
        
        messages =[{"role": "system", "content": sys_msg}]
        messages.extend(self.memory.get_context(limit=8))
        messages.append({"role": "user", "content": safe_user_text})
        
        self.memory.log_chat("user", user_text)

        max_iterations = 5
        
        for iteration in range(max_iterations):
            response = self.call_llm(messages)
            ai_msg = response["choices"][0]["message"]
            
            if not ai_msg.get("content"):
                ai_msg["content"] = ""
                
            messages.append(ai_msg)

            if ai_msg.get("tool_calls"):
                for tool in ai_msg["tool_calls"]:
                    name = tool["function"]["name"]
                    try:
                        args = json.loads(tool["function"]["arguments"])
                        if name in self.available_tools:
                            print(f"🔧[Executing on {DEVICE_OS}] {name} -> {args}")
                            result = self.available_tools[name](**args)
                        else:
                            result = f"Error: Tool {name} not found."
                    except Exception as e:
                        result = f"Error: {str(e)}"
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool["id"],
                        "name": name,
                        "content": str(result)
                    })
                time.sleep(1) 
            else:
                final_reply = ai_msg.get("content", "Error processing request.")
                self.memory.log_chat("assistant", final_reply)
                return final_reply

        fallback_msg = "⚠️ Process limit reached."
        self.memory.log_chat("assistant", fallback_msg)
        return fallback_msg