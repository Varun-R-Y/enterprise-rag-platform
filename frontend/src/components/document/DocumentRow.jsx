import { useState, useEffect, useRef } from 'react';
import { MoreVertical, Trash2, Eye, Download, RefreshCw, AlertTriangle } from 'lucide-react';
import StatusBadge from './StatusBadge';

export default function DocumentRow({ document: doc, onDeleteClick, onRetryClick }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef(null);

  const formatFileSize = (bytes) => {
    if (bytes === undefined || bytes === null || bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Close menu on click outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setMenuOpen(false);
      }
    };
    if (menuOpen) {
      window.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      window.removeEventListener('mousedown', handleClickOutside);
    };
  }, [menuOpen]);

  const isFailed = doc.status?.toLowerCase() === 'failed';

  return (
    <tr className="hover:bg-slate-50/50 border-b border-slate-100 last:border-0 transition duration-150 text-slate-700">
      {/* Filename & Size */}
      <td className="px-6 py-4">
        <div className="font-semibold text-slate-800 break-all max-w-xs md:max-w-md" title={doc.original_filename}>
          {doc.original_filename}
        </div>
        <div className="text-xs text-slate-400 font-medium mt-0.5">
          {formatFileSize(doc.file_size || 0)}
        </div>
      </td>

      {/* Status */}
      <td className="px-6 py-4 whitespace-nowrap">
        <div className="flex items-center gap-2">
          <StatusBadge status={doc.status} />
          {isFailed && (
            <button
              onClick={() => onRetryClick?.(doc)}
              className="text-xs text-indigo-600 hover:text-indigo-500 font-bold flex items-center gap-1 ml-1 cursor-pointer focus:outline-none focus:underline"
              title="Indexing retry is coming soon"
              disabled
            >
              <RefreshCw size={12} />
              Retry
            </button>
          )}
        </div>
      </td>

      {/* Pages/Chunks */}
      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500 font-medium">
        {doc.chunk_count !== undefined ? `${doc.chunk_count} Chunks` : '0 Chunks'}
      </td>

      {/* Uploaded At */}
      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500 font-medium">
        {formatDate(doc.uploaded_at)}
      </td>

      {/* Actions */}
      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium relative">
        <div ref={menuRef} className="inline-block text-left">
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="p-1 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-md transition cursor-pointer"
            aria-label="Actions menu"
          >
            <MoreVertical size={18} />
          </button>

          {menuOpen && (
            <div className="absolute right-0 mt-1 w-48 rounded-lg bg-white shadow-lg border border-slate-200 py-1 z-10 animate-in fade-in slide-in-from-top-1 duration-100">
              <button
                disabled
                className="w-full text-left px-4 py-2 text-xs text-slate-400 flex items-center gap-2 cursor-not-allowed hover:bg-slate-50/50"
                title="Future feature"
              >
                <Eye size={14} />
                View Details <span className="text-[9px] bg-slate-100 text-slate-400 px-1 rounded ml-auto">Soon</span>
              </button>
              
              <button
                disabled
                className="w-full text-left px-4 py-2 text-xs text-slate-400 flex items-center gap-2 cursor-not-allowed hover:bg-slate-50/50"
                title="Future feature"
              >
                <Download size={14} />
                Download Original <span className="text-[9px] bg-slate-100 text-slate-400 px-1 rounded ml-auto">Soon</span>
              </button>

              <button
                disabled
                className="w-full text-left px-4 py-2 text-xs text-slate-400 flex items-center gap-2 cursor-not-allowed hover:bg-slate-50/50"
                title="Future feature"
              >
                <RefreshCw size={14} />
                Reindex <span className="text-[9px] bg-slate-100 text-slate-400 px-1 rounded ml-auto">Soon</span>
              </button>

              <hr className="border-slate-100 my-1" />

              <button
                onClick={() => {
                  setMenuOpen(false);
                  onDeleteClick(doc);
                }}
                className="w-full text-left px-4 py-2 text-xs text-rose-600 hover:bg-rose-50 flex items-center gap-2 cursor-pointer transition font-medium"
              >
                <Trash2 size={14} />
                Delete Document
              </button>
            </div>
          )}
        </div>
      </td>
    </tr>
  );
}
