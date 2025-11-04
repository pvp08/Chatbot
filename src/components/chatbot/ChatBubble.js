import React from 'react';
import { MessageCircle, X } from 'lucide-react';

const ChatBubble = ({ isOpen, onClick }) => {
  return (
    <button
      onClick={onClick}
      className="fixed bottom-8 right-8 z-50 w-16 h-16 bg-blue-600 rounded-full shadow-2xl hover:bg-blue-700 transition-all duration-300 flex items-center justify-center group hover:scale-110"
      aria-label={isOpen ? "Close chat" : "Open chat"}
    >
      {isOpen ? (
        <X className="w-7 h-7 text-white transition-transform duration-300" />
      ) : (
        <MessageCircle className="w-7 h-7 text-white transition-transform duration-300 group-hover:scale-110" />
      )}
      
      {/* Pulsing indicator when closed */}
      {!isOpen && (
        <>
          <span className="absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75 animate-ping"></span>
          <span className="absolute top-2 right-2 w-3 h-3 bg-green-400 rounded-full border-2 border-white"></span>
        </>
      )}
    </button>
  );
};

export default ChatBubble;