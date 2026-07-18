import { useEffect, useRef } from 'react';
import ChatMessage from './ChatMessage';
import TypingIndicator from './TypingIndicator';
import EmptyChat from './EmptyChat';
import { Bot } from 'lucide-react';

export default function ChatWindow({ messages, isGenerating, onSelectPrompt, onRegenerate, onSelectCitation }) {
  const bottomRef = useRef(null);

  // Auto-scroll to the bottom on new messages or generation status changes
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isGenerating]);

  if (!messages || messages.length === 0) {
    return <EmptyChat onSelectPrompt={onSelectPrompt} />;
  }

  return (
    <div className="flex-grow overflow-y-auto border border-slate-200 rounded-xl bg-white shadow-2xs divide-y divide-slate-100 min-h-[300px] max-h-[calc(100vh-320px)] sm:max-h-[calc(100vh-270px)]">
      <div className="flex flex-col">
        {messages.map((msg, idx) => {
          // Determine the user prompt immediately preceding this assistant message for regeneration
          const userPromptMsg = idx > 0 ? messages[idx - 1] : null;
          const regenerateCallback = !msg.isUser && userPromptMsg && onRegenerate 
            ? () => onRegenerate(userPromptMsg.text) 
            : null;

          return (
            <ChatMessage
              key={msg.id}
              message={msg}
              onRegenerate={regenerateCallback}
              isGenerating={isGenerating}
              onSelectCitation={onSelectCitation}
            />
          );
        })}

        {/* Typing indicator bubble inside message layout */}
        {isGenerating && (
          <div className="flex gap-4 p-4 md:p-6 w-full bg-slate-50/50 border-y border-slate-100">
            <div className="flex gap-3 md:gap-4 max-w-4xl w-full flex-row">
              <div className="w-8 h-8 md:w-10 md:h-10 rounded-lg flex items-center justify-center shrink-0 bg-indigo-50 border border-indigo-100 text-indigo-600 shadow-2xs">
                <Bot size={18} />
              </div>
              <div className="flex-grow min-w-0 space-y-1">
                <div className="flex items-center gap-2 text-xs font-semibold text-slate-400">
                  <span>AI Assistant</span>
                  <span>•</span>
                  <span>Thinking...</span>
                </div>
                <TypingIndicator />
              </div>
            </div>
          </div>
        )}
        
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
