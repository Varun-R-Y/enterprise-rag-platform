import { MessageSquareText } from 'lucide-react';
import Button from '../ui/Button';

export default function EmptyConversationState({ onCreateNew }) {
  return (
    <div className="flex-grow flex flex-col items-center justify-center p-8 text-center max-w-md mx-auto my-12 animate-in fade-in duration-200">
      <div className="p-4 bg-indigo-50 text-indigo-600 rounded-full mb-4 shadow-2xs border border-indigo-100 shrink-0">
        <MessageSquareText size={32} />
      </div>
      <h3 className="text-lg font-bold text-slate-800 mb-2">No conversations yet</h3>
      <p className="text-sm text-slate-500 mb-6 leading-relaxed">
        Start a new conversation to begin asking questions about your uploaded documents using Retrieval-Augmented Generation.
      </p>
      <Button
        onClick={onCreateNew}
        className="w-full h-11 px-4 py-2 cursor-pointer font-semibold"
      >
        New Conversation
      </Button>
    </div>
  );
}
