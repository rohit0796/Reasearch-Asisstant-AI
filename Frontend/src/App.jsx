// src/App.js
import React, { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {

  const URL = 'http://127.0.0.1:8000'
  const [messages, setMessages] = useState([
    {
      text: "Hello! I'm your research assistant. You can paste YouTube links, upload PDFs, or ask me questions about your research.",
      sender: 'ai',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [input, setInput] = useState('');
  const [sessionId] = useState(Date.now().toString());
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom of messages
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const detectUrlType = (text) => {
    if (/youtube\.com|youtu\.be/.test(text)) {
      return { type: "YouTube", icon: "▶️" };
    } else if (/https?:\/\/[^\s]+/.test(text)) {
      return { type: "Web Article", icon: "🌐" };
    } else if (/\.pdf$/.test(text)) {
      return { type: "PDF Document", icon: "📄" };
    }
    return null;
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    // Add user message
    const userMsg = {
      text: input,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch(`${URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: input,
          session_id: sessionId
        })
      });
      var responseText = await response.json();
      const aiMsg = {
        text: responseText.response,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, aiMsg]);
    } catch (error) {
      const errorMsg = {
        text: "I'm having trouble connecting right now. Please try again later.",
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePdfUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("session_id", sessionId);

    // Add upload notification
    const uploadMsg = {
      text: `Uploading PDF: ${file.name}`,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setMessages(prev => [...prev, uploadMsg]);

    try {
      const response = await fetch(`${URL}/upload-pdf`, {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      const aiMsg = {
        text: data.status,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, aiMsg]);
    } catch (error) {
      const errorMsg = {
        text: "Failed to process PDF. Please try a different file.",
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <div className="app-container">

      {/* Sidebar with info */}
      <div className="info-sidebar">
        <div className="sidebar-section">
          <h2>Research Assistant</h2>
          <p>Your AI-powered research companion that can analyze content from multiple sources:</p>
        </div>

        <div className="sidebar-section">
          <h3>How It Works</h3>
          <div className="feature-card">
            <div className="feature-icon">📄</div>
            <div>
              <h4>PDF Documents</h4>
              <p>Upload research papers, articles, or reports for analysis</p>
            </div>
          </div>
          <div className="feature-card">
            <div className="feature-icon">▶️</div>
            <div>
              <h4>YouTube Videos</h4>
              <p>Paste video links to extract and analyze transcripts</p>
            </div>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🌐</div>
            <div>
              <h4>Web Articles</h4>
              <p>Provide URLs to online content for summarization</p>
            </div>
          </div>
        </div>

        <div className="sidebar-section">
          <h3>Powered By</h3>
          <div className="tech-badges">
            <span>Llama 3</span>
            <span>LangChain</span>
            <span>Groq</span>
            <span>FAISS</span>
          </div>
        </div>

        <div className="sidebar-section">
          <div className="stats-card">
            <div className="stat">
              <div className="stat-value">3</div>
              <div className="stat-label">Source Types</div>
            </div>
            <div className="stat">
              <div className="stat-value">∞</div>
              <div className="stat-label">Research Topics</div>
            </div>
          </div>
        </div>
      </div>

      <div className="chat-container">
        {/* Header */}
        <div className="chat-header">
          <div className="header-content">
            <div className="ai-avatar">RA</div>
            <div>
              <h1>Research Assistant</h1>
              <p>Powered by Llama 3 & LangChain</p>
            </div>
          </div>
          <div className="status-indicator">
            <div className={`status-dot ${isLoading ? 'loading' : 'active'}`}></div>
            <span>{isLoading ? 'Thinking...' : 'Online'}</span>
          </div>
        </div>

        {/* Messages Area */}
        <div className="messages-area">
          {messages.map((msg, i) => {
            const urlInfo = detectUrlType(msg.text);
            return (
              <div
                key={i}
                className={`message ${msg.sender}`}
              >
                <div className="message-content">
                  {urlInfo ? (
                    <div className="url-message">
                      <div className="url-badge">
                        <span className="url-icon">{urlInfo.icon}</span>
                        <span className="url-type">{urlInfo.type}</span>
                      </div>
                      <div className="url-text">{msg.text}</div>
                    </div>
                  ) : msg.text}
                </div>
                <div className="message-timestamp">{msg.timestamp}</div>
              </div>
            );
          })}
          <div ref={messagesEndRef} />
          {isLoading && (
            <div className="message ai">
              <div className="message-content">
                <div className="typing-indicator">
                  <div className="dot"></div>
                  <div className="dot"></div>
                  <div className="dot"></div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="input-area">
          <div className="file-upload-btn" onClick={() => fileInputRef.current.click()}>
            {isUploading ? (
              <div className="upload-spinner"></div>
            ) : (
              <>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M11 16V7.85l-2.6 2.6L7 9l5-5 5 5-1.4 1.45-2.6-2.6V16h-2Zm-8 4v-5h2v3h14v-3h2v5H3Z" />
                </svg>
                <span>PDF</span>
              </>
            )}
            <input
              type="file"
              accept=".pdf"
              onChange={handlePdfUpload}
              ref={fileInputRef}
              style={{ display: 'none' }}
            />
          </div>

          <div className="input-wrapper">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask a question, paste URL, or upload PDF..."
              disabled={isLoading}
            />
            <div className="input-hints">
              <span>YouTube</span>
              <span>PDF</span>
              <span>Web</span>
            </div>
          </div>

          <button
            onClick={handleSend}
            className="send-btn"
            disabled={isLoading || !input.trim()}
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path d="M3 20v-6l8-2-8-2V4l19 8-19 8Z" />
            </svg>
          </button>
        </div>
      </div>


    </div>
  );
}

export default App;