"""
ELIZA v0.4 - AI Character Sandbox
Named in honor of ELIZA (1966), the first chatbot, and the ELIZA effect.

CHANGELOG v0.4:
- Fixed: Security - localhost only binding
- Fixed: Dynamic character creation (no refresh needed!)
- Improved: Single chat interface with character selector
- Improved: Better error handling
- Improved: Input validation

Requirements:
pip install gradio requests
"""

import gradio as gr
import json
import os
import requests
from datetime import datetime

# ============ CONFIGURATION ============

VERSION = "0.4"
APP_NAME = "ELIZA"

LLM_BACKENDS = {
    'ollama': {'url': 'http://localhost:11434', 'name': 'Ollama'},
    'lm_studio': {'url': 'http://localhost:1234', 'name': 'LM Studio'},
    'text_gen_webui': {'url': 'http://localhost:5000', 'name': 'Text Generation WebUI'}
}

# Global state
characters = {}
chat_histories = {}
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
                response.raise_for_status()
                return response.json()["response"]
        except requests.exceptions.Timeout:
            raise Exception("⏱️ AI timeout - model may be too large or busy")
        except requests.exceptions.ConnectionError:
            raise Exception("🔌 Cannot connect to AI backend - is it running?")
        except KeyError:
            raise Exception("📦 Unexpected response format from AI")
        except Exception as e:
            raise Exception(f"AI error: {str(e)}")

# ============ CHARACTER MANAGEMENT ============

def validate_character_name(name):
    """Validate character name for file system safety"""
    if not name or not name.strip():
        return False, "Name cannot be empty"
    
    name = name.strip()
    
    if len(name) < 2:
        return False, "Name must be at least 2 characters"
    
    if len(name) > 50:
        return False, "Name too long (max 50 characters)"
    
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    if any(c in name for c in invalid_chars):
        return False, f"Name contains invalid characters: {', '.join(invalid_chars)}"
    
    return True, name

def create_character(name, personality, backstory, appearance, example_dialogue):
    # Validate name
    valid, result = validate_character_name(name)
    if not valid:
        return f"❌ {result}", gr.Dropdown(), ""
    
    name = result
    
    if not personality or not personality.strip():
        return "❌ Personality is required!", gr.Dropdown(), ""
    
    if name in characters:
        return f"❌ Character '{name}' already exists!", gr.Dropdown(), ""
    
    characters[name] = {
        "name": name,
        "personality": personality.strip(),
        "backstory": backstory.strip() if backstory else "",
        "appearance": appearance.strip() if appearance else "",
        "example_dialogue": example_dialogue.strip() if example_dialogue else "",
        "created": datetime.now().isoformat()
    }
    
    chat_histories[name] = []
    
    try:
        save_character_to_file(name)
    except Exception as e:
        del characters[name]
        del chat_histories[name]
        return f"❌ Failed to save character: {str(e)}", gr.Dropdown(), ""
    
    # Update character dropdown
    char_list = get_character_list()
    
    return (
        f"✅ Character '{name}' created successfully!",
        gr.Dropdown(choices=char_list, value=name),
        ""  # Clear name field
    )

def save_character_to_file(name):
    try:
        os.makedirs("characters", exist_ok=True)
        
        # Save character data
        char_file = f"characters/{name}.json"
        with open(char_file, 'w', encoding='utf-8') as f:
            json.dump(characters[name], f, indent=2, ensure_ascii=False)
        
        # Save chat history
        history_file = f"characters/{name}_history.json"
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(chat_histories.get(name, []), f, indent=2, ensure_ascii=False)
    except IOError as e:
        raise Exception(f"File system error: {str(e)}")

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
    if not name or name not in characters:
        return "❌ Please select a character to delete", gr.Dropdown()
    
    try:
        del characters[name]
        if name in chat_histories:
            del chat_histories[name]
        
        char_file = f"characters/{name}.json"
        if os.path.exists(char_file):
            os.remove(char_file)
        
        history_file = f"characters/{name}_history.json"
        if os.path.exists(history_file):
            os.remove(history_file)
        
        char_list = get_character_list()
        new_selection = char_list[0] if char_list else None
        
        return (
            f"✅ Character '{name}' deleted successfully",
            gr.Dropdown(choices=char_list, value=new_selection)
        )
    except Exception as e:
        return f"❌ Error deleting character: {str(e)}", gr.Dropdown()

def get_character_list():
    return sorted(characters.keys()) if characters else []

def get_character_info(name):
    if not name or name not in characters:
        return "Select a character to view details"
    
    char = characters[name]
    info = f"**{char['name']}**\n\n"
    info += f"**Personality:** {char['personality']}\n\n"
    
    if char.get('backstory'):
        info += f"**Backstory:** {char['backstory']}\n\n"
    
    if char.get('appearance'):
        info += f"**Appearance:** {char['appearance']}\n\n"
    
    if char.get('example_dialogue'):
        info += f"**Example Dialogue:**\n{char['example_dialogue']}\n\n"
    
    info += f"*Created: {char.get('created', 'Unknown')}*"
    
    return info

# ============ CHAT FUNCTIONS ============

def build_prompt(character_name, user_message):
    if character_name not in characters:
        return None
    
    char = characters[character_name]
    
    prompt = f"""You are roleplaying as {char['name']}. This is fictional creative writing.

CRITICAL: Stay in character. Respond naturally as {char['name']} would in 1-3 paragraphs.

Character:
- Name: {char['name']}
- Personality: {char['personality']}"""
    
    if char.get('backstory'):
        prompt += f"\n- Backstory: {char['backstory']}"
    
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
        return history + [(user_message, "❌ No AI backend detected. Check Setup tab.")], ""
    
    if not character_name or character_name not in characters:
        return history + [(user_message, "❌ Please select a character first.")], ""
    
    if not user_message or not user_message.strip():
        return history, ""
    
    user_message = user_message.strip()
    
    # Check if model exists
    if model not in available_models and model != "No models":
        return history + [(user_message, f"❌ Model '{model}' not available. Refresh models in Setup tab.")], ""
    
    prompt = build_prompt(character_name, user_message)
    
    try:
        client = LocalLLMClient(active_llm)
        ai_response = client.generate(prompt, model, temperature, max_tokens).strip()
        
        # Save to history (with limit)
        if character_name not in chat_histories:
            chat_histories[character_name] = []
        
        chat_histories[character_name].append((user_message, ai_response))
        
        # Limit history size
        MAX_HISTORY = 100
        if len(chat_histories[character_name]) > MAX_HISTORY:
            chat_histories[character_name] = chat_histories[character_name][-MAX_HISTORY:]
        
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
    
    status = "# 🔍 Backend Status\n\n"
    
    if llm_backends:
        status += "## ✅ LLM Active\n\n"
        for key, name in llm_backends:
            if key == 'ollama':
                models = BackendDetector.get_ollama_models()
                if models:
                    status += f"- **{name}**: {len(models)} models available\n"
                    if not active_llm:
                        active_llm = key
                        available_models = models
    else:
        status += "## ❌ No LLM Detected\n\nPlease install [Ollama](https://ollama.ai) and run:\n```\nollama pull llama3.2\n```\n"
    
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
                        f"✅ Found {len(models)} models"
                    )
    
    return (
        gr.Dropdown(choices=["No models"], value="No models"),
        gr.Dropdown(choices=["No models"], value="No models"),
        "❌ No backends detected"
    )

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
        <p style="color: #a0a0a0; margin: 5px 0 0 0;">v{VERSION} · AI Character Sandbox · Self-hosted & Private</p>
    </div>
    """)
    
    gr.Markdown("""
    <div style="text-align: center; color: #a0a0a0; margin: 10px 0; padding: 10px; background: #242424; border-radius: 8px;">
        ⚠️ <strong>18+ Only</strong> · Local AI · You control everything
    </div>
    """)
    
    with gr.Tabs():
        # Chat tab
        with gr.Tab("💬 Chat"):
            with gr.Row():
                with gr.Column(scale=1, min_width=250):
                    gr.Markdown("### Character")
                    
                    character_select = gr.Dropdown(
                        choices=get_character_list(),
                        value=get_character_list()[0] if get_character_list() else None,
                        label="Select Character",
                        interactive=True
                    )
                    
                    character_info_display = gr.Markdown(
                        get_character_info(get_character_list()[0] if get_character_list() else None)
                    )
                    
                    gr.Markdown("---")
                    gr.Markdown("### AI Settings")
                    
                    model_select = gr.Dropdown(
                        choices=available_models if available_models else ["No models"],
                        value=available_models[0] if available_models else "No models",
                        label="Model"
                    )
                    
                    temperature = gr.Slider(0.1, 2.0, 0.9, step=0.1, label="Creativity")
                    max_tokens = gr.Slider(50, 500, 200, step=50, label="Response Length")
                    
                    gr.Markdown("---")
                    
                    clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary", size="sm")
                
                with gr.Column(scale=3):
                    chatbot = gr.Chatbot(
                        label="Conversation",
                        value=[],
                        height=600,
                        type="tuples"
                    )
                    
                    with gr.Row():
                        msg_input = gr.Textbox(
                            placeholder="Type your message...",
                            show_label=False,
                            scale=4,
                            lines=2
                        )
                        send_btn = gr.Button("Send ➤", variant="primary", scale=1)
            
            # Character selection handler
            character_select.change(
                fn=lambda name: (get_character_info(name), load_chat_history(name)),
                inputs=[character_select],
                outputs=[character_info_display, chatbot]
            )
            
            # Chat handlers
            msg_input.submit(
                chat_with_character,
                [character_select, msg_input, chatbot, model_select, temperature, max_tokens],
                [chatbot, msg_input]
            )
            
            send_btn.click(
                chat_with_character,
                [character_select, msg_input, chatbot, model_select, temperature, max_tokens],
                [chatbot, msg_input]
            )
            
            clear_btn.click(
                lambda name: clear_chat(name),
                [character_select],
                [chatbot]
            )
        
        # Create Character tab
        with gr.Tab("➕ Create Character"):
            gr.Markdown("### Create a New Character")
            
            with gr.Column():
                char_name = gr.Textbox(
                    label="Name",
                    placeholder="e.g., Sarah",
                    max_lines=1
                )
                char_personality = gr.Textbox(
                    label="Personality (Required)",
                    placeholder="e.g., Witty software engineer who loves coffee and late-night coding",
                    lines=3
                )
                char_backstory = gr.Textbox(
                    label="Backstory (Optional)",
                    placeholder="e.g., Former game developer, now works on AI research...",
                    lines=5
                )
                char_appearance = gr.Textbox(
                    label="Appearance (Optional)",
                    placeholder="e.g., Mid-30s, brown hair, green eyes, casual dresser",
                    lines=2
                )
                char_example = gr.Textbox(
                    label="Example Dialogue (Optional)",
                    placeholder="User: Hi!\nSarah: Hey there! Ready to build something cool?",
                    lines=3
                )
                
                create_btn = gr.Button("✨ Create Character", variant="primary", size="lg")
                create_output = gr.Textbox(label="Status", interactive=False)
            
            create_btn.click(
                create_character,
                [char_name, char_personality, char_backstory, char_appearance, char_example],
                [create_output, character_select, char_name]
            )
        
        # Manage Characters tab
        with gr.Tab("📋 Manage Characters"):
            gr.Markdown("### Manage Your Characters")
            
            with gr.Column():
                manage_character_select = gr.Dropdown(
                    choices=get_character_list(),
                    value=get_character_list()[0] if get_character_list() else None,
                    label="Select Character to Manage"
                )
                
                manage_character_info = gr.Markdown(
                    get_character_info(get_character_list()[0] if get_character_list() else None)
                )
                
                gr.Markdown("---")
                
                delete_btn = gr.Button("❌ Delete This Character", variant="stop", size="lg")
                delete_output = gr.Textbox(label="Status", interactive=False)
            
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
        
        # Setup tab
        with gr.Tab("⚙️ Setup"):
            gr.Markdown("### System Configuration")
            
            check_btn = gr.Button("🔍 Check AI Backends", variant="primary", size="lg")
            status_display = gr.Markdown()
            
            gr.Markdown("---")
            gr.Markdown("### Model Management")
            
            with gr.Row():
                model_dropdown_global = gr.Dropdown(
                    choices=available_models if available_models else ["No models"],
                    value=available_models[0] if available_models else "No models",
                    label="Available Models",
                    scale=3
                )
                
                refresh_models_btn = gr.Button("🔄 Refresh", variant="primary", size="lg", scale=1)
            
            refresh_status = gr.Textbox(label="Status", interactive=False)
            
            gr.Markdown("""
            ---
            
            ### Quick Start Guide
            
            1. **Install Ollama**: Visit [ollama.ai](https://ollama.ai) and download
            2. **Download a model**: Open terminal and run:
               ```bash
               ollama pull llama3.2
               ```
            3. **Verify**: Click "Check AI Backends" above
            4. **Create**: Go to "Create Character" tab
            5. **Chat**: Select your character in the "Chat" tab
            
            ### Tips & Tricks
            
            - **Model size matters**: Larger models give better responses
              - `llama3.2:1b` - Fast but basic (1GB)
              - `llama3.2` - Balanced (3GB) ⭐ Recommended
              - `llama3.1:8b` - High quality (8GB)
            
            - **Creativity slider**: 
              - Low (0.3-0.5) = Consistent, predictable
              - Medium (0.7-0.9) = Balanced ⭐ Default
              - High (1.2+) = Creative, unpredictable
            
            - **All data is local**: Characters saved in `./characters/` folder
            
            - **Backup**: Just copy the `characters` folder!
            
            ### Troubleshooting
            
            **"No AI backend detected"**
            - Make sure Ollama is installed and running
            - Try: `ollama serve` in terminal
            
            **"Model not available"**
            - Pull a model: `ollama pull llama3.2`
            - Click "Refresh" button above
            
            **"AI timeout"**
            - Model may be too large for your hardware
            - Try a smaller model like `llama3.2:1b`
            
            ### Security Note
            
            ✅ This version binds to **localhost only** (127.0.0.1)
            - Only accessible from your computer
            - No network exposure
            - All data stays on your machine
            
            If you need network access, edit the code and change:
            ```python
            server_name="127.0.0.1"  # Change to "0.0.0.0"
            ```
            """)
            
            check_btn.click(check_backends, None, status_display)
            
            refresh_models_btn.click(
                refresh_models,
                None,
                [model_select, model_dropdown_global, refresh_status]
            )

if __name__ == "__main__":
    print("=" * 60)
    print(f"🎭 {APP_NAME} v{VERSION}")
    print("=" * 60)
    print("📂 Characters: ./characters/")
    print("🔒 Security: Localhost only (127.0.0.1)")
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
                    print(f"✅ Models: {', '.join(models[:5])}")
                    if len(models) > 5:
                        print(f"   ... and {len(models)-5} more")
    else:
        print("⚠️  No LLM detected - Install Ollama from https://ollama.ai")
    
    print("\n🌐 Starting web interface...")
    print("=" * 60)
    
    app.launch(
        server_name="127.0.0.1",  # FIXED: localhost only for security
        server_port=7861,
        share=False
    )