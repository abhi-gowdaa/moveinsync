// src/hooks/useChat.js
import { useState, useCallback } from 'react';
import apiService from '../services/api';

export const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [awaitingConfirmation, setAwaitingConfirmation] = useState(false);
  const [pendingAction, setPendingAction] = useState(null);

  const sendMessage = useCallback(async (message, currentPage) => {
    if (!message.trim() || isLoading) return;

    // Add user message to chat
    const userMessage = { 
      id: Date.now(), 
      text: message, 
      sender: 'user',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await apiService.sendMessage(message, currentPage);
      
      // Add assistant response to chat
      const assistantMessage = {
        id: Date.now() + 1,
        text: response.response,
        sender: 'assistant',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, assistantMessage]);
      
      // Handle confirmation state
      setAwaitingConfirmation(response.requiresConfirmation || false);
      setPendingAction(response.pendingAction || null);
      
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'assistant',
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading]);

  const sendImage = useCallback(async (file, message, currentPage) => {
    if (!file || isLoading) return;

    // Add user message to chat
    const userMessage = { 
      id: Date.now(), 
      text: message || 'Analyzing image...', 
      sender: 'user',
      timestamp: new Date(),
      image: URL.createObjectURL(file)
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await apiService.sendImage(file, message, currentPage);
      
      // Add assistant response to chat
      const assistantMessage = {
        id: Date.now() + 1,
        text: response.response,
        sender: 'assistant',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, assistantMessage]);
      
      // Handle confirmation state
      setAwaitingConfirmation(response.requiresConfirmation || false);
      setPendingAction(response.pendingAction || null);
      
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, I encountered an error with the image. Please try again.',
        sender: 'assistant',
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [isLoading]);

  const confirmAction = useCallback(async () => {
    if (!awaitingConfirmation) return;
    
    setIsLoading(true);
    
    try {
      const response = await apiService.sendMessage('yes', '');
      
      // Update the last assistant message with the confirmation response
      setMessages(prev => {
        const newMessages = [...prev];
        const lastMessage = newMessages[newMessages.length - 1];
        if (lastMessage && lastMessage.sender === 'assistant') {
          lastMessage.text = response.response;
        }
        return newMessages;
      });
      
      setAwaitingConfirmation(false);
      setPendingAction(null);
      
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'assistant',
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [awaitingConfirmation]);

  const cancelAction = useCallback(async () => {
    if (!awaitingConfirmation) return;
    
    setIsLoading(true);
    
    try {
      const response = await apiService.sendMessage('no', '');
      
      // Update the last assistant message with the cancellation response
      setMessages(prev => {
        const newMessages = [...prev];
        const lastMessage = newMessages[newMessages.length - 1];
        if (lastMessage && lastMessage.sender === 'assistant') {
          lastMessage.text = response.response;
        }
        return newMessages;
      });
      
      setAwaitingConfirmation(false);
      setPendingAction(null);
      
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'assistant',
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [awaitingConfirmation]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setAwaitingConfirmation(false);
    setPendingAction(null);
  }, []);

  return {
    messages,
    isLoading,
    isDrawerOpen,
    awaitingConfirmation,
    pendingAction,
    sendMessage,
    sendImage,
    confirmAction,
    cancelAction,
    clearMessages,
    setIsDrawerOpen
  };
};