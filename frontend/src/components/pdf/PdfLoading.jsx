import React from 'react';
import Spinner from '../ui/Spinner';

export default function PdfLoading({ message = 'Loading document...' }) {
  return (
    <div className="flex flex-col items-center justify-center h-full w-full py-16 px-4 bg-slate-50/50 rounded-xl border border-dashed border-slate-200">
      <Spinner size="lg" className="text-indigo-600 animate-spin" />
      <span className="mt-4 text-sm font-semibold text-slate-500 animate-pulse">
        {message}
      </span>
    </div>
  );
}
