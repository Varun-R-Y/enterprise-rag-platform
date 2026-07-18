import { MessageSquare, Trash2 } from 'lucide-react';

export default function ConversationItem({ conversation, isActive, onClick, onDeleteClick }) {
  
  const getRelativeTime = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  };

  const handleDelete = (e) => {
    e.stopPropagation();
    onDeleteClick(conversation);
  };

  return (
    <div
      onClick={onClick}
      className={`group flex items-center justify-between p-3.5 rounded-lg transition-all duration-150 cursor-pointer select-none border border-transparent ${
        isActive
          ? 'bg-slate-700 text-white shadow-2xs font-semibold'
          : 'hover:bg-slate-750 text-slate-300 hover:text-white'
      }`}
    >
      <div className="flex items-center gap-3 min-w-0 flex-grow pr-2">
        <MessageSquare size={16} className={`shrink-0 ${isActive ? 'text-indigo-400' : 'text-slate-400 group-hover:text-slate-200'}`} />
        <div className="min-w-0 flex-grow">
          <div className="text-sm truncate leading-snug" title={conversation.title}>
            {conversation.title}
          </div>
          <div className="flex items-center gap-2 mt-1 text-[10px] font-medium text-slate-400 select-none">
            <span>{getRelativeTime(conversation.updated_at || conversation.created_at)}</span>
            <span>•</span>
            <span className={`px-1 rounded ${isActive ? 'bg-slate-600 text-slate-200' : 'bg-slate-800 text-slate-400 group-hover:text-slate-350'}`}>
              {conversation.message_count || 0} messages
            </span>
          </div>
        </div>
      </div>

      {/* Delete trash button action */}
      <button
        onClick={handleDelete}
        className={`p-1.5 rounded text-slate-400 hover:text-rose-400 hover:bg-slate-800/80 transition cursor-pointer md:opacity-0 group-hover:opacity-100 focus:opacity-100 focus:outline-none`}
        aria-label="Delete chat conversation"
      >
        <Trash2 size={14} />
      </button>
    </div>
  );
}
