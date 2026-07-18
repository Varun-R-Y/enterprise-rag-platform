import { useEffect, useRef } from 'react';
import { SendHorizontal } from 'lucide-react';

export default function ChatInput({ value, onChange, onSubmit, disabled }) {
  const textareaRef = useRef(null);

  // Auto-resize textarea height up to 192px (max-h-48) before scrolling
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 192)}px`;
    }
  }, [value]);

  // Auto-focus input on mount
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  }, []);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (value.trim() && !disabled) {
        onSubmit();
      }
    }
  };

  return (
    <div className="relative border border-slate-200 rounded-xl bg-white shadow-2xs focus-within:ring-2 focus-within:ring-indigo-500 focus-within:border-indigo-500 transition duration-150 px-4 py-3 flex items-end gap-3 max-w-4xl mx-auto w-full">
      <textarea
        ref={textareaRef}
        rows={1}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask a question about your documents..."
        disabled={disabled}
        className="flex-grow resize-none overflow-y-auto bg-transparent border-0 outline-none text-sm text-slate-700 leading-normal max-h-48 py-1 focus:ring-0 focus:outline-none placeholder-slate-400"
      />
      <button
        onClick={onSubmit}
        disabled={disabled || !value.trim()}
        className="p-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-100 text-white disabled:text-slate-400 rounded-lg transition shrink-0 cursor-pointer disabled:cursor-not-allowed focus:outline-none"
        aria-label="Send message"
      >
        <SendHorizontal size={16} />
      </button>
    </div>
  );
}
