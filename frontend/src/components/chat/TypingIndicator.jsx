export default function TypingIndicator() {
  return (
    <div className="flex items-center gap-1.5 px-4 py-3 bg-slate-100/80 rounded-2xl w-fit border border-slate-200/50 shadow-2xs">
      <div className="w-1.5 h-1.5 bg-slate-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
      <div className="w-1.5 h-1.5 bg-slate-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
      <div className="w-1.5 h-1.5 bg-slate-500 rounded-full animate-bounce"></div>
    </div>
  );
}
