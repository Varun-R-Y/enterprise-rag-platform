import React from 'react';
import { AlertCircle, RotateCcw } from 'lucide-react';
import Button from '../ui/Button';

export default function PdfError({ message, onRetry }) {
  return (
    <div className="flex flex-col items-center justify-center h-full w-full py-16 px-6 bg-rose-50/30 rounded-xl border border-dashed border-rose-200 text-center animate-in fade-in duration-200">
      <div className="p-3 bg-rose-100/80 text-rose-600 rounded-full mb-4 border border-rose-200/50">
        <AlertCircle size={28} />
      </div>
      <h4 className="text-sm font-bold text-slate-800 mb-1">Failed to load document</h4>
      <p className="text-xs text-slate-500 max-w-xs leading-relaxed mb-6">
        {message || 'An error occurred while loading this PDF. Please verify your connection or try again.'}
      </p>
      {onRetry && (
        <Button
          onClick={onRetry}
          variant="secondary"
          className="h-9 px-4 text-xs font-semibold flex items-center justify-center gap-1.5 cursor-pointer"
        >
          <RotateCcw size={13} />
          Try Again
        </Button>
      )}
    </div>
  );
}
