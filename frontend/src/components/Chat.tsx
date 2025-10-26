import React, { useState } from 'react';

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
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      border: '1px solid #ddd',
      borderRadius: '4px',
      backgroundColor: '#fff'
    }}>
      <div style={{
        padding: '10px',
        borderBottom: '1px solid #ddd',
        backgroundColor: '#f5f5f5',
        fontWeight: 'bold'
      }}>
        Chat
      </div>

      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '10px',
        display: 'flex',
        flexDirection: 'column',
        gap: '10px'
      }}>
        {messages.length === 0 && (
          <div style={{ color: '#999', textAlign: 'center', marginTop: '20px' }}>
            No messages yet. Start chatting!
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            style={{
              alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '80%',
              padding: '8px 12px',
              borderRadius: '8px',
              backgroundColor: msg.role === 'user' ? '#007bff' : '#e9ecef',
              color: msg.role === 'user' ? '#fff' : '#000'
            }}
          >
            {msg.content}
          </div>
        ))}
      </div>

      <div style={{
        padding: '10px',
        borderTop: '1px solid #ddd',
        display: 'flex',
        gap: '10px'
      }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type a message..."
          style={{
            flex: 1,
            padding: '8px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            fontSize: '14px'
          }}
        />
        <button
          onClick={handleSend}
          disabled={!input.trim()}
          style={{
            padding: '8px 16px',
            backgroundColor: '#007bff',
            color: '#fff',
            border: 'none',
            borderRadius: '4px',
            cursor: input.trim() ? 'pointer' : 'not-allowed',
            opacity: input.trim() ? 1 : 0.6
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
}

export default Chat;
