import json
import os

DB_FILE = "database.json"

# Load or initialize memory database
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({}, f)

def load_memory():
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_memory(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

def update_user_memory(user_id: str, entry: str):
    memory = load_memory()
    user_data = memory.get(user_id, {"history": []})
    user_data["history"].append(entry)
    memory[user_id] = user_data
    save_memory(memory)

def get_user_context(user_id: str, last_n=10):
    memory = load_memory()
    history = memory.get(user_id, {}).get("history", [])
    return history[-last_n:]

def clear_user_memory(user_id):
    memory = load_memory()
    memory[user_id] = {"history": []}
    save_memory(memory)
