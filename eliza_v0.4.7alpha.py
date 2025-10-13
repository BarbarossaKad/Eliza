"""
ELIZA v0.6 - AI Character Sandbox with ENHANCED UI
Named in honor of ELIZA (1966), the first chatbot, and the ELIZA effect.

CHANGELOG v0.6:
- NEW: Stunning game-like visual design
- NEW: Animated gradients and effects
- NEW: Character avatars with emojis
- Improved: Dark theme with neon accents
- Improved: Professional message bubbles

Requirements:
pip install gradio requests
"""

import gradio as gr
import json
import os
import requests
from datetime import datetime
import re

# ============ CONFIGURATION ============

VERSION = "0.6"
APP_NAME = "ELIZA"

LLM_BACKENDS = {
    'ollama': {'url': 'http://localhost:11434', 'name': 'Ollama'},
    'lm_studio': {'url': 'http://localhost:1234', 'name': 'LM Studio'},
    'text_gen_webui': {'url': 'http://localhost:5000', 'name': 'Text Generation WebUI'}
}

# Global state
characters = {}
chat_histories = {}
character_memories = {}
active_llm = None
available_models = []

# ============ ENHANCED CUSTOM CSS ============

CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

:root {
    --bg-primary: #0a0a0f;
    --bg-secondary: #151520;
    --bg-tertiary: #1e1e2e;
    --bg-card: #252535;
    --accent-primary: #8b5cf6;
    --accent-secondary: #a78bfa;
    --accent-glow: rgba(139, 92, 246, 0.5);
    --text-primary: #f0f0f0;
    --text-secondary: #a0a0b0;
    --border-color: #2d2d3d;
    --success: #10b981;
    --warning: #f59e0b;
    --error: #ef4444;
}

* {
    font-family: 'Poppins', 'Segoe UI', system-ui, sans-serif !important;
}

.gradio-container {
    background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #16213e 100%) !important;
    background-size: 400% 400% !important;
    animation: gradientShift 15s ease infinite !important;
    color: var(--text-primary) !important;
    min-height: 100vh !important;
}

@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.header-container {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(167, 139, 250, 0.1)) !important;
    border: 2px solid var(--accent-primary) !important;
    border-radius: 20px !important;
    padding: 30px !important;
    margin-bottom: 20px !important;
    box-shadow: 0 8px 32px rgba(139, 92, 246, 0.3) !important;
}

.header-title {
    font-size: 48px !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, #8b5cf6, #a78bfa, #c4b5fd) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    text-align: center !important;
    margin: 0 !important;
}

.panel-container {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 16px !important;
    padding: 20px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5) !important;
    transition: all 0.3s ease !important;
}

.panel-container:hover {
    border-color: var(--accent-primary) !important;
    box-shadow: 0 8px 30px rgba(139, 92, 246, 0.3) !important;
    transform: translateY(-2px) !important;
}

button.primary {
    background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary)) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4) !important;
}

button.primary:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 25px rgba(139, 92, 246, 0.6) !important;
}

textarea, input {
    background: var(--bg-tertiary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
    padding: 12px !important;
    transition: all 0.3s ease !important;
}

textarea:focus, input:focus {
    border-color: var(--accent-primary) !important;
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.2) !important;
}

.character-avatar {
    width: 60px !important;
    height: 60px !important;
    border-radius: 50% !important;
    background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary)) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 32px !important;
    margin-right: 15px !important;
    box-shadow: 0 4px 15px var(--accent-glow) !important;
}

.memory-tag {
    display: inline-block;
    padding: 6px 12px;
    margin: 4px;
    background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
    color: white;
    box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3);
}

.stat-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    transition: all 0.3s ease;
}

.stat-card:hover {
    border-color: var(--accent-primary);
    transform: scale(1.05);
}

.stat-number {
    font-size: 36px;
    font-weight: 700;
    background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.stat-label {
    color: var(--text-secondary);
    font-size: 14px;
    margin-top: 8px;
}

.alert {
    padding: 16px 20px;
    border-radius: 12px;
    margin: 10px 0;
    font-weight: 500;
}

.alert-success {
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid var(--success);
    color: var(--success);
}

.alert-warning {
    background: rgba(245, 158, 11, 0.1);
    border: 1px solid var(--warning);
    color: var(--warning);
}

.alert-error {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid var(--error);
    color: var(--error);
}

::-webkit-scrollbar {
    width: 12px;
}

::-webkit-scrollbar-track {
    background: var(--bg-secondary);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
    border-radius: 10px;
}
"""

# ============ BACKEND DETECTION ============

class BackendDetector:
    @staticmethod
    def check_server(url, endpoint=''):
        try:
            response = requests.get(f"{url}{endpoint}", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    @staticmethod
    def detect_llm_backends():
        available = []
        for key, config in LLM_BACKENDS.items():
            if key == 'ollama':
                if BackendDetector.check_server(config['url'], '/api/tags'):
                    available.append((key, config['name']))
        return available
    
    @staticmethod
    def get_ollama_models():
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=2)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
        except:
            pass
        return []

# ============ AI CLIENT ============

class LocalLLMClient:
    def __init__(self, backend_key):
        self.backend = backend_key
        self.url = LLM_BACKENDS[backend_key]['url']
    
    def generate(self, prompt, model, temperature=0.8, max_tokens=200):
        try:
            if self.backend == 'ollama':
                response = requests.post(
                    f"{self.url}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": temperature, "num_predict": max_tokens}
                    },
                    timeout=120
                )
                response.raise_for_status()
                return response.json()["response"]
        except Exception as e:
            raise Exception(f"AI error: {str(e)}")

# ============ MEMORY SYSTEM ============

class MemoryBank:
    def __init__(self, character_name):
        self.character_name = character_name
        self.user_facts = []
        self.important_moments = []
        self.conversation_summaries = []
        self.preferences = {}
        self.last_topics = []
        
    def add_user_fact(self, fact, timestamp=None):
        if not timestamp:
            timestamp = datetime.now().isoformat()
        if not any(f['fact'].lower() == fact.lower() for f in self.user_facts):
            self.user_facts.append({
                'fact': fact,
                'timestamp': timestamp,
                'confidence': 'high'
            })
    
    def add_important_moment(self, moment, tags=None):
        if tags is None:
            tags = []
        self.important_moments.append({
            'moment': moment,
            'tags': tags,
            'timestamp': datetime.now().isoformat()
        })
    
    def add_preference(self, category, value):
        self.preferences[category] = value
    
    def add_topic(self, topic):
        if topic not in self.last_topics:
            self.last_topics.append(topic)
            self.last_topics = self.last_topics[-10:]
    
    def get_context_string(self):
        context = ""
        if self.user_facts:
            context += "\nWhat you know about the user:\n"
            for fact in self.user_facts[-10:]:
                context += f"- {fact['fact']}\n"
        if self.preferences:
            context += "\nUser preferences:\n"
            for cat, val in self.preferences.items():
                context += f"- {cat.capitalize()}: {val}\n"
        if self.important_moments:
            context += "\nImportant moments you remember:\n"
            for moment in self.important_moments[-5:]:
                tags_str = ', '.join(moment['tags']) if moment['tags'] else 'general'
                context += f"- [{tags_str}] {moment['moment']}\n"
        return context
    
    def to_dict(self):
        return {
            'user_facts': self.user_facts,
            'important_moments': self.important_moments,
            'conversation_summaries': self.conversation_summaries,
            'preferences': self.preferences,
            'last_topics': self.last_topics
        }
    
    @staticmethod
    def from_dict(character_name, data):
        memory = MemoryBank(character_name)
        memory.user_facts = data.get('user_facts', [])
        memory.important_moments = data.get('important_moments', [])
        memory.conversation_summaries = data.get('conversation_summaries', [])
        memory.preferences = data.get('preferences', {})
        memory.last_topics = data.get('last_topics', [])
        return memory

def extract_memories_from_conversation(character_name, user_message, ai_response):
    memory = character_memories.get(character_name)
    if not memory:
        return
    
    user_msg_lower = user_message.lower()
    
    name_match = re.search(r"my name is (\w+)", user_msg_lower)
    if name_match:
        memory.add_user_fact(f"User's name is {name_match.group(1).capitalize()}")
    
    identity_patterns = [
        r"i(?:'m| am) a (\w+(?:\s+\w+)?)",
        r"i work as (?:a |an )?(\w+(?:\s+\w+)?)",
        r"i(?:'m| am) from (\w+(?:\s+\w+)?)",
    ]
    
    for pattern in identity_patterns:
        match = re.search(pattern, user_msg_lower)
        if match:
            memory.add_user_fact(f"User is {match.group(1)}")
    
    preference_match = re.search(r"i (?:like|love|enjoy|prefer) (\w+(?:\s+\w+){0,3})", user_msg_lower)
    if preference_match:
        memory.add_preference("likes", preference_match.group(1))

# ============ CHARACTER MANAGEMENT ============

def get_character_avatar(name):
    avatars = ["👤", "🎭", "🦊", "🐺", "🦁", "🐯", "🐱", "🐶", "🐼", "🐨"]
    index = (ord(name[0].upper()) - 65) % len(avatars)
    return avatars[index]

def create_character(name, personality, backstory, appearance, example_dialogue):
    if not name or not name.strip():
        return "<div class='alert alert-error'>❌ Name cannot be empty</div>", gr.Dropdown(), ""
    
    name = name.strip()
    
    if not personality or not personality.strip():
        return "<div class='alert alert-error'>❌ Personality is required!</div>", gr.Dropdown(), ""
    
    if name in characters:
        return f"<div class='alert alert-error'>❌ Character '{name}' already exists!</div>", gr.Dropdown(), ""
    
    characters[name] = {
        "name": name,
        "personality": personality.strip(),
        "backstory": backstory.strip() if backstory else "",
        "appearance": appearance.strip() if appearance else "",
        "example_dialogue": example_dialogue.strip() if example_dialogue else "",
        "created": datetime.now().isoformat(),
        "avatar": get_character_avatar(name)
    }
    
    chat_histories[name] = []
    character_memories[name] = MemoryBank(name)
    
    try:
        save_character_to_file(name)
    except Exception as e:
        del characters[name]
        return f"<div class='alert alert-error'>❌ Failed to save: {str(e)}</div>", gr.Dropdown(), ""
    
    char_list = get_character_list()
    
    return (
        f"<div class='alert alert-success'>✅ Character '{name}' created!</div>",
        gr.Dropdown(choices=char_list, value=name),
        ""
    )

def save_character_to_file(name):
    os.makedirs("characters", exist_ok=True)
    
    with open(f"characters/{name}.json", 'w', encoding='utf-8') as f:
        json.dump(characters[name], f, indent=2)
    
    with open(f"characters/{name}_history.json", 'w', encoding='utf-8') as f:
        json.dump(chat_histories.get(name, []), f, indent=2)
    
    if name in character_memories:
        with open(f"characters/{name}_memory.json", 'w', encoding='utf-8') as f:
            json.dump(character_memories[name].to_dict(), f, indent=2)

def load_characters_from_files():
    if not os.path.exists("characters"):
        return
    
    for filename in os.listdir("characters"):
        if filename.endswith(".json") and "_history" not in filename and "_memory" not in filename:
            try:
                with open(f"characters/{filename}", 'r', encoding='utf-8') as f:
                    char_data = json.load(f)
                    name = char_data["name"]
                    
                    if 'avatar' not in char_data:
                        char_data['avatar'] = get_character_avatar(name)
                    
                    characters[name] = char_data
                    
                    history_file = f"characters/{name}_history.json"
                    if os.path.exists(history_file):
                        with open(history_file, 'r') as hf:
                            chat_histories[name] = json.load(hf)
                    else:
                        chat_histories[name] = []
                    
                    memory_file = f"characters/{name}_memory.json"
                    if os.path.exists(memory_file):
                        with open(memory_file, 'r') as mf:
                            memory_data = json.load(mf)
                            character_memories[name] = MemoryBank.from_dict(name, memory_data)
                    else:
                        character_memories[name] = MemoryBank(name)
            except Exception as e:
                print(f"Error loading {filename}: {e}")

def delete_character(name):
    if not name or name not in characters:
        return "<div class='alert alert-error'>❌ Select a character first</div>", gr.Dropdown()
    
    try:
        del characters[name]
        if name in chat_histories:
            del chat_histories[name]
        if name in character_memories:
            del character_memories[name]
        
        for suffix in ["", "_history", "_memory"]:
            file_path = f"characters/{name}{suffix}.json"
            if os.path.exists(file_path):
                os.remove(file_path)
        
        char_list = get_character_list()
        new_selection = char_list[0] if char_list else None
        
        return (
            f"<div class='alert alert-success'>✅ Character '{name}' deleted</div>",
            gr.Dropdown(choices=char_list, value=new_selection)
        )
    except Exception as e:
        return f"<div class='alert alert-error'>❌ Error: {str(e)}</div>", gr.Dropdown()

def get_character_list():
    return sorted(characters.keys()) if characters else []

def get_character_info(name):
    if not name or name not in characters:
        return "<div class='panel-container'>Select a character</div>"
    
    char = characters[name]
    avatar = char.get('avatar', '👤')
    
    info = f"""<div class='panel-container'>
    <div style='text-align: center; margin-bottom: 20px;'>
        <div class='character-avatar' style='display: inline-flex;'>{avatar}</div>
        <h2 style='color: var(--accent-primary);'>{char['name']}</h2>
    </div>
    <h3 style='color: var(--accent-secondary);'>✨ Personality</h3>
    <p>{char['personality']}</p>
    """
    
    if char.get('backstory'):
        info += f"<h3 style='color: var(--accent-secondary);'>📖 Backstory</h3><p>{char['backstory'][:200]}...</p>"
    
    if name in character_memories:
        memory = character_memories[name]
        info += f"""
    <div style='display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-top: 20px;'>
        <div class='stat-card'>
            <div class='stat-number'>{len(memory.user_facts)}</div>
            <div class='stat-label'>Facts</div>
        </div>
        <div class='stat-card'>
            <div class='stat-number'>{len(memory.important_moments)}</div>
            <div class='stat-label'>Moments</div>
        </div>
        <div class='stat-card'>
            <div class='stat-number'>{len(memory.preferences)}</div>
            <div class='stat-label'>Preferences</div>
        </div>
    </div>
    """
    
    info += "</div>"
    return info

# ============ MEMORY MANAGEMENT ============

def get_memory_display(character_name):
    if not character_name or character_name not in character_memories:
        return "<div class='panel-container'>Select a character</div>"
    
    memory = character_memories[character_name]
    char = characters[character_name]
    avatar = char.get('avatar', '👤')
    
    display = f"""<div class='panel-container'>
    <div style='text-align: center;'><div class='character-avatar' style='display: inline-flex;'>{avatar}</div>
    <h2 style='color: var(--accent-primary);'>🧠 Memory: {character_name}</h2></div>
    <h3 style='color: var(--accent-secondary);'>📝 Facts About You</h3>"""
    
    if memory.user_facts:
        display += "<ul>"
        for fact in memory.user_facts[-10:]:
            display += f"<li>{fact['fact']}</li>"
        display += "</ul>"
    else:
        display += "<p><em>No facts yet. Chat more!</em></p>"
    
    display += "<h3 style='color: var(--accent-secondary);'>⭐ Important Moments</h3>"
    if memory.important_moments:
        display += "<ul>"
        for moment in memory.important_moments[-5:]:
            tags = ', '.join(moment['tags']) if moment['tags'] else 'general'
            display += f"<li><span class='memory-tag'>{tags}</span> {moment['moment']}</li>"
        display += "</ul>"
    else:
        display += "<p><em>No moments tagged yet.</em></p>"
    
    display += "</div>"
    return display

def add_manual_memory(character_name, fact_text):
    if not character_name or character_name not in character_memories:
        return "<div class='alert alert-error'>❌ Select a character</div>", get_memory_display(character_name)
    
    if not fact_text or not fact_text.strip():
        return "<div class='alert alert-warning'>⚠️ Enter a fact</div>", get_memory_display(character_name)
    
    memory = character_memories[character_name]
    memory.add_user_fact(fact_text.strip())
    save_character_to_file(character_name)
    
    return f"<div class='alert alert-success'>✅ Added to memory!</div>", get_memory_display(character_name)

def clear_memories(character_name):
    if not character_name or character_name not in character_memories:
        return "<div class='alert alert-error'>❌ Select a character</div>", ""
    
    character_memories[character_name] = MemoryBank(character_name)
    save_character_to_file(character_name)
    
    return f"<div class='alert alert-success'>✅ Memories cleared</div>", get_memory_display(character_name)

def tag_moment(character_name, moment_text, tags_text):
    if not character_name or character_name not in character_memories:
        return "<div class='alert alert-error'>❌ Select a character</div>", get_memory_display(character_name)
    
    if not moment_text or not moment_text.strip():
        return "<div class='alert alert-warning'>⚠️ Describe the moment</div>", get_memory_display(character_name)
    
    tags = [t.strip() for t in tags_text.split(',')] if tags_text else []
    
    memory = character_memories[character_name]
    memory.add_important_moment(moment_text.strip(), tags)
    save_character_to_file(character_name)
    
    return "<div class='alert alert-success'>✅ Moment tagged!</div>", get_memory_display(character_name)

# ============ CHAT FUNCTIONS ============

def build_prompt(character_name, user_message):
    if character_name not in characters:
        return None
    
    char = characters[character_name]
    memory = character_memories.get(character_name)
    
    prompt = f"""You are roleplaying as {char['name']}.

Character:
- Name: {char['name']}
- Personality: {char['personality']}"""
    
    if char.get('backstory'):
        prompt += f"\n- Backstory: {char['backstory']}"
    
    if memory:
        memory_context = memory.get_context_string()
        if memory_context.strip():
            prompt += f"\n{memory_context}"
    
    history = chat_histories.get(character_name, [])
    if history:
        prompt += f"\n\nRecent conversation:\n"
        for user_msg, ai_msg in history[-5:]:
            prompt += f"User: {user_msg}\n{char['name']}: {ai_msg}\n"
    
    prompt += f"\n\nUser: {user_message}\n{char['name']}:"
    
    return prompt

def chat_with_character(character_name, user_message, history, model, temperature, max_tokens, auto_memory):
    global active_llm
    
    if not active_llm:
        return history + [(user_message, "❌ No AI backend detected. Check Setup tab.")], ""
    
    if not character_name or character_name not in characters:
        return history + [(user_message, "❌ Please select a character first.")], ""
    
    if not user_message or not user_message.strip():
        return history, ""
    
    user_message = user_message.strip()
    
    prompt = build_prompt(character_name, user_message)
    
    try:
        client = LocalLLMClient(active_llm)
        ai_response = client.generate(prompt, model, temperature, max_tokens).strip()
        
        if character_name not in chat_histories:
            chat_histories[character_name] = []
        
        chat_histories[character_name].append((user_message, ai_response))
        
        if auto_memory:
            extract_memories_from_conversation(character_name, user_message, ai_response)
        
        if len(chat_histories[character_name]) > 100:
            chat_histories[character_name] = chat_histories[character_name][-100:]
        
        save_character_to_file(character_name)
        
        return history + [(user_message, ai_response)], ""
        
    except Exception as e:
        return history + [(user_message, f"❌ {str(e)}")], ""

def clear_chat(character_name):
    if character_name and character_name in chat_histories:
        chat_histories[character_name] = []
        save_character_to_file(character_name)
    return []

def load_chat_history(character_name):
    if character_name and character_name in chat_histories:
        return chat_histories[character_name]
    return []

# ============ BACKEND MANAGEMENT ============

def check_backends():
    global active_llm, available_models
    
    llm_backends = BackendDetector.detect_llm_backends()
    
    status = "<div class='panel-container'><h2>🔍 Backend Status</h2>"
    
    if llm_backends:
        status += "<h3 style='color: var(--success);'>✅ LLM Active</h3><ul>"
        for key, name in llm_backends:
            if key == 'ollama':
                models = BackendDetector.get_ollama_models()
                if models:
                    status += f"<li><strong>{name}</strong>: {len(models)} models</li>"
                    if not active_llm:
                        active_llm = key
                        available_models = models
        status += "</ul>"
    else:
        status += "<h3 style='color: var(--error);'>❌ No LLM Detected</h3>"
        status += "<p>Install <a href='https://ollama.ai' target='_blank'>Ollama</a></p>"
    
    status += "</div>"
    return status

def refresh_models():
    global active_llm, available_models
    
    llm_backends = BackendDetector.detect_llm_backends()
    
    if llm_backends:
        for key, name in llm_backends:
            if key == 'ollama':
                models = BackendDetector.get_ollama_models()
                if models:
                    active_llm = key
                    available_models = models
                    return (
                        gr.Dropdown(choices=models, value=models[0]),
                        gr.Dropdown(choices=models, value=models[0]),
                        f"<div class='alert alert-success'>✅ Found {len(models)} models</div>"
                    )
    
    return (
        gr.Dropdown(choices=["No models"], value="No models"),
        gr.Dropdown(choices=["No models"], value="No models"),
        "<div class='alert alert-error'>❌ No backends detected</div>"
    )

# ============ INITIALIZATION ============

load_characters_from_files()

# ============ UI CONSTRUCTION ============

with gr.Blocks(title=f"{APP_NAME} - AI Character Sandbox", css=CUSTOM_CSS, theme=gr.themes.Base()) as app:
    
    gr.HTML(f"""
    <div class="header-container">
        <h1 class="header-title">🎭 {APP_NAME}</h1>
        <p style="text-align: center; color: var(--text-secondary); font-size: 16px; margin-top: 10px;">
            v{VERSION} · Enhanced Memory · Self-hosted & Private
        </p>
    </div>
    """)
    
    gr.HTML("""
    <div style="text-align: center; padding: 15px; background: rgba(245, 158, 11, 0.1); 
                border: 1px solid var(--warning); border-radius: 12px; margin: 20px 0;">
        <span style="color: var(--warning); font-weight: 600;">
            ⚠️ 18+ Only · Local AI · Characters Remember You! 🧠
        </span>
    </div>
    """)
    
    with gr.Tabs():
        with gr.Tab("💬 Chat"):
            with gr.Row():
                with gr.Column(scale=1, min_width=300):
                    gr.Markdown("### 🎭 Character")
                    
                    character_select = gr.Dropdown(
                        choices=get_character_list(),
                        value=get_character_list()[0] if get_character_list() else None,
                        label="Select Character",
                        interactive=True
                    )
                    
                    character_info_display = gr.HTML(
                        get_character_info(get_character_list()[0] if get_character_list() else None)
                    )
                    
                    gr.Markdown("---")
                    gr.Markdown("### ⚙️ AI Settings")
                    
                    model_select = gr.Dropdown(
                        choices=available_models if available_models else ["No models"],
                        value=available_models[0] if available_models else "No models",
                        label="Model"
                    )
                    
                    temperature = gr.Slider(0.1, 2.0, 0.9, step=0.1, label="🔥 Creativity")
                    max_tokens = gr.Slider(50, 500, 200, step=50, label="📏 Length")
                    
                    gr.Markdown("---")
                    gr.Markdown("### 🧠 Memory")
                    
                    auto_memory = gr.Checkbox(
                        label="Auto-learn from conversation",
                        value=True
                    )
                    
                    gr.Markdown("---")
                    
                    clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary", size="lg")
                
                with gr.Column(scale=3):
                    chatbot = gr.Chatbot(
                        label="Conversation",
                        value=[],
                        height=650,
                        type="tuples"
                    )
                    
                    with gr.Row():
                        msg_input = gr.Textbox(
                            placeholder="Type your message... ✨",
                            show_label=False,
                            scale=4,
                            lines=2
                        )
                        send_btn = gr.Button("Send ➤", variant="primary", scale=1, size="lg")
            
            character_select.change(
                fn=lambda name: (get_character_info(name), load_chat_history(name)),
                inputs=[character_select],
                outputs=[character_info_display, chatbot]
            )
            
            msg_input.submit(
                chat_with_character,
                [character_select, msg_input, chatbot, model_select, temperature, max_tokens, auto_memory],
                [chatbot, msg_input]
            )
            
            send_btn.click(
                chat_with_character,
                [character_select, msg_input, chatbot, model_select, temperature, max_tokens, auto_memory],
                [chatbot, msg_input]
            )
            
            clear_btn.click(
                lambda name: clear_chat(name),
                [character_select],
                [chatbot]
            )
        
        with gr.Tab("🧠 Memory Bank"):
            gr.HTML("""
            <div class='panel-container'>
                <h2 style='color: var(--accent-primary);'>Character Memory Management</h2>
                <p>View and manage what your characters remember about you.</p>
            </div>
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    memory_character_select = gr.Dropdown(
                        choices=get_character_list(),
                        value=get_character_list()[0] if get_character_list() else None,
                        label="Select Character"
                    )
                    
                    gr.Markdown("### ➕ Add Memory")
                    
                    manual_fact = gr.Textbox(
                        label="Add Fact",
                        placeholder="e.g., User is a software engineer",
                        lines=2
                    )
                    
                    add_fact_btn = gr.Button("➕ Add Fact", variant="primary")
                    
                    gr.Markdown("---")
                    gr.Markdown("### ⭐ Tag Moment")
                    
                    moment_text = gr.Textbox(
                        label="Describe Moment",
                        placeholder="e.g., User shared their dream",
                        lines=3
                    )
                    
                    moment_tags = gr.Textbox(
                        label="Tags (comma-separated)",
                        placeholder="e.g., personal, dreams",
                        lines=1
                    )
                    
                    tag_moment_btn = gr.Button("⭐ Tag Moment", variant="primary")
                    
                    gr.Markdown("---")
                    
                    clear_memory_btn = gr.Button("🗑️ Clear Memories", variant="stop")
                    
                    memory_status = gr.HTML()
                
                with gr.Column(scale=2):
                    memory_display = gr.HTML(
                        get_memory_display(get_character_list()[0] if get_character_list() else None)
                    )
            
            memory_character_select.change(
                fn=get_memory_display,
                inputs=[memory_character_select],
                outputs=[memory_display]
            )
            
            add_fact_btn.click(
                add_manual_memory,
                [memory_character_select, manual_fact],
                [memory_status, memory_display]
            )
            
            tag_moment_btn.click(
                tag_moment,
                [memory_character_select, moment_text, moment_tags],
                [memory_status, memory_display]
            )
            
            clear_memory_btn.click(
                clear_memories,
                [memory_character_select],
                [memory_status, memory_display]
            )
        
        with gr.Tab("➕ Create Character"):
            gr.HTML("""
            <div class='panel-container'>
                <h2 style='color: var(--accent-primary);'>✨ Create a New Character</h2>
                <p>Design your perfect AI companion.</p>
            </div>
            """)
            
            with gr.Column():
                char_name = gr.Textbox(label="Character Name", placeholder="e.g., Sarah")
                char_personality = gr.Textbox(
                    label="Personality (Required)",
                    placeholder="e.g., Witty engineer who loves coffee",
                    lines=3
                )
                char_backstory = gr.Textbox(
                    label="Backstory (Optional)",
                    placeholder="e.g., Former game developer...",
                    lines=5
                )
                char_appearance = gr.Textbox(
                    label="Appearance (Optional)",
                    placeholder="e.g., Mid-30s, brown hair",
                    lines=2
                )
                char_example = gr.Textbox(
                    label="Example Dialogue (Optional)",
                    placeholder="User: Hi!\nSarah: Hey there!",
                    lines=3
                )
                
                create_btn = gr.Button("✨ Create Character", variant="primary", size="lg")
                create_output = gr.HTML()
            
            create_btn.click(
                create_character,
                [char_name, char_personality, char_backstory, char_appearance, char_example],
                [create_output, character_select, char_name]
            )
        
        with gr.Tab("📋 Manage Characters"):
            gr.HTML("""
            <div class='panel-container'>
                <h2 style='color: var(--accent-primary);'>📋 Manage Your Characters</h2>
                <p>View or delete characters.</p>
            </div>
            """)
            
            with gr.Column():
                manage_character_select = gr.Dropdown(
                    choices=get_character_list(),
                    value=get_character_list()[0] if get_character_list() else None,
                    label="Select Character"
                )
                
                manage_character_info = gr.HTML(
                    get_character_info(get_character_list()[0] if get_character_list() else None)
                )
                
                gr.Markdown("---")
                
                delete_btn = gr.Button("❌ Delete This Character", variant="stop", size="lg")
                delete_output = gr.HTML()
            
            manage_character_select.change(
                fn=get_character_info,
                inputs=[manage_character_select],
                outputs=[manage_character_info]
            )
            
            delete_btn.click(
                delete_character,
                [manage_character_select],
                [delete_output, character_select]
            )
        
        with gr.Tab("⚙️ Setup"):
            gr.HTML("""
            <div class='panel-container'>
                <h2 style='color: var(--accent-primary);'>⚙️ System Configuration</h2>
            </div>
            """)
            
            check_btn = gr.Button("🔍 Check AI Backends", variant="primary", size="lg")
            status_display = gr.HTML()
            
            gr.Markdown("---")
            gr.Markdown("### 🤖 Model Management")
            
            with gr.Row():
                model_dropdown_global = gr.Dropdown(
                    choices=available_models if available_models else ["No models"],
                    value=available_models[0] if available_models else "No models",
                    label="Available Models",
                    scale=3
                )
                
                refresh_models_btn = gr.Button("🔄 Refresh", variant="primary", size="lg", scale=1)
            
            refresh_status = gr.HTML()
            
            gr.HTML("""
            <div class='panel-container' style='margin-top: 30px;'>
                <h2>📚 Quick Start</h2>
                <ol>
                    <li>Install <a href='https://ollama.ai' target='_blank'>Ollama</a></li>
                    <li>Run: <code>ollama pull llama3.2</code></li>
                    <li>Click "Check AI Backends"</li>
                    <li>Create a character</li>
                    <li>Start chatting!</li>
                </ol>
                
                <h3>🧠 Memory Features</h3>
                <p>Characters automatically learn:</p>
                <ul>
                    <li>Your name, job, interests</li>
                    <li>Your preferences</li>
                    <li>Important moments</li>
                </ul>
                
                <h3>🎨 Model Recommendations</h3>
                <ul>
                    <li><strong>llama3.2:1b</strong> - Fast (1GB)</li>
                    <li><strong>llama3.2</strong> - Balanced (3GB) ⭐</li>
                    <li><strong>llama3.1:8b</strong> - Best quality (8GB)</li>
                </ul>
            </div>
            """)
            
            check_btn.click(check_backends, None, status_display)
            
            refresh_models_btn.click(
                refresh_models,
                None,
                [model_select, model_dropdown_global, refresh_status]
            )

if __name__ == "__main__":
    print("=" * 70)
    print(f"🎭 {APP_NAME} v{VERSION} - Enhanced UI Edition")
    print("=" * 70)
    print("🎨 Enhanced UI: ENABLED")
    print("🧠 Memory System: ACTIVE")
    print("🔒 Security: Localhost only")
    
    llm = BackendDetector.detect_llm_backends()
    if llm:
        for key, _ in llm:
            if key == 'ollama':
                models = BackendDetector.get_ollama_models()
                if models:
                    available_models = models
                    active_llm = key
                    print(f"✅ Models: {', '.join(models[:3])}")
    else:
        print("⚠️  No LLM detected")
    
    print("\n🌐 Starting web interface...")
    print("=" * 70)
    
    app.launch(
        server_name="127.0.0.1",
        server_port=7861,
        share=False
    )