import React, { useState, useEffect, useRef, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { FaArrowUp, FaMoon, FaSun, FaFileExport, FaTrash } from 'react-icons/fa';
import { FiCopy } from 'react-icons/fi';
import './chatbox.css';
import {
  Moon, Sun, Trash2, FileDown, X
} from "lucide-react";



function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [darkMode, setDarkMode] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [isOnline, setIsOnline] = useState(true);
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  // Load saved messages and theme from localStorage
  useEffect(() => {
    const savedMessages = localStorage.getItem('chatMessages');
    const savedTheme = localStorage.getItem('darkMode');
    
    if (savedMessages) {
      try {
        setMessages(JSON.parse(savedMessages));
      } catch (e) {
        console.error("Failed to parse saved messages", e);
      }
    }
    
    if (savedTheme) {
      setDarkMode(savedTheme === 'true');
    }

    // Check online status
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Save messages and theme to localStorage
  useEffect(() => {
    localStorage.setItem('chatMessages', JSON.stringify(messages));
  }, [messages]);

  useEffect(() => {
    localStorage.setItem('darkMode', darkMode);
    document.documentElement.className = darkMode ? 'dark' : '';
  }, [darkMode]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  // Focus input on load
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const simulateTyping = useCallback(() => {
    setIsTyping(true);
    return new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1000));
  }, []);

  const handleSend = async (e) => {
    e?.preventDefault();
    if (!input.trim()) return;

    const userMsg = {
      role: 'user',
      content: input,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsTyping(true);

    try {
      await simulateTyping();

      if (!isOnline) {
        throw new Error("Offline - Can't connect to server");
      }

      const res = await fetch('http://localhost:5000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: input, 
          user_id: "demo-user", 
          user_name: "" 
        })
      });

      if (!res.ok) throw new Error(res.statusText);
      
      const data = await res.json();
      const botMsg = {
        role: 'bot',
        content: data.reply,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        buttons: data.buttons || [],
        showButtons: data.buttons && data.buttons.length > 0
      };

      setMessages(prev => [...prev, botMsg]);
    } catch (err) {
      const errorMsg = {
        role: 'bot',
        content: isOnline 
          ? "```error\n⚠️ We are experiencing high traffic. Please try again.\n```"
          : "```error\n⚠️ You are offline. Please check your connection.\n```",
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, errorMsg]);
      console.error("API Error:", err);
    } finally {
      setIsTyping(false);
    }
  };

  const handleExport = () => {
    const text = messages.map(m => 
      `${m.role === 'user' ? 'You' : 'Assistant'} (${m.time}):\n${m.content.replace(/\n/g, '\n  ')}`
    ).join('\n\n---\n\n');
    
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `xcer-chat-${new Date().toISOString().slice(0,10)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleReset = () => {
    if (messages.length > 0 && !window.confirm('Clear all chat history?')) return;
    setMessages([]);
  };

  const sendFlowMessage = async (flowMsg) => {
    setIsTyping(true);
    try {
      const res = await fetch('http://localhost:5000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: flowMsg,
          user_id: "demo-user",
          user_name: ""
        })
      });

      if (!res.ok) throw new Error(res.statusText);
      const data = await res.json();

      const botMsg = {
        role: 'bot',
        content: data.reply,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        buttons: data.buttons || [],
        showButtons: data.buttons && data.buttons.length > 0
      };

      setMessages(prev => [...prev, botMsg]);
    } catch (err) {
      console.error("Flow API Error:", err);
      setMessages(prev => [...prev, {
        role: 'bot',
        content: "```error\n⚠️ Could not process the request. Try again.\n```",
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      // You could add a temporary notification here
    }).catch(err => {
      console.error('Failed to copy:', err);
    });
  };

  const formatTime = (timeString) => {
    return timeString || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
<div className={`chat-container ${darkMode ? 'dark-mode' : 'light-mode'}`}>
      {/* Header */}
<div className={`chat-header ${darkMode ? 'dark-header' : 'light-header'}`}>
        <h2 className="text-sm font-semibold truncate">XCER Labs Chat</h2>

    <div className="header-buttons flex gap-2">
  <button
    className="icon-btn"
    onClick={() => setDarkMode(!darkMode)}
    aria-label="Toggle Theme"
  >
    {darkMode ? <Sun size={18} /> : <Moon size={18} />}
  </button>

  {messages.length > 0 && (
    <>
      <button
        className="icon-btn"
        onClick={handleExport}
        aria-label="Export Chat"
      >
        <FileDown size={18} />
      </button>

      <button
        className="icon-btn"
        onClick={handleReset}
        aria-label="Clear Chat"
      >
        <Trash2 size={18} />
      </button>
    </>
  )}
</div>


      </div>

      {/* Chat container */}
<div className="chat-body">
        {messages.length === 0 && (
<div className="chat-welcome">
  <p className="chat-welcome-text">Welcome to XCER Labs Assistant! How can I help you today?</p>
</div>

        )}
        
        {messages.map((msg, i) => (

          <div 
  key={i}
  className={`chat-message ${msg.role === 'user' ? 'user-message' : 'bot-message'}`}
  data-time={formatTime(msg.time)}
>

            <div className="prose dark:prose-invert prose-sm max-w-none">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {msg.content}
              </ReactMarkdown>
            </div>
{msg.role !== 'user' && (

<span className={`msg-time ${msg.role === 'user' ? 'user-time' : 'bot-time'}`}>
              {formatTime(msg.time)}
            </span>)}

           
         {msg.role === 'bot' && msg.buttons && Array.isArray(msg.buttons) && msg.showButtons && msg.buttons.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-2">
                {msg.buttons.map((button, index) => {
                  const handleButtonClick = () => {
                    const { type, value, flow } = button;
                    switch (type) {
                      case 'whatsapp': {
                        const number = value.replace(/\D/g, '');
                        window.open(`https://wa.me/${number}`, '_blank');
                        break;
                      }
                      case 'url':
                      case 'link': {
                        window.open(value.includes('http') ? value : `https://${value}`, '_blank');
                        break;
                      }
                      case 'email': {
                        window.open(`mailto:${value}`, '_blank');
                        break;
                      }
                      case 'phone': {
                        window.open(`tel:${value}`, '_blank');
                        break;
                      }
                      case 'flow':
                      case 'next': {
                        sendFlowMessage(`[FLOW] ${value}`, false);
                        break;
                      }
                      default:
                        console.warn('Unknown button type:', type);
                    }

                    if (flow) {
                      setMessages(prev =>
                        prev.map(m =>
                          m.id === msg.id ? { ...m, showButtons: false } : m
                        )
                      );
                    }
                  };

                  return (
                    <button
                      key={`${index}-${button.label}`}
                      className={`chat-button ${darkMode ? 'dark-button' : 'light-button'}`}

                      onClick={handleButtonClick}
                    >
                      {button.label}
                    </button>
                  );
                })}
              </div>
            )}

            <button 
              className={`absolute top-1 right-1 opacity-0 hover:opacity-100 transition p-1 rounded ${
                msg.role === 'user' 
                  ? 'hover:bg-blue-700/50' 
                  : 'hover:bg-gray-300/50 dark:hover:bg-gray-600/50'
              }`}
              onClick={() => copyToClipboard(msg.content)}
              aria-label="Copy to clipboard"
            >
              <FiCopy size={14} className={msg.role === 'user' ? 'text-blue-100' : 'text-gray-500 dark:text-gray-400'} />
            </button>
          </div>
        ))}

        {isTyping && (
          <div className="typing-indicator">
  <div className="typing-dot dot1" />
  <div className="typing-dot dot2" />
  <div className="typing-dot dot3" />
</div>

        )}
        <div ref={bottomRef} />
      </div>

{/* Input area */}
<div className={`chat-input-area ${darkMode ? 'dark-mode' : ''}`}>
  <form onSubmit={handleSend} className="chat-form">
    <textarea
  ref={inputRef}
  value={input}
  onChange={(e) => setInput(e.target.value)}
  onKeyDown={(e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend(e);
    }
  }}
  placeholder="Message XCER Assistant..."
  className="chat-input"
  aria-label="Chat input"
  disabled={isTyping}
  rows={1}
/>

    <button 
      type="submit" 
      disabled={!input.trim() || isTyping}
      className="chat-send-button"
      aria-label="Send message"
    >
      <FaArrowUp size={16} />
    </button>
  </form>
</div>


      
      {!isOnline && (
  <div className={`offline-banner ${darkMode ? 'dark-mode' : ''}`}>
    You are offline. Messages will be sent when you reconnect.
  </div>
)}

    </div>
  );
}

export default App;