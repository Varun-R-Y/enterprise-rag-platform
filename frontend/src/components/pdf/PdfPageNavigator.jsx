import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

export default function PdfPageNavigator({ page, numPages, onPageChange }) {
  const [inputValue, setInputValue] = useState(String(page));

  useEffect(() => {
    setInputValue(String(page));
  }, [page]);

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
  };

  const submitPage = () => {
    const val = parseInt(inputValue, 10);
    if (!isNaN(val) && val >= 1 && val <= numPages) {
      onPageChange(val);
    } else {
      setInputValue(String(page));
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      submitPage();
    }
  };

  return (
    <div className="flex items-center gap-1 bg-slate-50 border border-slate-200 rounded-lg p-1 shrink-0">
      <button
        onClick={() => onPageChange(page - 1)}
        disabled={page <= 1}
        className="p-1 hover:bg-slate-200 disabled:opacity-40 disabled:hover:bg-transparent rounded-md text-slate-600 transition cursor-pointer disabled:cursor-not-allowed focus:outline-none"
        title="Previous page"
        aria-label="Previous page"
      >
        <ChevronLeft size={16} />
      </button>

      <div className="flex items-center gap-1 text-xs font-semibold text-slate-500 px-1">
        <input
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          onBlur={submitPage}
          onKeyDown={handleKeyDown}
          className="w-10 h-7 text-center bg-white border border-slate-200 rounded-md focus:border-indigo-400 focus:outline-none text-slate-800 font-bold"
          aria-label="Page number"
        />
        <span>/</span>
        <span className="font-bold text-slate-700">{numPages || '--'}</span>
      </div>

      <button
        onClick={() => onPageChange(page + 1)}
        disabled={page >= numPages}
        className="p-1 hover:bg-slate-200 disabled:opacity-40 disabled:hover:bg-transparent rounded-md text-slate-600 transition cursor-pointer disabled:cursor-not-allowed focus:outline-none"
        title="Next page"
        aria-label="Next page"
      >
        <ChevronRight size={16} />
      </button>
    </div>
  );
}
