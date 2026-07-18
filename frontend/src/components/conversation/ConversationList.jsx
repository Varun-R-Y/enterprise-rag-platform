import ConversationItem from './ConversationItem';
import Spinner from '../ui/Spinner';

export default function ConversationList({ 
  conversations, 
  activeId, 
  onSelect, 
  onDeleteClick, 
  onLoadMore, 
  hasMore, 
  loadingMore 
}) {
  if (!conversations || conversations.length === 0) {
    return (
      <div className="text-center py-8 text-xs font-semibold text-slate-500">
        No chats recorded
      </div>
    );
  }

  return (
    <div className="flex-grow overflow-y-auto space-y-1.5 pr-1 max-h-[calc(100vh-250px)] md:max-h-[calc(100vh-210px)] select-none">
      {conversations.map((conv) => (
        <ConversationItem
          key={conv.id}
          conversation={conv}
          isActive={conv.id === activeId}
          onClick={() => onSelect(conv)}
          onDeleteClick={onDeleteClick}
        />
      ))}

      {/* Pagination trigger button */}
      {hasMore && (
        <div className="pt-2 text-center">
          {loadingMore ? (
            <Spinner size="xs" className="mx-auto" />
          ) : (
            <button
              onClick={onLoadMore}
              className="text-[11px] font-semibold text-indigo-400 hover:text-indigo-300 py-1.5 px-3 rounded hover:bg-slate-800 transition duration-150 cursor-pointer w-full focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              Load More Chats
            </button>
          )}
        </div>
      )}
    </div>
  );
}
