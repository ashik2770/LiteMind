import sqlite3
import json
import math
import requests
from datetime import datetime

class EnhancedVectorMemory:
    def __init__(self, api_key):
        # We use a free fallback or Gemini API for embeddings
        self.api_key = api_key
        self.db_path = "litemind_memory.sqlite"
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY, role TEXT, content TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS vectors (id INTEGER PRIMARY KEY, timestamp TEXT, text TEXT, embedding TEXT)''')
        self.conn.commit()

    def get_embedding(self, text):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={self.api_key}"
        payload = {"model": "models/text-embedding-004", "content": {"parts":[{"text": text}]}}
        res = requests.post(url, json=payload).json()
        return res['embedding']['values']

    def cosine_similarity(self, v1, v2):
        dot_product = sum(a * b for a, b in zip(v1, v2))
        mag1 = math.sqrt(sum(a ** 2 for a in v1))
        mag2 = math.sqrt(sum(b ** 2 for b in v2))
        return dot_product / (mag1 * mag2) if mag1 and mag2 else 0

    def save_memory(self, text):
        emb = self.get_embedding(text)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO vectors (timestamp, text, embedding) VALUES (?, ?, ?)", (timestamp, text, json.dumps(emb)))
        self.conn.commit()
        return f"Memory saved at {timestamp}: '{text}'"

    def search_memory(self, query, top_k=3):
        self.cursor.execute("SELECT timestamp, text, embedding FROM vectors")
        rows = self.cursor.fetchall()
        if not rows: return ""

        query_emb = self.get_embedding(query)
        results =[]
        for row in rows:
            similarity = self.cosine_similarity(query_emb, json.loads(row[2]))
            results.append((similarity, f"[{row[0]}] {row[1]}"))
        
        results.sort(key=lambda x: x[0], reverse=True)
        return "\n".join([res[1] for res in results[:top_k] if res[0] > 0.4])

    def log_chat(self, role, content):
        self.cursor.execute("INSERT INTO history (role, content) VALUES (?, ?)", (role, content))
        self.conn.commit()

    def get_context(self, limit=10):
        self.cursor.execute("SELECT role, content FROM history ORDER BY id DESC LIMIT ?", (limit,))
        return [{"role": row[0], "content": row[1]} for row in self.cursor.fetchall()[::-1]]