import SuggestedPrompts from './SuggestedPrompts';
import { Layers } from 'lucide-react';

export default function EmptyChat({ onSelectPrompt }) {
  return (
    <div className="flex-grow flex flex-col items-center justify-center p-6 text-center max-w-2xl mx-auto h-full">
      <div className="p-4 bg-indigo-50 text-indigo-600 rounded-full mb-4 shadow-2xs border border-indigo-100 shrink-0">
        <Layers size={36} />
      </div>
      <h2 className="text-xl md:text-2xl font-bold text-slate-800 tracking-tight mb-2">
        Enterprise Knowledge Assistant
      </h2>
      <p className="text-sm text-slate-500 max-w-md mb-8 leading-relaxed">
        Ask questions about your uploaded documents using Retrieval-Augmented Generation. Select a suggested prompt below or type your inquiry in the input field.
      </p>
      
      <SuggestedPrompts onSelect={onSelectPrompt} />
    </div>
  );
}
