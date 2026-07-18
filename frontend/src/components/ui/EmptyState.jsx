import Card from './Card';
import Button from './Button';
import { FileUp, FileText, Cpu, Database, Search } from 'lucide-react';

export default function EmptyState({ onAction, actionLabel, title, description }) {
  const steps = [
    { icon: <FileText size={16} className="text-indigo-500" />, text: 'Extract layout-aware page text' },
    { icon: <Cpu size={16} className="text-indigo-500" />, text: 'Generate dense vector representations' },
    { icon: <Database size={16} className="text-indigo-500" />, text: 'Store isolated embeddings in Qdrant' },
    { icon: <Search size={16} className="text-indigo-500" />, text: 'Ground the system for semantic search & retrieval' },
  ];

  return (
    <Card className="flex flex-col items-center justify-center text-center py-12 px-6 border-dashed border-2 border-slate-200 bg-slate-50/50 max-w-2xl mx-auto my-8">
      <div className="p-4 bg-indigo-50 text-indigo-600 rounded-full mb-4">
        <FileUp size={32} />
      </div>
      <h3 className="text-lg font-semibold text-slate-800 mb-1">{title}</h3>
      <p className="text-sm text-slate-500 max-w-sm mb-6">{description}</p>
      
      {/* Workflow checklist */}
      <div className="w-full max-w-md bg-white rounded-lg border border-slate-100 p-4 text-left mb-8 shadow-xs">
        <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-3 text-center md:text-left">
          RAG Pipeline Processing Steps
        </span>
        <ul className="space-y-2.5">
          {steps.map((step, idx) => (
            <li key={idx} className="flex items-center gap-3 text-sm text-slate-600">
              <span className="p-1 bg-indigo-50 rounded-md shrink-0">{step.icon}</span>
              <span>{step.text}</span>
            </li>
          ))}
        </ul>
      </div>

      {onAction && actionLabel && (
        <Button onClick={onAction} variant="primary">
          {actionLabel}
        </Button>
      )}
    </Card>
  );
}
