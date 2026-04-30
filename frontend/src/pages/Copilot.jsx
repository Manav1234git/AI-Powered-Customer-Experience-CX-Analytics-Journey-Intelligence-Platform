import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Bot, User, Send, Loader2 } from 'lucide-react';

const API_URL = 'http://localhost:8000';

export default function Copilot() {
  const [messages, setMessages] = useState([
    { role: 'ai', content: "Hello! I'm your CX Copilot. Ask me about top complaints, churn risk, or sentiment trends." }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const endOfMessagesRef = useRef(null);

  const scrollToBottom = () => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = input.trim();
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await axios.post(`${API_URL}/query-ai`, { question: userMsg });
      setMessages(prev => [...prev, { role: 'ai', content: res.data.answer }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'ai', content: "Sorry, I encountered an error. Please try again." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] max-w-4xl mx-auto">
      <div className="mb-6">
        <h2 className="text-2xl font-bold">AI Copilot</h2>
        <p className="text-textSecondary">Query your customer data using natural language</p>
      </div>

      <div className="flex-1 bg-card rounded-xl border border-slate-700 flex flex-col overflow-hidden">
        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-6">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
              <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${
                msg.role === 'ai' ? 'bg-blue-500 text-white' : 'bg-slate-700 text-white'
              }`}>
                {msg.role === 'ai' ? <Bot size={20} /> : <User size={20} />}
              </div>
              <div className={`max-w-[80%] rounded-2xl px-5 py-3 ${
                msg.role === 'user' ? 'bg-accent text-white rounded-tr-sm' : 'bg-slate-800 text-slate-200 border border-slate-700 rounded-tl-sm'
              }`}>
                {msg.content}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex gap-4">
              <div className="w-10 h-10 rounded-full bg-blue-500 text-white flex items-center justify-center shrink-0">
                <Bot size={20} />
              </div>
              <div className="bg-slate-800 text-slate-200 border border-slate-700 rounded-2xl rounded-tl-sm px-5 py-3 flex items-center gap-2">
                <Loader2 size={16} className="animate-spin" /> Thinking...
              </div>
            </div>
          )}
          <div ref={endOfMessagesRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-slate-700 bg-slate-800">
          <form onSubmit={handleSend} className="flex gap-4">
            <input 
              type="text" 
              placeholder="E.g. Which customers are most at risk?" 
              className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500 transition-colors"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isLoading}
            />
            <button 
              type="submit" 
              disabled={isLoading || !input.trim()}
              className="bg-accent hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed text-white px-6 rounded-lg font-medium transition-colors flex items-center justify-center"
            >
              <Send size={20} />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
