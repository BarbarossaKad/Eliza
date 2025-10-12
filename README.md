# 🎭 ELIZA - AI Character Sandbox

**Version 0.4.1** - A self-hosted AI character creation and roleplay chat system

Named in honor of [ELIZA (1966)](https://en.wikipedia.org/wiki/ELIZA), the first chatbot, and the psychological phenomenon known as the “ELIZA effect” - where people attribute human-like feelings to computer programs.

**Repository:** https://github.com/BarbarossaKad/Eliza

-----

## 🚨 Why ELIZA? Privacy Matters.

Recent data breaches at major AI platforms highlight why self-hosting matters. With ELIZA, your conversations never leave your computer. No cloud. No leaks. Just you and your AI.

-----

## 🆚 Why Choose ELIZA?

|Feature     |ELIZA             |Character.AI      |Replika           |
|------------|------------------|------------------|------------------|
|Privacy     |✅ 100% local      |❌ Cloud-based     |❌ Cloud-based     |
|Data leaks  |✅ Impossible      |⚠️ Risk            |⚠️ Risk            |
|Cost        |✅ Free forever    |⚠️ Freemium        |❌ $70/year        |
|Censorship  |✅ None            |❌ Filtered        |❌ Filtered        |
|Offline mode|✅ Yes             |❌ No              |❌ No              |
|Open source |✅ Yes             |❌ No              |❌ No              |
|Your data   |✅ Stays on YOUR PC|❌ On their servers|❌ On their servers|

-----

- **Character Creation** - Design unique AI characters with personalities, backstories, and conversation styles
- **Natural Conversations** - Chat with your characters using local LLM models
- **Character Management** - Edit, update, and delete characters as needed
- **Multiple Characters** - Switch between different characters with dedicated chat tabs
- **Self-Hosted** - 100% private, runs entirely on your local machine
- **Multi-Backend Support** - Works with Ollama, LM Studio, or Text Generation WebUI
- **Network Access** - Use from any device on your local network (PC, phone, tablet)
- **Persistent Storage** - All characters and conversations saved locally

-----

## 📸 Screenshots

*(Add your screenshots here when ready)*

-----

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **Local LLM Backend** - One of:
  - [Ollama](https://ollama.ai) (Recommended - easiest)
  - [LM Studio](https://lmstudio.ai)
  - [Text Generation WebUI](https://github.com/oobabooga/text-generation-webui)

### Installation

1. **Clone the repository:**
   
   ```bash
   git clone https://github.com/BarbarossaKad/Eliza.git
   cd Eliza
   ```
1. **Install dependencies:**
   
   ```bash
   pip install gradio requests pillow
   ```
1. **Install and configure Ollama** (recommended):
   
   ```bash
   # Install from https://ollama.ai
   # Then pull a model:
   ollama pull mistral  # Recommended for roleplay
   # or
   ollama pull llama3.2  # Good alternative
   ```
1. **Run ELIZA:**
   
   ```bash
   python Eliza_v0.4.1.py
   ```
1. **Open in browser:**
- On PC: http://localhost:7861
- On phone: http://your-pc-ip:7861

-----

## 📖 Usage Guide

### Creating Your First Character

1. **Go to “➕ New Character” tab**
1. **Fill in character details:**
- **Name:** Character’s name (e.g., “Sarah Chen”)
- **Personality:** Detailed traits and behaviors
- **Backstory:** Background and history
- **Appearance:** Physical description (optional)
- **Example Dialogue:** Sample conversation showing their style
1. **Click “✨ Create Character”**
1. **Refresh the page** - your character appears as a new tab!

### Chatting with Characters

1. **Click the character’s tab** (e.g., “👤 Sarah”)
1. **Select AI model** from dropdown
1. **Adjust settings:**
- **Creativity:** Higher = more creative responses
- **Length:** Max response length
1. **Type message and hit Enter** or click “Send”

### Editing Characters

1. **Go to “📋 Manage” tab**
1. **Select character** from dropdown
1. **Click “📖 Load Character”**
1. **Edit any fields**
1. **Click “💾 Save Changes”**
1. **Refresh page** to see updates in character tab

### Tips for Better Characters

**Good Personality Description:**

```
Witty software engineer in her late 20s. Sarcastic but warm. 
Loves coffee and terrible coding puns. Gets excited about new tech. 
Sometimes overthinks everything. Dry sense of humor.
```

**Good Example Dialogue:**

```
User: How's your day going?
Sarah: Pretty good! Just had my third coffee and I'm only slightly 
vibrating. Fixed a bug that's been haunting me for two days - turns 
out I just needed to actually read the error message. Revolutionary 
concept, I know.

User: Hah! I do that all the time.
Sarah: Right?! Sometimes I think half of programming is just 
remembering to read what the computer is literally telling you.
```

-----

## ⚙️ Configuration

### Accessing from Other Devices

**Default:** ELIZA is accessible from any device on your local network.

**To restrict to PC only:**
Edit `Eliza_v0.4.1.py`, find:

```python
server_name="0.0.0.0",
```

Change to:

```python
server_name="127.0.0.1",
```

### Recommended AI Models

|Model      |Size|Speed    |Quality  |Best For          |
|-----------|----|---------|---------|------------------|
|mistral    |7B  |Medium   |Excellent|Roleplay ⭐        |
|llama3.1:8b|8B  |Slower   |Best     |Deep conversations|
|llama3.2   |3B  |Fast     |Good     |Quick responses   |
|llama3.2:1b|1B  |Very Fast|Basic    |Testing only      |

**Install via Ollama:**

```bash
ollama pull mistral
```

### Performance Tips

- **Use larger models** (7B+) for better roleplay
- **Increase creativity slider** (0.9-1.2) for more natural responses
- **Write detailed example dialogue** - the AI learns from it
- **GPU highly recommended** - CPU mode is slow

-----

## 🗂️ File Structure

```
eliza/
├── Eliza_v0.3.py           # Main application
├── characters/             # Character data (auto-created)
│   ├── CharacterName.json        # Character definition
│   └── CharacterName_history.json # Chat history
└── README.md
```

-----

## 🔒 Privacy & Security

### What ELIZA Does:

✅ Runs 100% locally on your computer  
✅ No data sent to external servers  
✅ No telemetry or tracking  
✅ All conversations stay on your PC  
✅ Open source - inspect the code yourself

### What ELIZA Does NOT Do:

❌ No cloud storage  
❌ No external API calls (except to your local LLM)  
❌ No analytics  
❌ No data collection

### Network Security:

- By default, accessible on local network only
- Not exposed to internet unless you port-forward
- Close the app when not in use to close ports
- Use `server_name="127.0.0.1"` for PC-only access

-----

## ⚠️ Important Notes

### Age Restriction

**18+ Only** - This tool is designed for adult users. You are responsible for all content created.

### Content Responsibility

- **You control all AI models** - ELIZA does not include any AI models
- **You are responsible** for all generated content
- **Use appropriate models** for your use case
- **Configure content filters** as needed for your situation

### Legal Disclaimer

This software is a tool/platform. All AI models and generated content are provided and controlled by the user. The developers are not responsible for how this tool is used or what content is generated.

-----

## 🛠️ Troubleshooting

### “No LLM backend detected”

**Solution:** Install and start Ollama, then click “🔄 Refresh & Update All Dropdowns” in Setup tab.

### Character not appearing after creation

**Solution:** Refresh the browser page (F5) to see the new character tab.

### Slow responses (30+ seconds)

**Solutions:**

- Use a smaller model (`llama3.2` instead of `llama3.1:8b`)
- Ensure you have a GPU (CPU mode is very slow)
- Reduce “Response Length” slider
- Check Task Manager - make sure Ollama is using GPU

### Character keeps saying “How can I help?”

**Solutions:**

- Use larger model (mistral 7B or llama3.1:8b)
- Add detailed example dialogue showing natural conversation
- Increase creativity slider to 1.0+
- Avoid assistant-like personality descriptions

### Model dropdown empty

**Solution:**

1. Make sure Ollama is running (`ollama list` in terminal)
1. Go to Setup tab
1. Click “🔄 Refresh & Update All Dropdowns”

-----

## 🚧 Roadmap

### v0.4 (Planned)

- [ ] Image generation integration (ComfyUI/A1111)
- [ ] Character portrait auto-generation
- [ ] Voice input/output (TTS/STT)
- [ ] Better conversation memory

### v0.5 (Future)

- [ ] Multi-character conversations
- [ ] Character sharing/import system
- [ ] Advanced prompt engineering tools
- [ ] Mobile app version

### v1.0 (Long-term)

- [ ] Steam Workshop integration
- [ ] Native desktop app (Godot)
- [ ] Cloud sync (optional)
- [ ] Plugin system

-----

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
1. Create a feature branch
1. Make your changes
1. Submit a pull request

**Areas needing help:**

- Better UI/UX design
- Additional LLM backend support
- Documentation improvements
- Bug fixes

-----

## 📜 License

[Choose your license - MIT, GPL, etc.]

This project is provided as-is with no warranties. Use at your own risk.

-----

## 🙏 Credits

**Inspired by:**

- ELIZA (1966) by Joseph Weizenbaum
- Character.AI
- Tavern AI / SillyTavern

**Built with:**

- [Gradio](https://gradio.app) - Web UI framework
- [Ollama](https://ollama.ai) - Local LLM runtime
- Python 3.10+

**Special thanks to:**

- The open-source AI community
- Everyone building and sharing local AI tools

-----

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/BarbarossaKad/Eliza/issues)
- **Discussions:** [GitHub Discussions](https://github.com/BarbarossaKad/Eliza/discussions)
- **Reddit:** r/LocalLLaMA (for general AI help)

-----

## ⚖️ Disclaimer

**ELIZA is a tool for creative writing and entertainment purposes.**

- Not intended for therapy, counseling, or medical advice
- AI-generated content may be inaccurate or inappropriate
- Users must be 18+ or legal age in their jurisdiction
- You are responsible for compliance with local laws
- No warranty or guarantee of any kind is provided

**The ELIZA effect is real** - remember you’re chatting with an AI, not a person.

-----

**Version:** 0.4.1  
**Last Updated:** October 2025  
**Requires:** Python 3.10+, Ollama (or compatible LLM backend)

-----

Made with ❤️ for the local AI community

**[⭐ Star on GitHub](https://github.com/BarbarossaKad/Eliza)** if you find this useful!i
