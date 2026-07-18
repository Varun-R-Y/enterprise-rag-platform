import { X } from 'lucide-react';
import NewConversationButton from './NewConversationButton';
import ConversationList from './ConversationList';

export default function ConversationSidebar({
  conversations,
  activeId,
  onSelect,
  onDeleteClick,
  onCreateNew,
  onLoadMore,
  hasMore,
  loadingMore,
  isOpen,
  onClose
}) {
  const sidebarContent = (
    <div className="flex flex-col h-full bg-slate-900 text-slate-100 p-4 space-y-4 select-none">
      
      {/* Sidebar Header & Close (for Mobile Drawer) */}
      <div className="flex items-center justify-between shrink-0">
        <h2 className="text-sm font-bold text-slate-400 uppercase tracking-wider">
          Conversations
        </h2>
        <button
          onClick={onClose}
          className="p-1.5 text-slate-400 hover:text-white rounded hover:bg-slate-800 transition md:hidden cursor-pointer focus:outline-none"
          aria-label="Close sidebar"
        >
          <X size={16} />
        </button>
      </div>

      {/* New Conversation Button */}
      <NewConversationButton onClick={onCreateNew} />

      {/* Conversation List */}
      <ConversationList
        conversations={conversations}
        activeId={activeId}
        onSelect={(conv) => {
          onSelect(conv);
          onClose(); // Auto close on mobile select
        }}
        onDeleteClick={onDeleteClick}
        onLoadMore={onLoadMore}
        hasMore={hasMore}
        loadingMore={loadingMore}
      />
    </div>
  );

  return (
    <>
      {/* Desktop Sidebar (Persistent) */}
      <aside className="hidden md:flex flex-col w-[300px] border-r border-slate-800 shrink-0 bg-slate-900">
        {sidebarContent}
      </aside>

      {/* Mobile Drawer Backdrop overlay */}
      {isOpen && (
        <div 
          onClick={onClose}
          className="fixed inset-0 z-30 bg-slate-950/60 backdrop-blur-xs md:hidden"
        />
      )}

      {/* Mobile Drawer Sidebar */}
      <aside 
        className={`fixed inset-y-0 left-0 z-40 w-[280px] bg-slate-900 border-r border-slate-800 transition-transform duration-200 ease-in-out md:hidden ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {sidebarContent}
      </aside>
    </>
  );
}
