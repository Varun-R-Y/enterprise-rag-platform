import { Plus } from 'lucide-react';

export default function NewConversationButton({ onClick, disabled }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="w-full flex items-center justify-center gap-2 py-3 px-4 bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 disabled:opacity-50 text-white rounded-lg text-sm font-semibold transition duration-150 shadow-2xs shrink-0 cursor-pointer disabled:cursor-not-allowed border-0 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-slate-900"
    >
      <Plus size={16} />
      New Chat
    </button>
  );
}
