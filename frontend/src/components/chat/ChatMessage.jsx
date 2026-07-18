import { useState } from 'react';
import { Bot, User, Copy, Check, RotateCcw, ThumbsUp, ThumbsDown } from 'lucide-react';
import MessageBubble from './MessageBubble';
import SourceList from './SourceList';

export default function ChatMessage({ message, onRegenerate, isGenerating, onSelectCitation }) {
  const [copied, setCopied] = useState(false);
  const [feedback, setFeedback] = useState(null); // 'up' | 'down' | null

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const handleFeedback = (type) => {
    setFeedback(prev => prev === type ? null : type);
  };

  const isUser = message.isUser;
  const timeString = new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  return (
    <div className={`flex gap-4 p-4 md:p-6 w-full ${isUser ? 'justify-end' : 'justify-start bg-slate-50/50 border-y border-slate-100'}`}>
      <div className={`flex gap-3 md:gap-4 max-w-4xl w-full ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        
        {/* Avatar */}
        <div className={`w-8 h-8 md:w-10 md:h-10 rounded-lg flex items-center justify-center shrink-0 shadow-2xs border ${
          isUser 
            ? 'bg-slate-200 border-slate-300 text-slate-600 font-bold text-sm' 
            : 'bg-indigo-50 border-indigo-100 text-indigo-600'
        }`}>
          {isUser ? <User size={18} /> : <Bot size={18} />}
        </div>

        {/* Message Bubble + Meta */}
        <div className="flex-grow min-w-0 space-y-1">
          {/* Header */}
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-400">
            <span>{isUser ? 'You' : 'AI Assistant'}</span>
            <span>•</span>
            <span>{timeString}</span>
          </div>

          {/* Bubble wrapper */}
          <div className={`rounded-xl p-4 shadow-2xs ${
            isUser 
              ? 'bg-indigo-600 text-white' 
              : 'bg-white border border-slate-200 text-slate-800'
          }`}>
            <MessageBubble isUser={isUser} text={message.text} />
            
            {/* Citations if assistant message */}
            {!isUser && message.sources && message.sources.length > 0 && (
              <SourceList sources={message.sources} onSelectCitation={onSelectCitation} />
            )}
          </div>

          {/* Actions toolbar for assistant messages */}
          {!isUser && (
            <div className="flex items-center gap-4 pt-1 text-slate-400 text-xs font-semibold select-none animate-in fade-in duration-200">
              {/* Copy */}
              <button
                onClick={handleCopy}
                className="flex items-center gap-1.5 hover:text-slate-600 transition cursor-pointer focus:outline-none"
                title="Copy response to clipboard"
              >
                {copied ? <Check size={13} className="text-emerald-500" /> : <Copy size={13} />}
                <span>{copied ? 'Copied' : 'Copy'}</span>
              </button>

              {/* Regenerate */}
              {onRegenerate && (
                <button
                  onClick={onRegenerate}
                  disabled={isGenerating}
                  className="flex items-center gap-1.5 hover:text-slate-600 disabled:opacity-40 transition cursor-pointer disabled:cursor-not-allowed focus:outline-none"
                  title="Resend last prompt"
                >
                  <RotateCcw size={13} className={isGenerating ? 'animate-spin' : ''} />
                  <span>Regenerate</span>
                </button>
              )}

              {/* Feedback Thumb Up */}
              <button
                onClick={() => handleFeedback('up')}
                className={`flex items-center gap-1 p-0.5 hover:text-emerald-600 transition cursor-pointer focus:outline-none ${
                  feedback === 'up' ? 'text-emerald-600' : ''
                }`}
                title="Helpful response"
              >
                <ThumbsUp size={13} className={feedback === 'up' ? 'fill-emerald-50' : ''} />
              </button>

              {/* Feedback Thumb Down */}
              <button
                onClick={() => handleFeedback('down')}
                className={`flex items-center gap-1 p-0.5 hover:text-rose-600 transition cursor-pointer focus:outline-none ${
                  feedback === 'down' ? 'text-rose-600' : ''
                }`}
                title="Not helpful response"
              >
                <ThumbsDown size={13} className={feedback === 'down' ? 'fill-rose-50' : ''} />
              </button>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
