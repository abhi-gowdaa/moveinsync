// src/components/MessageBubble.js
import React from 'react';
import './MessageBubble.css';

const MessageBubble = ({ message }) => {
  const formatTime = (date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };
  
  return (
    <div className={`message-bubble ${message.sender} ${message.isError ? 'error' : ''}`}>
      {message.image && (
        <div className="message-image">
          <img src={message.image} alt="Uploaded" />
        </div>
      )}
      <div className="message-content">
        {message.text}
      </div>
      <div className="message-time">
        {formatTime(message.timestamp)}
      </div>
    </div>
  );
};

export default MessageBubble;