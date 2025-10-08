"""
ELIZA v0.2 - AI Character Sandbox
Named in honor of ELIZA (1966), the first chatbot, and the ELIZA effect.

A self-hosted AI character creation and chat interface with professional UI.

Requirements:
pip install gradio requests pillow

Supported Backends (user installs separately):
- LLM: Ollama, LM Studio, Text Generation WebUI
- Image: Automatic1111 (coming soon)
"""

import gradio as gr
import json
import os
import requests
import time
from datetime import datetime
from typing import Optional

# ============ CONFIGURATION ============

VERSION = "0.2"
APP_NAME = "ELIZA"

# Backend configuration
LLM_BACKENDS = {
    'ollama': {'url': 'http://localhost:11434', 'name': 'Ollama'},
    'lm_studio': {'url': 'http://localhost:1234', 'name': 'LM Studio'},
    'text_gen_webui': {'url': 'http://localhost:5000', 'name': 'Text Generation WebUI'}
}

IMAGE_BACKENDS = {
    'automatic1111': {'url': 'http://localhost:7862', 'name': 'Automatic1111'}
}

# Global state
characters = {}
chat_histories = {}
active_llm = None
active_image = None
available_models = []

# ============ CUSTOM CSS ============

CUSTOM_CSS = """
/* Main theme - Dark & Sleek */
:root {
    --bg-primary: #1a1a1a;
    --bg-secondary: #242424;
    --bg-tertiary: #2d2d2d;
    --accent-primary: #8b5cf6;
    --accent-secondary: #a78bfa;
    --text-primary: #e5e5e5;
    --text-secondary: #a0a0a0;
    --border-color: #3a3a3a;
    --success: #10b981;
    --warning: #f59e0b;
    --error: #ef4444;
}

/* Global styling */
.gradio-container {
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif !important;
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

/* Chat messages styling */
.message-user {
    background: var(--accent-primary) !important;
    border-radius: 18px 18px 4px 18px !important;
    padding: 12px 16px !important;
    margin: 8px 0 !important;
    max-width: 70% !important;
    margin-left: auto !important;
    color: white !important;
}

.message-bot {
    background: var(--bg-tertiary) !important;
    border-radius: 18px 18px 18px 4px !important;
    padding: 12px 16px !important;
    margin: 8px 0 !important;
    max-width: 70% !important;
    color: var(--text-primary) !important;
    border-left: 3px solid var(--accent-primary) !important;
}

/* Buttons */
.primary-button {
    background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary)) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    font-weight: 600 !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
}

.primary-button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(139, 92, 246, 0.4) !important;
}

/* Input fields */
textarea, input {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
    padding: 10px !important;
}

textarea:focus, input:focus {
    border-color: var(--accent-primary) !important;
    box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2) !important;
}

/* Dropdowns */
select, .dropdown {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
}

/* Cards */
.character-card {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    padding: 16px !important;
    margin: 8px 0 !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
}

.character-card:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
    border-color: var(--accent-primary) !important;
}

/* Status indicators */
.status-online {
    color: var(--success) !important;
}

.status-offline {
    color: var(--error) !important;
}

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.message {
    animation: fadeIn 0.3s ease-out !important;
}

/* Typing indicator */
.typing-indicator {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 12px 16px;
    background: var(--bg-tertiary);
    border-radius: 18px;
    width: fit-content;
}

.typing-dot {
    width: 8px;
    height: 8px;
    background: var(--text-secondary);
    border-radius: 50%;
    animation: typing 1.4s infinite;
}

.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
    0%, 60%, 100% { transform: translateY(0); }
    30% { transform: translateY(-10px); }
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: var(--bg-secondary);
}

::-webkit-scrollbar-thumb {
    background: var(--accent-primary);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--accent-secondary);
}

/* Header */
.app-header {
    background: linear-gradient(135deg, #1a1a1a, #2d2d2d) !important;
    padding: 20px !important;
    border-bottom: 2px solid var(--accent-primary) !important;
    margin-bottom: 20px !important;
}

.app-title {
    font-size: 32px !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary)) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    margin: 0 !important;
}

/* Tabs */
.tabs {
    background: var(--bg-secondary) !important;
    border-radius: 12px !important;
    padding: 4px !important;
}

.tab-nav button {
    color: var(--text-secondary) !important;
    border: none !important;
    padding: 12px 24px !important;
    border-radius: 8px !important;
    transition: all 0.2s !important;
}

.tab-nav button.selected {
    background: var(--accent-primary) !important;
    color: white !important;
}

/* Character avatar placeholder */
.character-avatar {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 32px;
    font-weight: bold;
    color: white;
    margin: 0 auto 12px;
    border: 3px solid var(--border-color);
}
"""

# ============ BACKEND DETECTION ============

class BackendDetector:
    """Detects and connects to local AI backends"""
    
    @staticmethod
    def check_server(url, endpoint=''):
        """Ping server to see if it's running"""
        try:
            response = requests.get(f"{url}{endpoint}", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    @staticmethod
    def detect_llm_backends():
        """Check which LLM servers are running"""
        available = []
        for key, config in LLM_BACKENDS.items():
            if key == 'ollama':
                if BackendDetector.check_server(config['url'], '/api/tags'):
                    available.append((key, config['name']))
            elif key == 'lm_studio':
                if BackendDetector.check_server(config['url'], '/v1/models'):
                    available.append((key, config['name']))
            elif key == 'text_gen_webui':
                if BackendDetector.check_server(config['url'], '/api/v1/model'):
                    available.append((key, config['name']))
        return available
    
    @staticmethod
    def get_ollama_models():
        """Get list of installed Ollama models"""
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=2)
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])
                return [model['name'] for model in models]
        except Exception as e:
            print(f"Error getting Ollama models: {e}")
        return []
    
    @staticmethod
    def get_lm_studio_models():
        """Get list of loaded LM Studio models"""
        try:
            response = requests.get('http://localhost:1234/v1/models', timeout=2)
            if response.status_code == 200:
                models = response.json().get('data', [])
                return [model['id'] for model in models]
        except:
            pass
        return []

# ============ AI CLIENT ============

class LocalLLMClient:
    """Unified client for local LLM backends"""
    
    def __init__(self, backend_key):
        self.backend = backend_key
        self.url = LLM_BACKENDS[backend_key]['url']
    
    def generate(self, prompt, model, temperature=0.8, max_tokens=200):
        """Generate text from prompt"""
        try:
            if self.backend == 'ollama':
                return self._ollama_generate(prompt, model, temperature, max_tokens)
            elif self.backend == 'lm_studio':
                return self._openai_format_generate(prompt, model, temperature, max_tokens)
            elif self.backend == 'text_gen_webui':
                return self._text_gen_webui_generate(prompt, temperature, max_tokens)
        except Exception as e:
            raise Exception(f"AI generation error: {str(e)}")
    
    def _ollama_generate(self, prompt, model, temperature, max_tokens):
        response = requests.post(
            f"{self.url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            },
            timeout=120
        )
        return response.json()["response"]
    
    def _openai_format_generate(self, prompt, model, temperature, max_tokens):
        response = requests.post(
            f"{self.url}/v1/chat/completions",
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens
            },
            timeout=120
        )
        return response.json()["choices"][0]["message"]["content"]
    
    def _text_gen_webui_generate(self, prompt, temperature, max_tokens):
        response = requests.post(
            f"{self.url}/api/v1/generate",
            json={
                "prompt": prompt,
                "temperature": temperature,
                "max_new_tokens": max_tokens
            },
            timeout=120
        )
        return response.json()["results"][0]["text"]

# ============ CHARACTER MANAGEMENT ============

def create_character(name, personality, backstory, appearance, example_dialogue):
    """Create a new character"""
    if not name or not personality:
        return "❌ Name and personality are required!", "", gr.Dropdown(), gr.Dropdown(), gr.Dropdown()
    
    if name in characters:
        return f"❌ Character '{name}' already exists!", "", gr.Dropdown(), gr.Dropdown(), gr.Dropdown()
    
    characters[name] = {
        "name": name,
        "personality": personality,
        "backstory": backstory,
        "appearance": appearance,
        "example_dialogue": example_dialogue,
        "created": datetime.now().isoformat(),
        "avatar": None
    }
    
    chat_histories[name] = []
    save_character_to_file(name)
    
    # Get updated character list
    char_list = list(characters.keys())
    
    return (
        f"✅ Character '{name}' created successfully!",
        "",
        gr.Dropdown(choices=char_list, value=name),
        gr.Dropdown(choices=char_list, value=name),
        gr.Dropdown(choices=char_list, value=name)
    )

def save_character_to_file(name):
    """Save character to JSON file"""
    os.makedirs("characters", exist_ok=True)
    filepath = f"characters/{name}.json"
    
    char_data = characters[name].copy()
    char_data.pop('avatar', None)  # Don't save binary data
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(char_data, f, indent=2, ensure_ascii=False)

def load_characters_from_files():
    """Load all characters from files"""
    if not os.path.exists("characters"):
        return
    
    for filename in os.listdir("characters"):
        if filename.endswith(".json"):
            try:
                with open(f"characters/{filename}", 'r', encoding='utf-8') as f:
                    char_data = json.load(f)
                    name = char_data["name"]
                    characters[name] = char_data
                    if name not in chat_histories:
                        chat_histories[name] = []
            except Exception as e:
                print(f"Error loading {filename}: {e}")

def delete_character(name):
    """Delete a character"""
    if name in characters:
        del characters[name]
        if name in chat_histories:
            del chat_histories[name]
        
        filepath = f"characters/{name}.json"
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return f"✅ Character '{name}' deleted."
    return "❌ Character not found."

def get_character_info(name):
    """Get formatted character info for display"""
    if not name or name not in characters:
        return "No character selected", "", "", ""
    
    char = characters[name]
    initials = ''.join([word[0].upper() for word in name.split()[:2]])
    
    # Short personality preview
    personality_preview = char['personality'][:100] + "..." if len(char['personality']) > 100 else char['personality']
    
    return (
        f"### {name}\n\n{personality_preview}",
        initials,
        char.get('personality', ''),
        char.get('backstory', '')
    )

# ============ CHAT FUNCTIONS ============

def build_prompt(character_name, user_message):
    """Build the AI prompt with character context"""
    if character_name not in characters:
        return None
    
    char = characters[character_name]
    
    prompt = f"""You are roleplaying as {char['name']}.

Personality: {char['personality']}

Backstory: {char['backstory']}
"""
    
    if char.get('appearance'):
        prompt += f"\nAppearance: {char['appearance']}\n"
    
    if char.get('example_dialogue'):
        prompt += f"\nExample dialogue style:\n{char['example_dialogue']}\n"
    
    # Add recent conversation history
    history = chat_histories.get(character_name, [])
    if history:
        prompt += "\nRecent conversation:\n"
        for user_msg, ai_msg in history[-3:]:  # Last 3 exchanges
            prompt += f"User: {user_msg}\n{char['name']}: {ai_msg}\n"
    
    prompt += f"\nUser: {user_message}\n{char['name']}:"
    
    return prompt

def chat_with_character(character_name, user_message, history, model, temperature, max_tokens):
    """Handle chat interaction"""
    global active_llm
    
    if not active_llm:
        return history + [("Error", "❌ No AI backend detected. Check Setup tab.")], ""
    
    if not character_name or character_name not in characters:
        return history + [("Error", "Please select a character first.")], ""
    
    if not user_message.strip():
        return history, ""
    
    # Show typing indicator (simulated)
    prompt = build_prompt(character_name, user_message)
    
    try:
        client = LocalLLMClient(active_llm)
        ai_response = client.generate(prompt, model, temperature, max_tokens)
        ai_response = ai_response.strip()
        
        # Save to history
        chat_histories[character_name].append((user_message, ai_response))
        
        # Return updated chat
        return history + [(user_message, ai_response)], ""
        
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        return history + [(user_message, error_msg)], ""

def clear_chat(character_name):
    """Clear chat history"""
    if character_name in chat_histories:
        chat_histories[character_name] = []
    return []

# ============ BACKEND MANAGEMENT ============

def check_backends():
    """Check AI backend status"""
    global active_llm, available_models
    
    llm_backends = BackendDetector.detect_llm_backends()
    
    status = "# 🔍 Backend Status\n\n"
    
    if llm_backends:
        status += "## ✅ LLM Backends Active\n\n"
        for key, name in llm_backends:
            status += f"- **{name}**"
            
            if key == 'ollama':
                models = BackendDetector.get_ollama_models()
                if models:
                    status += f" ({len(models)} models)\n"
                    if not active_llm:
                        active_llm = key
                        available_models = models
            elif key == 'lm_studio':
                models = BackendDetector.get_lm_studio_models()
                if models:
                    status += f" ({len(models)} models)\n"
                    if not active_llm:
                        active_llm = key
                        available_models = models
        
        status += f"\n**Active:** {LLM_BACKENDS.get(active_llm, {}).get('name', 'None')}\n"
    else:
        status += "## ❌ No LLM Backends Detected\n\n"
        status += "Install [Ollama](https://ollama.ai) or [LM Studio](https://lmstudio.ai)\n"
    
    status += "\n---\n\n## 🎨 Image Generation\n\n"
    status += "⚠️ **Coming Soon** - Automatic1111 integration\n"
    
    return status

def refresh_models():
    """Refresh available models"""
    global active_llm, available_models
    
    llm_backends = BackendDetector.detect_llm_backends()
    
    if llm_backends:
        for key, name in llm_backends:
            if key == 'ollama':
                models = BackendDetector.get_ollama_models()
                if models:
                    active_llm = key
                    available_models = models
                    return gr.Dropdown(choices=models, value=models[0]), f"✅ Found {len(models)} models"
            elif key == 'lm_studio':
                models = BackendDetector.get_lm_studio_models()
                if models:
                    active_llm = key
                    available_models = models
                    return gr.Dropdown(choices=models, value=models[0]), f"✅ Found {len(models)} models"
    
    return gr.Dropdown(choices=["No models"], value="No models"), "❌ No backends found"

# ============ INITIALIZATION ============

load_characters_from_files()

# ============ UI CONSTRUCTION ============

with gr.Blocks(title=f"{APP_NAME} - AI Character Sandbox", css=CUSTOM_CSS, theme=gr.themes.Base()) as app:
    
    # Header
    with gr.Row(elem_classes="app-header"):
        gr.Markdown(f"""
        <div class="app-title">🎭 {APP_NAME}</div>
        <div style="color: var(--text-secondary); font-size: 14px; margin-top: 4px;">
            v{VERSION} · AI Character Sandbox · Named after ELIZA (1966)
        </div>
        """)
    
    gr.Markdown("""
    <div style="text-align: center; color: var(--text-secondary); margin: 20px 0; padding: 12px; background: var(--bg-secondary); border-radius: 8px;">
        ⚠️ <strong>18+ Only</strong> · Self-hosted AI · Complete privacy · You control everything
    </div>
    """)
    
    with gr.Tabs():
        
        # ============ CHAT TAB ============
        with gr.Tab("💬 Chat", id="chat"):
            with gr.Row():
                # Left sidebar - Character info
                with gr.Column(scale=1, min_width=250):
                    gr.Markdown("### Active Character")
                    
                    char_select = gr.Dropdown(
                        choices=list(characters.keys()),
                        label="Select Character",
                        interactive=True,
                        elem_classes="dropdown"
                    )
                    
                    character_info_display = gr.Markdown("No character selected")
                    
                    gr.Markdown("---")
                    gr.Markdown("### AI Settings")
                    
                    model_select = gr.Dropdown(
                        choices=available_models if available_models else ["No models"],
                        value=available_models[0] if available_models else "No models",
                        label="Model",
                        interactive=True
                    )
                    
                    refresh_models_btn = gr.Button("🔄 Refresh Models", size="sm")
                    refresh_status = gr.Textbox(label="Status", value="", interactive=False, visible=False)
                    
                    temperature = gr.Slider(
                        minimum=0.1,
                        maximum=2.0,
                        value=0.9,
                        step=0.1,
                        label="Creativity",
                        info="Higher = more creative"
                    )
                    
                    max_tokens = gr.Slider(
                        minimum=50,
                        maximum=500,
                        value=200,
                        step=50,
                        label="Response Length"
                    )
                    
                    clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary", size="sm")
                
                # Right side - Chat window
                with gr.Column(scale=3):
                    chatbot = gr.Chatbot(
                        label="Conversation",
                        height=600,
                        type="tuples",
                        show_label=False,
                        avatar_images=(None, None)
                    )
                    
                    with gr.Row():
                        msg_input = gr.Textbox(
                            label="Message",
                            placeholder="Type your message here...",
                            show_label=False,
                            scale=4,
                            lines=2
                        )
                        send_btn = gr.Button("Send ➤", variant="primary", scale=1, elem_classes="primary-button")
        
        # ============ CREATE CHARACTER TAB ============
        with gr.Tab("✨ Create Character", id="create"):
            gr.Markdown("### Create a New Character")
            
            with gr.Row():
                with gr.Column():
                    char_name = gr.Textbox(
                        label="Character Name",
                        placeholder="e.g., Sarah Chen",
                        info="Give your character a name"
                    )
                    
                    char_personality = gr.Textbox(
                        label="Personality",
                        placeholder="e.g., Witty software engineer, loves coffee and puns, always optimistic",
                        lines=3,
                        info="Describe their personality traits"
                    )
                    
                    char_backstory = gr.Textbox(
                        label="Backstory",
                        placeholder="e.g., Former game developer turned AI researcher. Spent 10 years in Silicon Valley before moving to a quiet town to focus on creative projects...",
                        lines=5,
                        info="Their history and background"
                    )
                    
                    char_appearance = gr.Textbox(
                        label="Appearance (Optional)",
                        placeholder="e.g., Mid-30s, shoulder-length brown hair, green eyes, usually wears hoodies and jeans",
                        lines=3,
                        info="Physical description"
                    )
                    
                    char_example = gr.Textbox(
                        label="Example Dialogue (Optional)",
                        placeholder="User: How's your day?\nSarah: Pretty good! Just debugging some code and fueling up on espresso. The usual chaos! ☕",
                        lines=4,
                        info="Example of how they talk"
                    )
                    
                    create_btn = gr.Button("✨ Create Character", variant="primary", elem_classes="primary-button")
                    create_output = gr.Textbox(label="Status", interactive=False)
        
        # ============ MANAGE CHARACTERS TAB ============
        with gr.Tab("📋 Manage", id="manage"):
            gr.Markdown("### Manage Your Characters")
            
            with gr.Row():
                with gr.Column(scale=1):
                    manage_char_select = gr.Dropdown(
                        choices=list(characters.keys()),
                        label="Select Character"
                    )
                    
                    load_btn = gr.Button("📖 Load Details", variant="secondary")
                    delete_btn = gr.Button("🗑️ Delete Character", variant="stop")
                    manage_status = gr.Textbox(label="Status", interactive=False)
                
                with gr.Column(scale=2):
                    view_name = gr.Textbox(label="Name", interactive=False)
                    view_personality = gr.Textbox(label="Personality", lines=3, interactive=False)
                    view_backstory = gr.Textbox(label="Backstory", lines=5, interactive=False)
                    view_appearance = gr.Textbox(label="Appearance", lines=3, interactive=False)
                    view_example = gr.Textbox(label="Example Dialogue", lines=4, interactive=False)
        
        # ============ EXPORT TAB ============
        with gr.Tab("📤 Export", id="export"):
            gr.Markdown("""
            ### Export Character
            
            Share your character as a JSON file. **AI models not included** - recipients must use their own.
            """)
            
            export_char_select = gr.Dropdown(
                choices=list(characters.keys()),
                label="Character to Export"
            )
            
            export_btn = gr.Button("📤 Export Character", variant="primary", elem_classes="primary-button")
            export_output = gr.Code(label="Character JSON", language="json", lines=20)
        
        # ============ SETUP TAB ============
        with gr.Tab("⚙️ Setup", id="setup"):
            gr.Markdown("### System Setup & Configuration")
            
            check_btn = gr.Button("🔍 Check AI Backends", variant="primary", size="lg", elem_classes="primary-button")
            status_display = gr.Markdown()
            
            gr.Markdown("""
            ---
            
            ### Quick Start Guide
            
            **1. Install Ollama (Required for chat):**
            - Download: [ollama.ai](https://ollama.ai)
            - Run: `ollama pull llama3.2`
            - Click "Check AI Backends" above
            
            **2. Install LM Studio (Alternative):**
            - Download: [lmstudio.ai](https://lmstudio.ai)
            - Load a model and start server
            
            **3. Create a character in the ✨ Create tab**
            
            **4. Start chatting in the 💬 Chat tab!**
            
            ---
            
            ### Coming Soon
            
            - 🎨 **Image Generation** - Character portraits via Automatic1111
            - 🎤 **Voice Chat** - Text-to-speech responses
            - 👥 **Group Chats** - Multiple characters in one conversation
            - 🧠 **Memory System** - Characters remember past conversations
            - 🌐 **Character Marketplace** - Share and discover characters
            
            """)
    
    # ============ EVENT HANDLERS ============
    
    # Character selection updates info
    def on_character_select(name):
        info, initials, personality, backstory = get_character_info(name)
        return info
    
    char_select.change(on_character_select, char_select, character_info_display)
    
    # Refresh models
    refresh_models_btn.click(refresh_models, None, [model_select, refresh_status])
    
    # Chat handlers
    msg_input.submit(
        chat_with_character,
        [char_select, msg_input, chatbot, model_select, temperature, max_tokens],
        [chatbot, msg_input]
    )
    
    send_btn.click(
        chat_with_character,
        [char_select, msg_input, chatbot, model_select, temperature, max_tokens],
        [chatbot, msg_input]
    )
    
    clear_btn.click(clear_chat, char_select, chatbot)
    
    # Create character - with automatic refresh
    def create_and_refresh(name, personality, backstory, appearance, example_dialogue):
        result = create_character(name, personality, backstory, appearance, example_dialogue)
        char_list = list(characters.keys())
        return (
            result[0],  # status message
            result[1],  # cleared name field
            gr.Dropdown(choices=char_list, value=char_list[-1] if char_list else None),  # chat dropdown
            gr.Dropdown(choices=char_list, value=char_list[-1] if char_list else None),  # manage dropdown
            gr.Dropdown(choices=char_list, value=char_list[-1] if char_list else None)   # export dropdown
        )
    
    create_btn.click(
        create_and_refresh,
        [char_name, char_personality, char_backstory, char_appearance, char_example],
        [create_output, char_name, char_select, manage_char_select, export_char_select]
    )
    
    # Manage characters
    def load_character_details(name):
        if not name or name not in characters:
            return "", "", "", "", ""
        char = characters[name]
        return (
            char['name'],
            char.get('personality', ''),
            char.get('backstory', ''),
            char.get('appearance', ''),
            char.get('example_dialogue', '')
        )
    
    load_btn.click(
        load_character_details,
        manage_char_select,
        [view_name, view_personality, view_backstory, view_appearance, view_example]
    )
    
    delete_btn.click(delete_character, manage_char_select, manage_status)
    
    # Export character
    def export_character(name):
        if not name or name not in characters:
            return "❌ Character not found"
        
        char = characters[name].copy()
        char.pop('avatar', None)
        
        export_data = {
            "format": "eliza_character_v1",
            "version": VERSION,
            "character": char,
            "exported": datetime.now().isoformat(),
            "note": "AI models and avatars not included. Import to ELIZA to use."
        }
        
        return json.dumps(export_data, indent=2, ensure_ascii=False)
    
    export_btn.click(export_character, export_char_select, export_output)
    
    # Check backends
    check_btn.click(check_backends, None, status_display)

# ============ LAUNCH ============

if __name__ == "__main__":
    print("=" * 60)
    print(f"🎭 {APP_NAME} v{VERSION} - AI Character Sandbox")
    print("=" * 60)
    print("📂 Characters saved to ./characters/")
    print("🔍 Checking for AI backends...")
    
    # Initial backend check
    llm = BackendDetector.detect_llm_backends()
    
    if llm:
        print(f"✅ Found LLM backends: {', '.join([name for _, name in llm])}")
        # Auto-detect models
        for key, name in llm:
            if key == 'ollama':
                models = BackendDetector.get_ollama_models()
                if models:
                    available_models = models
                    active_llm = key
                    print(f"✅ Ollama models: {', '.join(models)}")
    else:
        print("⚠️  No LLM backends detected.")
        print("    Install Ollama: https://ollama.ai")
    
    print("\n🌐 Starting web interface...")
    print("=" * 60)
    
    app.launch(
        server_name="0.0.0.0",
        server_port=7861,
        share=False,
        show_error=True
    )
