import React from 'react';
import { ZoomIn, ZoomOut, RefreshCw, Download, X } from 'lucide-react';
import PdfPageNavigator from './PdfPageNavigator';

export default function PdfToolbar({
  page,
  numPages,
  onPageChange,
  scale,
  onZoomIn,
  onZoomOut,
  onZoomReset,
  onDownload,
  onClose,
  title,
}) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 p-3 bg-white border-b border-slate-200 select-none shrink-0 shadow-2xs">
      {/* Title */}
      <div className="min-w-0 flex-1 max-w-[180px] sm:max-w-xs">
        <h2 className="text-sm font-bold text-slate-800 truncate" title={title}>
          {title}
        </h2>
      </div>

      {/* Page Navigator & Zoom Controls */}
      <div className="flex items-center gap-2">
        <PdfPageNavigator page={page} numPages={numPages} onPageChange={onPageChange} />

        {/* Zoom controls */}
        <div className="flex items-center gap-0.5 bg-slate-50 border border-slate-200 rounded-lg p-1">
          <button
            onClick={onZoomOut}
            disabled={scale <= 0.5}
            className="p-1 hover:bg-slate-200 disabled:opacity-40 disabled:hover:bg-transparent rounded-md text-slate-600 transition cursor-pointer disabled:cursor-not-allowed focus:outline-none"
            title="Zoom out"
            aria-label="Zoom out"
          >
            <ZoomOut size={16} />
          </button>
          
          <span className="text-[10px] font-bold text-slate-500 w-10 text-center">
            {Math.round(scale * 100)}%
          </span>

          <button
            onClick={onZoomIn}
            disabled={scale >= 3.0}
            className="p-1 hover:bg-slate-200 disabled:opacity-40 disabled:hover:bg-transparent rounded-md text-slate-600 transition cursor-pointer disabled:cursor-not-allowed focus:outline-none"
            title="Zoom in"
            aria-label="Zoom in"
          >
            <ZoomIn size={16} />
          </button>

          <button
            onClick={onZoomReset}
            disabled={scale === 1.0}
            className="p-1 hover:bg-slate-200 disabled:opacity-40 disabled:hover:bg-transparent rounded-md text-slate-600 transition cursor-pointer disabled:cursor-not-allowed focus:outline-none"
            title="Reset zoom"
            aria-label="Reset zoom"
          >
            <RefreshCw size={14} />
          </button>
        </div>
      </div>

      {/* Actions (Download & Close) */}
      <div className="flex items-center gap-1.5 ml-auto">
        {onDownload && (
          <button
            onClick={onDownload}
            className="p-1.5 hover:bg-slate-100 border border-slate-200 hover:border-slate-300 rounded-lg text-slate-600 hover:text-slate-800 transition cursor-pointer shadow-3xs focus:outline-none"
            title="Download original PDF"
            aria-label="Download original PDF"
          >
            <Download size={16} />
          </button>
        )}

        <button
          onClick={onClose}
          className="p-1.5 hover:bg-rose-50 border border-slate-200 hover:border-rose-200 rounded-lg text-slate-600 hover:text-rose-600 transition cursor-pointer shadow-3xs focus:outline-none"
          title="Close viewer"
          aria-label="Close viewer"
        >
          <X size={16} />
        </button>
      </div>
    </div>
  );
}
