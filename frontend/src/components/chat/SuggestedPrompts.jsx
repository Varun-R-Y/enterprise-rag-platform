import { Compass } from 'lucide-react';

export default function SuggestedPrompts({ onSelect }) {
  const prompts = [
    'Summarize the uploaded documents.',
    'Explain the leave policy.',
    'Compare the HR and Finance manuals.',
    'List important security guidelines.',
    'What reimbursement policies exist?',
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-2xl w-full">
      {prompts.map((prompt, idx) => (
        <button
          key={idx}
          onClick={() => onSelect(prompt)}
          className="text-left p-3.5 bg-white border border-slate-200 hover:border-indigo-400 rounded-lg hover:shadow-xs active:bg-slate-50 transition duration-150 text-xs font-semibold text-slate-700 cursor-pointer flex items-start gap-2.5 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          <Compass size={14} className="text-indigo-500 shrink-0 mt-0.5" />
          <span>{prompt}</span>
        </button>
      ))}
    </div>
  );
}
