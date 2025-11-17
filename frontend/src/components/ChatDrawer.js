// src/components/ChatDrawer.js
import React, { useState, useRef, useEffect } from 'react';
import { useChat } from '../hooks/useChat';
import MessageBubble from './MessageBubble';
import ConfirmationButtons from './ConfirmationButtons';
import UploadButton from './UploadButton';
import AudioButton from './AudioButton';
import SpeakButton from './SpeakButton';
import './ChatDrawer.css';

// MUI Icons
import CloseIcon from '@mui/icons-material/Close';
import SendRoundedIcon from '@mui/icons-material/SendRounded';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import SmartToyOutlinedIcon from '@mui/icons-material/SmartToyOutlined';
 
const ChatDrawer = ({ isOpen, onClose, currentPage }) => {
  const {
    messages,
    isLoading,
    sendMessage,
    sendImage,
    confirmAction,
    cancelAction,
    awaitingConfirmation,
    clearMessages
  } = useChat();
  
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef(null);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  const handleSendMessage = () => {
    if (inputText.trim()) {
      sendMessage(inputText, currentPage);
      setInputText('');
    }
  };
  
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  
  const handleImageUpload = (file) => {
    sendImage(file, inputText || 'Analyze this image', currentPage);
    setInputText('');
  };
  
  const handleTranscription = (transcription) => {
    setInputText(prev => prev ? `${prev} ${transcription}` : transcription);
  };
  
  return (
    <div className={`chat-drawer ${isOpen ? 'open' : ''}`}>
      {/* Header */}
      <div className="chat-header">
        <div className="chat-header-content">
          <div className="chat-header-icon">
            <SmartToyOutlinedIcon sx={{ fontSize: 24, color: '#10a37f' }} />
          </div>
          <div className="chat-header-text">
            <h3>Movi Assistant</h3>
            <span className="chat-status">Always here to help</span>
          </div>
        </div>
        <button className="close-btn" onClick={onClose} aria-label="Close chat">
          <CloseIcon sx={{ fontSize: 20 }} />
        </button>
      </div>
      
      {/* Messages */}
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <div className="welcome-icon">
              <SmartToyOutlinedIcon sx={{ fontSize: 48, color: '#10a37f' }} />
            </div>
            <h4>How can I help you today?</h4>
            <div className="suggestion-chips">
              <button className="suggestion-chip" onClick={() => sendMessage('Show unassigned vehicles', currentPage)}>
                <span>🚌</span> Show unassigned vehicles
              </button>
              <button className="suggestion-chip" onClick={() => sendMessage('How do I create a route?', currentPage)}>
                <span>🗺️</span> How do I create a route?
              </button>
              <button className="suggestion-chip" onClick={() => sendMessage('List all trips', currentPage)}>
                <span>📋</span> List all trips
              </button>
              <button className="suggestion-chip" onClick={() => sendMessage('Help me assign a vehicle', currentPage)}>
                <span>🔧</span> Help me assign a vehicle
              </button>
            </div>
          </div>
        ) : (
          <>
            {messages.map(message => (
              <div key={message.id} className={`message-wrapper ${message.sender}`}>
                {message.sender === 'assistant' && (
                  <div className="message-avatar">
                    <SmartToyOutlinedIcon sx={{ fontSize: 18, color: '#fff' }} />
                  </div>
                )}
                <div className="message-content">
                  <MessageBubble message={message} />
                  {message.sender === 'assistant' && !message.isError && (
                    <SpeakButton text={message.text} disabled={isLoading} />
                  )}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="message-wrapper assistant">
                <div className="message-avatar">
                  <SmartToyOutlinedIcon sx={{ fontSize: 18, color: '#fff' }} />
                </div>
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      {/* Input Area */}
      {awaitingConfirmation ? (
        <ConfirmationButtons 
          onConfirm={confirmAction}
          onCancel={cancelAction}
          disabled={isLoading}
        />
      ) : (
        <div className="chat-input-container">
          <div className="input-wrapper">
            <div className="input-row">
              <AudioButton onTranscription={handleTranscription} disabled={isLoading} />
              <UploadButton onUpload={handleImageUpload} disabled={isLoading} />
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Message Movi..."
                disabled={isLoading}
                className="chat-input"
                rows="1"
              />
              <button 
                onClick={handleSendMessage} 
                disabled={isLoading || !inputText.trim()}
                className="send-btn"
                aria-label="Send message"
              >
                <SendRoundedIcon sx={{ fontSize: 20 }} />
              </button>
            </div>
            <div className="input-footer">
              <span className="footer-text">Movi can make mistakes. Check important info.</span>
            </div>
          </div>
        </div>
      )}
      
      {/* Footer Actions */}
      {messages.length > 0 && (
        <div className="chat-actions">
          <button onClick={clearMessages} className="clear-btn">
            <DeleteOutlineIcon sx={{ fontSize: 16, marginRight: '6px' }} />
            Clear conversation
          </button>
        </div>
      )}
    </div>
  );
};

export default ChatDrawer;