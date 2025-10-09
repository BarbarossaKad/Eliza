"""
ELIZA v0.3 - AI Character Sandbox
Named in honor of ELIZA (1966), the first chatbot, and the ELIZA effect.

Simple character-based chat system - one conversation per character.

Requirements:
pip install gradio requests pillow
"""

import gradio as gr
import json
import os
import requests
from datetime import datetime

# ============ CONFIGURATION ============

VERSION = "0.3"
APP_NAME = "ELIZA"

LLM_BACKENDS = {
    'ollama': {'url': 'http://localhost:11434', 'name': 'Ollama'},
    'lm_studio': {'url': 'http://localhost:1234', 'name': 'LM Studio'},
    'text_gen_webui': {'url': 'http://localhost:5000', 'name': 'Text Generation WebUI'}
}

# Global state
characters = {}
chat_histories = {}  # Simple: {character_name: [(user, ai), ...]}
active_llm = None
available_models = []

# ============ CUSTOM CSS ============

CUSTOM_CSS = """
:root {
    --bg-primary: #1a1a1a;
    --bg-secondary: #242424;
    --bg-tertiary: #2d2d2d;
    --accent-primary: #8b5cf6;
    --accent-secondary: #a78bfa;
    --text-primary: #e5e5e5;
    --text-secondary: #a0a0a0;
    --border-color: #3a3a3a;
}

.gradio-container {
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif !important;
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

.primary-button {
    background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary)) !important;
    color: white !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: transform 0.2s !important;
}

.primary-button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(139, 92, 246, 0.4) !important;
}

textarea, input {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
}

::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: var(--bg-secondary);
}

::-webkit-scrollbar-thumb {
    background: var(--accent-primary);
    border-radius: 4px;
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
            elif key == 'lm_studio':
                if BackendDetector.check_server(config['url'], '/v1/models'):
                    available.append((key, config['name']))
            elif key == 'text_gen_webui':
                if BackendDetector.check_server(config['url'], '/api/v1/model'):
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
                return response.json()["response"]
        except Exception as e:
            raise Exception(f"AI error: {str(e)}")

# ============ CHARACTER MANAGEMENT ============

def create_character(name, personality, backstory, appearance, example_dialogue):
    if not name or not personality:
        return "❌ Name and personality required!", "", None
    
    if name in characters:
        return f"❌ Character '{name}' already exists!", "", None
    
    characters[name] = {
        "name": name,
        "personality": personality,
        "backstory": backstory,
        "appearance": appearance,
        "example_dialogue": example_dialogue,
        "created": datetime.now().isoformat()
    }
    
    chat_histories[name] = []
    save_character_to_file(name)
    
    return f"✅ Character '{name}' created!", "", gr.Tabs(selected=get_character_tab_index(name))

def save_character_to_file(name):
    os.makedirs("characters", exist_ok=True)
    
    # Save character data
    char_file = f"characters/{name}.json"
    with open(char_file, 'w', encoding='utf-8') as f:
        json.dump(characters[name], f, indent=2, ensure_ascii=False)
    
    # Save chat history
    history_file = f"characters/{name}_history.json"
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(chat_histories.get(name, []), f, indent=2, ensure_ascii=False)

def load_characters_from_files():
    if not os.path.exists("characters"):
        return
    
    for filename in os.listdir("characters"):
        if filename.endswith(".json") and not filename.endswith("_history.json"):
            try:
                with open(f"characters/{filename}", 'r', encoding='utf-8') as f:
                    char_data = json.load(f)
                    name = char_data["name"]
                    characters[name] = char_data
                    
                    # Load history
                    history_file = f"characters/{name}_history.json"
                    if os.path.exists(history_file):
                        with open(history_file, 'r', encoding='utf-8') as hf:
                            chat_histories[name] = json.load(hf)
                    else:
                        chat_histories[name] = []
            except Exception as e:
                print(f"Error loading {filename}: {e}")

def delete_character(name):
    if name in characters:
        del characters[name]
        if name in chat_histories:
            del chat_histories[name]
        
        char_file = f"characters/{name}.json"
        if os.path.exists(char_file):
            os.remove(char_file)
        
        history_file = f"characters/{name}_history.json"
        if os.path.exists(history_file):
            os.remove(history_file)
        
        return f"✅ '{name}' deleted"
    return "❌ Character not found"

def get_character_tab_index(name):
    """Get the tab index for a character (0-indexed, +1 for the 'New Character' tab)"""
    char_list = sorted(characters.keys())
    if name in char_list:
        return char_list.index(name)
    return 0

# ============ CHAT FUNCTIONS ============

def build_prompt(character_name, user_message):
    if character_name not in characters:
        return None
    
    char = characters[character_name]
    
    prompt = f"""You are roleplaying as {char['name']}. This is fictional creative writing.

CRITICAL: Stay in character. Respond naturally as {char['name']} would.

Character:
- Name: {char['name']}
- Personality: {char['personality']}
- Backstory: {char['backstory']}"""
    
    if char.get('appearance'):
        prompt += f"\n- Appearance: {char['appearance']}"
    
    if char.get('example_dialogue'):
        prompt += f"\n\nExample dialogue:\n{char['example_dialogue']}"
    
    history = chat_histories.get(character_name, [])
    if history:
        prompt += f"\n\nRecent conversation:\n"
        for user_msg, ai_msg in history[-5:]:  # Last 5 exchanges
            prompt += f"User: {user_msg}\n{char['name']}: {ai_msg}\n"
    
    prompt += f"\n\nUser: {user_message}\n{char['name']}:"
    
    return prompt

def chat_with_character(character_name, user_message, history, model, temperature, max_tokens):
    global active_llm
    
    if not active_llm:
        return history + [("Error", "❌ No AI backend. Check Setup tab.")], ""
    
    if not character_name or character_name not in characters:
        return history + [("Error", "Select a character first.")], ""
    
    if not user_message.strip():
        return history, ""
    
    prompt = build_prompt(character_name, user_message)
    
    try:
        client = LocalLLMClient(active_llm)
        ai_response = client.generate(prompt, model, temperature, max_tokens).strip()
        
        # Save to history
        if character_name not in chat_histories:
            chat_histories[character_name] = []
        
        chat_histories[character_name].append((user_message, ai_response))
        save_character_to_file(character_name)
        
        return history + [(user_message, ai_response)], ""
        
    except Exception as e:
        return history + [(user_message, f"❌ Error: {str(e)}")], ""

def clear_chat(character_name):
    if character_name in chat_histories:
        chat_histories[character_name] = []
        save_character_to_file(character_name)
    return []

def get_chat_history(character_name):
    return chat_histories.get(character_name, [])

# ============ BACKEND MANAGEMENT ============

def check_backends():
    global active_llm, available_models
    
    llm_backends = BackendDetector.detect_llm_backends()
    
    status = "# 🔍 Backend Status\n\n"
    
    if llm_backends:
        status += "## ✅ LLM Active\n\n"
        for key, name in llm_backends:
            if key == 'ollama':
                models = BackendDetector.get_ollama_models()
                if models:
                    status += f"- **{name}**: {len(models)} models\n"
                    if not active_llm:
                        active_llm = key
                        available_models = models
    else:
        status += "## ❌ No LLM Detected\n\nInstall [Ollama](https://ollama.ai)\n"
    
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
                    return gr.Dropdown(choices=models, value=models[0]), f"✅ {len(models)} models"
    
    return gr.Dropdown(choices=["No models"], value="No models"), "❌ No backends"

# ============ INITIALIZATION ============

load_characters_from_files()

# ============ UI CONSTRUCTION ============

with gr.Blocks(title=f"{APP_NAME} - AI Character Sandbox", css=CUSTOM_CSS, theme=gr.themes.Base()) as app:
    
    # Header
    gr.Markdown(f"""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #1a1a1a, #2d2d2d); border-bottom: 2px solid #8b5cf6; margin-bottom: 20px;">
        <h1 style="font-size: 36px; margin: 0; background: linear-gradient(135deg, #8b5cf6, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            🎭 {APP_NAME}
        </h1>
        <p style="color: #a0a0a0; margin: 5px 0 0 0;">v{VERSION} · AI Character Sandbox · One conversation per character</p>
    </div>
    """)
    
    gr.Markdown("""
    <div style="text-align: center; color: #a0a0a0; margin: 10px 0; padding: 10px; background: #242424; border-radius: 8px;">
        ⚠️ <strong>18+ Only</strong> · Self-hosted · Private · You control everything
    </div>
    """)
    
    # Main tabs - one tab per character + special tabs
    with gr.Tabs() as main_tabs:
        
        # Character chat tabs (dynamically created)
        character_chat_components = {}
        all_model_dropdowns = []  # Track all model dropdowns for updating
        
        for char_name in sorted(characters.keys()):
            with gr.Tab(f"👤 {char_name}", id=f"char_{char_name}"):
                with gr.Row():
                    with gr.Column(scale=1, min_width=200):
                        gr.Markdown(f"### 💬 {char_name}")
                        
                        char_info = characters[char_name]
                        personality_preview = char_info['personality'][:150] + "..." if len(char_info['personality']) > 150 else char_info['personality']
                        gr.Markdown(f"*{personality_preview}*")
                        
                        gr.Markdown("---")
                        gr.Markdown("### AI Settings")
                        
                        model_select = gr.Dropdown(
                            choices=available_models if available_models else ["No models"],
                            value=available_models[0] if available_models else "No models",
                            label="Model"
                        )
                        
                        all_model_dropdowns.append(model_select)  # Track this dropdown
                        
                        temperature = gr.Slider(0.1, 2.0, 0.9, step=0.1, label="Creativity")
                        max_tokens = gr.Slider(50, 500, 200, step=50, label="Length")
                        
                        gr.Markdown("---")
                        
                        clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary", size="sm")
                        delete_char_btn = gr.Button("❌ Delete Character", variant="stop", size="sm")
                        delete_status = gr.Textbox(label="", visible=False)
                    
                    with gr.Column(scale=3):
                        chatbot = gr.Chatbot(
                            label=f"Conversation with {char_name}",
                            value=get_chat_history(char_name),
                            height=600,
                            type="tuples"
                        )
                        
                        with gr.Row():
                            msg_input = gr.Textbox(
                                placeholder=f"Message {char_name}...",
                                show_label=False,
                                scale=4,
                                lines=2
                            )
                            send_btn = gr.Button("Send ➤", variant="primary", scale=1)
                
                # Store components for event handlers
                character_chat_components[char_name] = {
                    'chatbot': chatbot,
                    'msg_input': msg_input,
                    'send_btn': send_btn,
                    'clear_btn': clear_btn,
                    'delete_btn': delete_char_btn,
                    'delete_status': delete_status,
                    'model_select': model_select,
                    'temperature': temperature,
                    'max_tokens': max_tokens
                }
                
                # Chat handlers for this character
                def make_chat_handler(name):
                    def handler(user_msg, history, model, temp, tokens):
                        return chat_with_character(name, user_msg, history, model, temp, tokens)
                    return handler
                
                def make_clear_handler(name):
                    def handler():
                        return clear_chat(name)
                    return handler
                
                def make_delete_handler(name):
                    def handler():
                        result = delete_character(name)
                        return gr.Textbox(value=result, visible=True)
                    return handler
                
                chat_handler = make_chat_handler(char_name)
                clear_handler = make_clear_handler(char_name)
                delete_handler = make_delete_handler(char_name)
                
                msg_input.submit(
                    chat_handler,
                    [msg_input, chatbot, model_select, temperature, max_tokens],
                    [chatbot, msg_input]
                )
                
                send_btn.click(
                    chat_handler,
                    [msg_input, chatbot, model_select, temperature, max_tokens],
                    [chatbot, msg_input]
                )
                
                clear_btn.click(clear_handler, None, chatbot)
                delete_char_btn.click(delete_handler, None, delete_status)
        
        # New Character tab
        with gr.Tab("➕ New Character", id="new_char"):
            gr.Markdown("### Create a New Character")
            
            with gr.Column():
                char_name = gr.Textbox(label="Name", placeholder="e.g., Sarah")
                char_personality = gr.Textbox(
                    label="Personality",
                    placeholder="e.g., Witty, loves coffee, software engineer",
                    lines=3
                )
                char_backstory = gr.Textbox(
                    label="Backstory",
                    placeholder="e.g., Former game dev, now AI researcher...",
                    lines=5
                )
                char_appearance = gr.Textbox(
                    label="Appearance (Optional)",
                    placeholder="e.g., Mid-30s, brown hair, green eyes",
                    lines=2
                )
                char_example = gr.Textbox(
                    label="Example Dialogue (Optional)",
                    placeholder="User: Hi!\nSarah: Hey! Ready to code?",
                    lines=3
                )
                
                create_btn = gr.Button("✨ Create Character", variant="primary", size="lg")
                create_output = gr.Textbox(label="Status", interactive=False)
        
        # Setup tab
        with gr.Tab("⚙️ Setup", id="setup"):
            gr.Markdown("### System Configuration")
            
            check_btn = gr.Button("🔍 Check AI Backends", variant="primary", size="lg")
            status_display = gr.Markdown()
            
            gr.Markdown("---")
            
            model_dropdown_global = gr.Dropdown(
                choices=available_models if available_models else ["No models"],
                value=available_models[0] if available_models else "No models",
                label="Available Models"
            )
            
            refresh_models_btn = gr.Button("🔄 Refresh & Update All Dropdowns", variant="primary", size="sm")
            refresh_status = gr.Textbox(label="", interactive=False)
            
            gr.Markdown("""
            ---
            
            ### Quick Start
            
            1. **Install Ollama**: [ollama.ai](https://ollama.ai)
            2. **Get a model**: `ollama pull llama3.2`
            3. **Click "Check AI Backends" above**
            4. **Create a character**
            5. **Start chatting!**
            
            ### Tips
            
            - Each character has one continuous conversation
            - Click a character's tab to switch to their chat
            - All data stored locally in `./characters/`
            - Bigger models = better responses (try `llama3.2` instead of `llama3.2:1b`)
            """)
    
    # Event handlers for new character creation
    def create_and_reload(name, personality, backstory, appearance, example):
        result_msg, cleared_name, _ = create_character(name, personality, backstory, appearance, example)
        
        if "✅" in result_msg:
            # Character created successfully - need to reload page to show new tab
            return (
                result_msg + "\n\n**Refresh the page to see your new character!**",
                cleared_name
            )
        else:
            return result_msg, name
    
    create_btn.click(
        create_and_reload,
        [char_name, char_personality, char_backstory, char_appearance, char_example],
        [create_output, char_name]
    )
    
    check_btn.click(check_backends, None, status_display)
    
    def refresh_all_dropdowns():
        global active_llm, available_models
        
        llm_backends = BackendDetector.detect_llm_backends()
        
        if llm_backends:
            for key, name in llm_backends:
                if key == 'ollama':
                    models = BackendDetector.get_ollama_models()
                    if models:
                        active_llm = key
                        available_models = models
                        
                        # Return updated dropdowns for all components
                        updates = [gr.Dropdown(choices=models, value=models[0])] * (len(all_model_dropdowns) + 1)
                        updates.append(f"✅ Updated {len(all_model_dropdowns)} character dropdowns with {len(models)} models")
                        return updates
        
        # No models found
        no_model_updates = [gr.Dropdown(choices=["No models"], value="No models")] * (len(all_model_dropdowns) + 1)
        no_model_updates.append("❌ No backends found. Install Ollama and run 'ollama pull llama3.2'")
        return no_model_updates
    
    # Connect refresh button to update all dropdowns
    refresh_models_btn.click(
        refresh_all_dropdowns,
        None,
        all_model_dropdowns + [model_dropdown_global, refresh_status]
    )

if __name__ == "__main__":
    print("=" * 60)
    print(f"🎭 {APP_NAME} v{VERSION}")
    print("=" * 60)
    print("📂 Characters: ./characters/")
    print("🔍 Checking backends...")
    
    llm = BackendDetector.detect_llm_backends()
    if llm:
        print(f"✅ LLM: {', '.join([n for _, n in llm])}")
        for key, _ in llm:
            if key == 'ollama':
                models = BackendDetector.get_ollama_models()
                if models:
                    available_models = models
                    active_llm = key
                    print(f"✅ Models: {', '.join(models)}")
    else:
        print("⚠️  No LLM detected")
    
    print("\n🌐 Starting...")
    print("=" * 60)
    
    app.launch(
        server_name="0.0.0.0",
        server_port=7861,
        share=False
    )
