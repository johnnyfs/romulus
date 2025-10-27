import React, { useState } from 'react';
import styles from './Chat.module.css';

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
    <div className={styles.chatContainer}>
      <div className={styles.chatHeader}>
        Chat
      </div>

      <div className={styles.chatMessages}>
        {messages.length === 0 && (
          <div className={styles.chatEmpty}>
            No messages yet. Start chatting!
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`${styles.chatMessage} ${styles[`chatMessage${msg.role.charAt(0).toUpperCase() + msg.role.slice(1)}`]}`}
          >
            {msg.content}
          </div>
        ))}
      </div>

      <div className={styles.chatInputContainer}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type a message..."
          className={styles.chatInput}
        />
        <button
          onClick={handleSend}
          disabled={!input.trim()}
          className={styles.chatSendButton}
        >
          Send
        </button>
      </div>
    </div>
  );
}

export default Chat;
