import React, { useState } from 'react';
import './Chat.css';

interface ChatProps {
  gameId: string;
}

function Chat({ gameId }: ChatProps) {
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant', content: string }>>([]);
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (!input.trim()) return;

    // Add user message
    setMessages([...messages, { role: 'user', content: input }]);

    // TODO: Send to backend and get AI response
    // For now, just echo back
    setTimeout(() => {
      setMessages(prev => [...prev, { role: 'assistant', content: `Echo: ${input}` }]);
    }, 500);

    setInput('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        Chat
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-empty">
            No messages yet. Start chatting!
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`chat-message chat-message--${msg.role}`}
          >
            {msg.content}
          </div>
        ))}
      </div>

      <div className="chat-input-container">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type a message..."
          className="chat-input"
        />
        <button
          onClick={handleSend}
          disabled={!input.trim()}
          className="chat-send-button"
        >
          Send
        </button>
      </div>
    </div>
  );
}

export default Chat;
