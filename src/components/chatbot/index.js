import React, { useState } from 'react';
import ChatBubble from './ChatBubble';
import ChatWindow from './ChatWindow';

const ChatBot = () => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  return (
    <>
      <ChatWindow isOpen={isOpen} onClose={toggleChat} />
      <ChatBubble isOpen={isOpen} onClick={toggleChat} />
    </>
  );
};

export default ChatBot;