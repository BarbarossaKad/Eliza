import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, MoreVertical, Trash2, Settings, User, Brain, Plus, List, Activity, X } from 'lucide-react';

export default function ELIZAChatInterface() {
  const [messages, setMessages] = useState([
    { id: 1, text: "Hello! I'm your AI assistant. How can I help you today?", isBot: true, time: new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' }) }
  ]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showMemory, setShowMemory] = useState(false);
  const [showMenu, setShowMenu] = useState(false);
  const [showCharacterManager, setShowCharacterManager] = useState(false);
  const [showBackendStatus, setShowBackendStatus] = useState(false);
  
  // Settings
  const [ollamaUrl, setOllamaUrl] = useState('http://localhost:11434');
  const [model, setModel] = useState('llama2');
  const [temperature, setTemperature] = useState(0.9);
  const [maxTokens, setMaxTokens] = useState(200);
  
  // Character and memory
  const [characterName, setCharacterName] = useState('AI Assistant');
  const [characterPersonality, setCharacterPersonality] = useState('Helpful, friendly, and knowledgeable assistant');
  const [conversationHistory, setConversationHistory] = useState([]);
  const [memories, setMemories] = useState([]);
  
  // Character management
  const [characters, setCharacters] = useState({
    'AI Assistant': {
      name: 'AI Assistant',
      personality: 'Helpful, friendly, and knowledgeable assistant',
      backstory: '',
      avatar: '🤖'
    }
  });
  const [newCharName, setNewCharName] = useState('');
  const [newCharPersonality, setNewCharPersonality] = useState('');
  const [newCharBackstory, setNewCharBackstory] = useState('');
  const [newCharAvatar, setNewCharAvatar] = useState('👤');
  
  // Backend status
  const [backendStatus, setBackendStatus] = useState('Checking...');
  const [availableModels, setAvailableModels] = useState([]);
  
  const chatEndRef = useRef(null);
  
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const extractMemories = (userMessage, botResponse) => {
    const userLower = userMessage.toLowerCase();
    const newMemories = [];
    
    // Name extraction
    const nameMatch = userLower.match(/my name is (\w+)/);
    if (nameMatch) {
      newMemories.push(`User's name is ${nameMatch[1]}`);
    }
    
    // Preferences
    const likeMatch = userLower.match(/i (?:like|love|enjoy) ([\w\s]+)/);
    if (likeMatch) {
      newMemories.push(`User likes ${likeMatch[1]}`);
    }
    
    const dislikeMatch = userLower.match(/i (?:hate|dislike|don't like) ([\w\s]+)/);
    if (dislikeMatch) {
      newMemories.push(`User dislikes ${dislikeMatch[1]}`);
    }
    
    // Identity
    const identityMatch = userLower.match(/i(?:'m| am) (?:a |an )?([\w\s]+)/);
    if (identityMatch && !userLower.includes('i am here') && !userLower.includes('i am good')) {
      newMemories.push(`User is ${identityMatch[1]}`);
    }
    
    if (newMemories.length > 0) {
      setMemories(prev => {
        const updated = [...prev, ...newMemories.map(m => ({
          text: m,
          timestamp: new Date().toISOString()
        }))];
        return updated.slice(-20); // Keep last 20 memories
      });
    }
  };

  const buildPrompt = (userMessage) => {
    let prompt = `You are ${characterName}. ${characterPersonality}\n\n`;
    
    // Add memories
    if (memories.length > 0) {
      prompt += "What you know about the user:\n";
      memories.slice(-5).forEach(m => {
        prompt += `- ${m.text}\n`;
      });
      prompt += "\n";
    }
    
    // Add recent conversation
    if (conversationHistory.length > 0) {
      prompt += "Recent conversation:\n";
      conversationHistory.slice(-5).forEach(([user, bot]) => {
        prompt += `User: ${user}\n${characterName}: ${bot}\n`;
      });
      prompt += "\n";
    }
    
    prompt += `User: ${userMessage}\n${characterName}:`;
    return prompt;
  };

  const callOllama = async (prompt) => {
    try {
      const response = await fetch(`${ollamaUrl}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: model,
          prompt: prompt,
          stream: false,
          options: {
            temperature: temperature,
            num_predict: maxTokens
          }
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data.response.trim();
    } catch (error) {
      console.error('Ollama error:', error);
      throw new Error(
        error.message.includes('Failed to fetch') 
          ? "Can't connect to Ollama. Make sure it's running on " + ollamaUrl
          : `Ollama error: ${error.message}`
      );
    }
  };

  const handleSend = async () => {
    if (!inputText.trim() || isTyping) return;
    
    const userMessage = inputText.trim();
    const userMsg = {
      id: messages.length + 1,
      text: userMessage,
      isBot: false,
      time: new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })
    };
    
    setMessages(prev => [...prev, userMsg]);
    setInputText('');
    setIsTyping(true);

    try {
      const prompt = buildPrompt(userMessage);
      const botResponseText = await callOllama(prompt);
      
      const botMsg = {
        id: messages.length + 2,
        text: botResponseText,
        isBot: true,
        time: new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })
      };
      
      setMessages(prev => [...prev, botMsg]);
      setConversationHistory(prev => [...prev, [userMessage, botResponseText]].slice(-10));
      
      // Extract memories
      extractMemories(userMessage, botResponseText);
      
    } catch (error) {
      const errorMsg = {
        id: messages.length + 2,
        text: `❌ ${error.message}`,
        isBot: true,
        time: new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const clearChat = () => {
    setMessages([
      { id: 1, text: "Hello! I'm your AI assistant. How can I help you today?", isBot: true, time: new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' }) }
    ]);
    setConversationHistory([]);
  };

  const clearMemories = () => {
    setMemories([]);
  };

  const checkBackend = async () => {
    setBackendStatus('Checking...');
    try {
      const response = await fetch(`${ollamaUrl}/api/tags`, { timeout: 2000 });
      if (response.ok) {
        const data = await response.json();
        setAvailableModels(data.models.map(m => m.name));
        setBackendStatus(`✅ Connected - ${data.models.length} models found`);
      } else {
        setBackendStatus('❌ Ollama not responding');
      }
    } catch (error) {
      setBackendStatus('❌ Cannot connect to Ollama');
      setAvailableModels([]);
    }
  };

  const createCharacter = () => {
    if (!newCharName.trim()) {
      alert('Please enter a character name');
      return;
    }
    
    const char = {
      name: newCharName.trim(),
      personality: newCharPersonality.trim() || 'Friendly assistant',
      backstory: newCharBackstory.trim(),
      avatar: newCharAvatar
    };
    
    setCharacters(prev => ({...prev, [char.name]: char}));
    setCharacterName(char.name);
    setCharacterPersonality(char.personality);
    
    // Clear form
    setNewCharName('');
    setNewCharPersonality('');
    setNewCharBackstory('');
    setNewCharAvatar('👤');
    
    alert(`✅ Character "${char.name}" created!`);
  };

  const deleteCharacter = (name) => {
    if (name === 'AI Assistant') {
      alert('Cannot delete the default character');
      return;
    }
    
    if (confirm(`Delete character "${name}"?`)) {
      const newChars = {...characters};
      delete newChars[name];
      setCharacters(newChars);
      
      if (characterName === name) {
        setCharacterName('AI Assistant');
        setCharacterPersonality(characters['AI Assistant'].personality);
      }
    }
  };

  const switchCharacter = (name) => {
    const char = characters[name];
    setCharacterName(char.name);
    setCharacterPersonality(char.personality);
    setShowMenu(false);
    clearChat();
  };

  const closeAllPanels = () => {
    setShowSettings(false);
    setShowMemory(false);
    setShowCharacterManager(false);
    setShowBackendStatus(false);
    setShowMenu(false);
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-900 p-4">
      <div className="w-full max-w-4xl h-[700px] bg-gray-800 rounded-3xl shadow-2xl overflow-hidden flex">
        
        {/* Sidebar */}
        <div className={`${showSettings || showMemory || showCharacterManager || showBackendStatus ? 'w-80' : 'w-0'} bg-gray-900 border-r border-gray-700 overflow-y-auto transition-all duration-300`}>
          {showSettings && (
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                  <Settings size={20} className="text-blue-400" />
                  Settings
                </h3>
                <button onClick={closeAllPanels} className="text-gray-400 hover:text-white">
                  <X size={20} />
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Character Name</label>
                  <input
                    type="text"
                    value={characterName}
                    onChange={(e) => setCharacterName(e.target.value)}
                    className="w-full bg-gray-800 text-white rounded-lg px-3 py-2 text-sm border border-gray-700 focus:border-blue-500 focus:outline-none"
                  />
                </div>
                
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Personality</label>
                  <textarea
                    value={characterPersonality}
                    onChange={(e) => setCharacterPersonality(e.target.value)}
                    rows={3}
                    className="w-full bg-gray-800 text-white rounded-lg px-3 py-2 text-sm border border-gray-700 focus:border-blue-500 focus:outline-none"
                  />
                </div>
                
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Ollama URL</label>
                  <input
                    type="text"
                    value={ollamaUrl}
                    onChange={(e) => setOllamaUrl(e.target.value)}
                    className="w-full bg-gray-800 text-white rounded-lg px-3 py-2 text-sm border border-gray-700 focus:border-blue-500 focus:outline-none"
                  />
                </div>
                
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Model</label>
                  <input
                    type="text"
                    value={model}
                    onChange={(e) => setModel(e.target.value)}
                    placeholder="llama2, mistral, etc."
                    className="w-full bg-gray-800 text-white rounded-lg px-3 py-2 text-sm border border-gray-700 focus:border-blue-500 focus:outline-none"
                  />
                </div>
                
                <div>
                  <label className="block text-sm text-gray-400 mb-1">
                    Temperature: {temperature}
                  </label>
                  <input
                    type="range"
                    min="0.1"
                    max="2.0"
                    step="0.1"
                    value={temperature}
                    onChange={(e) => setTemperature(parseFloat(e.target.value))}
                    className="w-full"
                  />
                </div>
                
                <div>
                  <label className="block text-sm text-gray-400 mb-1">
                    Max Tokens: {maxTokens}
                  </label>
                  <input
                    type="range"
                    min="50"
                    max="500"
                    step="50"
                    value={maxTokens}
                    onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                    className="w-full"
                  />
                </div>
              </div>
            </div>
          )}
          
          {showMemory && (
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                  <Brain size={20} className="text-purple-400" />
                  Memory Bank
                </h3>
                <div className="flex gap-2">
                  <button
                    onClick={clearMemories}
                    className="text-xs px-2 py-1 bg-red-600 hover:bg-red-700 rounded text-white"
                  >
                    Clear
                  </button>
                  <button onClick={closeAllPanels} className="text-gray-400 hover:text-white">
                    <X size={16} />
                  </button>
                </div>
              </div>
              
              {memories.length === 0 ? (
                <p className="text-gray-500 text-sm">No memories yet. Chat to build memories!</p>
              ) : (
                <div className="space-y-2">
                  {memories.map((memory, idx) => (
                    <div key={idx} className="bg-gray-800 rounded-lg p-3 border border-gray-700">
                      <p className="text-sm text-gray-200">{memory.text}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        {new Date(memory.timestamp).toLocaleString()}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
          
          {showCharacterManager && (
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                  <User size={20} className="text-green-400" />
                  Characters
                </h3>
                <button onClick={closeAllPanels} className="text-gray-400 hover:text-white">
                  <X size={20} />
                </button>
              </div>
              
              <div className="mb-6">
                <h4 className="text-sm font-semibold text-gray-400 mb-2">Active Characters</h4>
                <div className="space-y-2">
                  {Object.values(characters).map(char => (
                    <div key={char.name} className="bg-gray-800 rounded-lg p-3 border border-gray-700 flex items-center justify-between">
                      <button 
                        onClick={() => switchCharacter(char.name)}
                        className="flex items-center gap-3 flex-1 text-left"
                      >
                        <div className="text-2xl">{char.avatar}</div>
                        <div>
                          <div className={`font-semibold ${characterName === char.name ? 'text-blue-400' : 'text-white'}`}>
                            {char.name}
                          </div>
                          <div className="text-xs text-gray-400 line-clamp-1">{char.personality}</div>
                        </div>
                      </button>
                      {char.name !== 'AI Assistant' && (
                        <button
                          onClick={() => deleteCharacter(char.name)}
                          className="text-red-400 hover:text-red-300 ml-2"
                        >
                          <Trash2 size={16} />
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="border-t border-gray-700 pt-4">
                <h4 className="text-sm font-semibold text-gray-400 mb-3">Create New Character</h4>
                <div className="space-y-3">
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">Avatar (emoji)</label>
                    <input
                      type="text"
                      value={newCharAvatar}
                      onChange={(e) => setNewCharAvatar(e.target.value.slice(0, 2))}
                      placeholder="👤"
                      className="w-full bg-gray-800 text-white rounded-lg px-3 py-2 text-sm border border-gray-700 focus:border-blue-500 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">Name *</label>
                    <input
                      type="text"
                      value={newCharName}
                      onChange={(e) => setNewCharName(e.target.value)}
                      placeholder="e.g., Detective Nova"
                      className="w-full bg-gray-800 text-white rounded-lg px-3 py-2 text-sm border border-gray-700 focus:border-blue-500 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">Personality *</label>
                    <textarea
                      value={newCharPersonality}
                      onChange={(e) => setNewCharPersonality(e.target.value)}
                      placeholder="e.g., Mysterious detective with sharp wit"
                      rows={2}
                      className="w-full bg-gray-800 text-white rounded-lg px-3 py-2 text-sm border border-gray-700 focus:border-blue-500 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">Backstory</label>
                    <textarea
                      value={newCharBackstory}
                      onChange={(e) => setNewCharBackstory(e.target.value)}
                      placeholder="Optional background story..."
                      rows={2}
                      className="w-full bg-gray-800 text-white rounded-lg px-3 py-2 text-sm border border-gray-700 focus:border-blue-500 focus:outline-none"
                    />
                  </div>
                  <button
                    onClick={createCharacter}
                    className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-lg px-4 py-2 text-sm font-semibold flex items-center justify-center gap-2"
                  >
                    <Plus size={16} />
                    Create Character
                  </button>
                </div>
              </div>
            </div>
          )}
          
          {showBackendStatus && (
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                  <Activity size={20} className="text-yellow-400" />
                  Backend Status
                </h3>
                <button onClick={closeAllPanels} className="text-gray-400 hover:text-white">
                  <X size={20} />
                </button>
              </div>
              
              <div className="space-y-4">
                <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm text-gray-400">Ollama Status</span>
                    <button
                      onClick={checkBackend}
                      className="text-xs px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-white"
                    >
                      Refresh
                    </button>
                  </div>
                  <p className="text-sm text-white">{backendStatus}</p>
                  <p className="text-xs text-gray-500 mt-2">URL: {ollamaUrl}</p>
                </div>
                
                {availableModels.length > 0 && (
                  <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                    <h4 className="text-sm font-semibold text-gray-400 mb-2">Available Models</h4>
                    <div className="space-y-1">
                      {availableModels.map(m => (
                        <div 
                          key={m} 
                          className={`text-sm px-2 py-1 rounded ${m === model ? 'bg-blue-600 text-white' : 'text-gray-300'}`}
                        >
                          {m}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                  <h4 className="text-sm font-semibold text-gray-400 mb-2">Quick Start</h4>
                  <div className="text-xs text-gray-400 space-y-2">
                    <p>1. Install Ollama from <a href="https://ollama.ai" target="_blank" className="text-blue-400 underline">ollama.ai</a></p>
                    <p>2. Run: <code className="bg-gray-900 px-2 py-1 rounded">ollama pull llama2</code></p>
                    <p>3. Click Refresh to detect models</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <div className="bg-gray-900 text-white p-4 flex items-center justify-between border-b border-gray-700">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-2xl">
                {characters[characterName]?.avatar || '🤖'}
              </div>
              <div>
                <div className="font-semibold">{characterName}</div>
                <div className="text-xs text-green-400 flex items-center gap-1">
                  <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                  {isTyping ? 'Typing...' : 'Online'}
                </div>
              </div>
            </div>
            <div className="flex gap-2 relative">
              <button
                onClick={() => {
                  setShowMemory(!showMemory);
                  setShowSettings(false);
                  setShowCharacterManager(false);
                  setShowBackendStatus(false);
                  setShowMenu(false);
                }}
                className={`hover:bg-gray-700 rounded-full p-2 transition ${showMemory ? 'bg-gray-700' : ''}`}
                title="Memory Bank"
              >
                <Brain size={20} />
              </button>
              <button
                onClick={() => {
                  setShowSettings(!showSettings);
                  setShowMemory(false);
                  setShowCharacterManager(false);
                  setShowBackendStatus(false);
                  setShowMenu(false);
                }}
                className={`hover:bg-gray-700 rounded-full p-2 transition ${showSettings ? 'bg-gray-700' : ''}`}
                title="Settings"
              >
                <Settings size={20} />
              </button>
              <button
                onClick={clearChat}
                className="hover:bg-gray-700 rounded-full p-2 transition"
                title="Clear chat"
              >
                <Trash2 size={20} />
              </button>
              <button 
                onClick={() => setShowMenu(!showMenu)}
                className={`hover:bg-gray-700 rounded-full p-2 transition ${showMenu ? 'bg-gray-700' : ''}`}
                title="More options"
              >
                <MoreVertical size={20} />
              </button>
              
              {/* Dropdown Menu */}
              {showMenu && (
                <div className="absolute right-0 top-12 bg-gray-800 border border-gray-700 rounded-lg shadow-xl w-56 z-50">
                  <button
                    onClick={() => {
                      setShowCharacterManager(true);
                      setShowSettings(false);
                      setShowMemory(false);
                      setShowBackendStatus(false);
                      setShowMenu(false);
                    }}
                    className="w-full px-4 py-3 text-left hover:bg-gray-700 flex items-center gap-3 text-white border-b border-gray-700"
                  >
                    <User size={18} className="text-green-400" />
                    <span>Manage Characters</span>
                  </button>
                  <button
                    onClick={() => {
                      setShowBackendStatus(true);
                      setShowSettings(false);
                      setShowMemory(false);
                      setShowCharacterManager(false);
                      setShowMenu(false);
                      checkBackend();
                    }}
                    className="w-full px-4 py-3 text-left hover:bg-gray-700 flex items-center gap-3 text-white border-b border-gray-700"
                  >
                    <Activity size={18} className="text-yellow-400" />
                    <span>Backend Status</span>
                  </button>
                  <button
                    onClick={() => {
                      if (confirm('Clear all chat history?')) {
                        clearChat();
                      }
                      setShowMenu(false);
                    }}
                    className="w-full px-4 py-3 text-left hover:bg-gray-700 flex items-center gap-3 text-white border-b border-gray-700"
                  >
                    <Trash2 size={18} className="text-red-400" />
                    <span>Clear History</span>
                  </button>
                  <button
                    onClick={() => {
                      if (confirm('Reset all memories?')) {
                        clearMemories();
                      }
                      setShowMenu(false);
                    }}
                    className="w-full px-4 py-3 text-left hover:bg-gray-700 flex items-center gap-3 text-white"
                  >
                    <Brain size={18} className="text-purple-400" />
                    <span>Reset Memories</span>
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-800">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.isBot ? 'justify-start' : 'justify-end'}`}
              >
                <div className={`max-w-[80%] ${message.isBot ? 'order-1' : 'order-2'}`}>
                  {message.isBot && (
                    <div className="flex items-center gap-2 mb-1 px-2">
                      <Bot size={14} className="text-blue-400" />
                      <span className="text-xs text-gray-400">{characterName}</span>
                    </div>
                  )}
                  <div
                    className={`rounded-2xl px-4 py-2 ${
                      message.isBot
                        ? 'bg-gradient-to-br from-blue-600 to-purple-600 text-white rounded-tl-md'
                        : 'bg-gray-700 text-gray-100 rounded-br-md'
                    }`}
                  >
                    <p className="text-sm break-words whitespace-pre-wrap">{message.text}</p>
                  </div>
                  <div
                    className={`text-xs text-gray-500 mt-1 px-2 ${
                      message.isBot ? 'text-left' : 'text-right'
                    }`}
                  >
                    {message.time}
                  </div>
                </div>
              </div>
            ))}
            
            {/* Typing indicator */}
            {isTyping && (
              <div className="flex justify-start">
                <div className="max-w-[80%]">
                  <div className="flex items-center gap-2 mb-1 px-2">
                    <Bot size={14} className="text-blue-400" />
                    <span className="text-xs text-gray-400">{characterName}</span>
                  </div>
                  <div className="bg-gradient-to-br from-blue-600 to-purple-600 text-white rounded-2xl rounded-tl-md px-4 py-3">
                    <div className="flex gap-1">
                      <span className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                      <span className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                      <span className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Input */}
          <div className="bg-gray-900 border-t border-gray-700 p-3 flex items-center gap-2">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Message AI Assistant..."
              className="flex-1 bg-gray-700 text-white placeholder-gray-400 rounded-full px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isTyping}
            />
            <button
              onClick={handleSend}
              disabled={isTyping || !inputText.trim()}
              className={`rounded-full p-2 transition ${
                inputText.trim() && !isTyping
                  ? 'bg-gradient-to-br from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700'
                  : 'bg-gray-700 text-gray-500 cursor-not-allowed'
              }`}
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}