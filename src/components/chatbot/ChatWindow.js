import React, { useState, useEffect, useRef } from 'react';
import { Send, X, Bot } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ChatWindow = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [showLeadForm, setShowLeadForm] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 200);
      
      if (messages.length === 0) {
        setMessages([
          {
            id: 'welcome',
            role: 'assistant',
            content: 'Hello! Welcome to Pinnacle Sync. I\'m here to assist you with our IT recruiting services and software solutions. How may I help you today?',
            timestamp: new Date()
          }
        ]);
      }
    }
  }, [isOpen, messages.length]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessageText = inputMessage.trim();
    setInputMessage('');
    
    const tempUserMessage = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: userMessageText,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, tempUserMessage]);
    setIsLoading(true);

    try {
      const response = await axios.post(`${API}/chat/message`, {
        session_id: sessionId,
        message: userMessageText
      });

      const { session_id, user_message, assistant_message } = response.data;
      
      if (!sessionId) {
        setSessionId(session_id);
      }

      setMessages(prev => {
        const withoutTemp = prev.filter(msg => msg.id !== tempUserMessage.id);
        return [
          ...withoutTemp,
          {
            ...user_message,
            timestamp: new Date(user_message.timestamp)
          },
          {
            ...assistant_message,
            timestamp: new Date(assistant_message.timestamp)
          }
        ];
      });

    } catch (error) {
      console.error('Error sending message:', error);
      
      setMessages(prev => [
        ...prev,
        {
          id: `error-${Date.now()}`,
          role: 'assistant',
          content: 'I apologize, but I\'m having trouble connecting right now. Please try again in a moment.',
          timestamp: new Date()
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleSubmitLead = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    const leadData = {
      session_id: sessionId,
      name: formData.get('name'),
      email: formData.get('email'),
      phone: formData.get('phone'),
      company: formData.get('company'),
      interest: formData.get('interest')
    };

    if (!leadData.name || !leadData.email) {
      alert('Please fill in required fields (Name and Email)');
      return;
    }

    try {
      await axios.post(`${API}/chat/lead`, leadData);

      setMessages(prev => [
        ...prev,
        {
          id: `lead-${Date.now()}`,
          role: 'assistant',
          content: 'Thank you! A member of our team will reach out to you shortly. Is there anything else I can help you with?',
          timestamp: new Date()
        }
      ]);

      setShowLeadForm(false);
    } catch (error) {
      console.error('Error submitting lead:', error);
      alert('There was an error submitting your information. Please try again.');
    }
  };

  if (!isOpen) return null;

  return (
    <>
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 z-40"
        onClick={onClose}
      />

      <div className="fixed bottom-8 right-8 z-50 w-[420px] h-[650px] bg-white rounded-2xl shadow-2xl flex flex-col overflow-hidden">
        <div className="bg-blue-600 text-white p-5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
              <Bot className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h3 className="font-semibold text-lg">Pinnacle Sync Assistant</h3>
              <p className="text-xs text-blue-100">We're here to help</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-white/20 rounded-lg transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-5 space-y-4 bg-gray-50">
          {messages.map((message, index) => (
            <div
              key={message.id || index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {message.role === 'assistant' ? (
                <div className="flex gap-3 max-w-[85%]">
                  <div className="bg-gray-300 p-2.5 rounded-full h-fit flex-shrink-0">
                    <Bot className="w-5 h-5 text-gray-600" />
                  </div>
                  <div className="bg-white p-4 rounded-2xl rounded-tl-sm shadow-sm border border-gray-200">
                    <p className="text-sm text-gray-800 whitespace-pre-wrap break-words">
                      {message.content}
                    </p>
                  </div>
                </div>
              ) : (
                <div className="bg-blue-600 text-white p-4 rounded-2xl rounded-br-sm shadow-sm max-w-[85%]">
                  <p className="text-sm whitespace-pre-wrap break-words">
                    {message.content}
                  </p>
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="flex gap-3">
                <div className="bg-gray-300 p-2.5 rounded-full h-fit">
                  <Bot className="w-5 h-5 text-gray-600" />
                </div>
                <div className="bg-white p-4 rounded-2xl rounded-tl-sm shadow-sm border border-gray-200">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {showLeadForm && (
          <div className="p-5 border-t border-gray-200 bg-gray-50">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-gray-800">Get in Touch</h3>
              <button onClick={() => setShowLeadForm(false)} className="text-gray-400 hover:text-gray-600">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleSubmitLead} className="space-y-2">
              <input type="text" name="name" placeholder="Name *" required className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm" />
              <input type="email" name="email" placeholder="Email *" required className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm" />
              <input type="tel" name="phone" placeholder="Phone" className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm" />
              <input type="text" name="company" placeholder="Company" className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm" />
              <select name="interest" className="w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm">
                <option value="recruiting">IT Recruiting</option>
                <option value="software">Software Solutions</option>
                <option value="consultation">Consultation</option>
                <option value="other">Other</option>
              </select>
              <button type="submit" className="w-full bg-blue-600 text-white px-4 py-2.5 rounded-lg hover:bg-blue-700 transition-colors font-medium">
                Submit
              </button>
            </form>
          </div>
        )}

        <div className="p-5 bg-white border-t border-gray-200">
          {!showLeadForm && (
            <div className="mb-3">
              <button onClick={() => setShowLeadForm(true)} className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                Get a callback from our team
              </button>
            </div>
          )}
          
          <div className="flex items-end gap-2">
            <input
              ref={inputRef}
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              disabled={isLoading}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:bg-gray-100 text-sm"
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || isLoading}
              className="flex-shrink-0 bg-blue-600 text-white p-3 rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2 text-center">Press Enter to send</p>
        </div>
      </div>
    </>
  );
};

export default ChatWindow;