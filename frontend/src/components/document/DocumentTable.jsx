import { useState, useRef, useEffect } from 'react';
import { MoreVertical, Trash2, Eye, Download, RefreshCw } from 'lucide-react';
import DocumentRow from './DocumentRow';
import StatusBadge from './StatusBadge';
import Card from '../ui/Card';

export default function DocumentTable({ documents, searchTerm, sortBy, onDeleteClick, onRetryClick }) {
  const [activeMenuId, setActiveMenuId] = useState(null);
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

  // Close menus on click outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setActiveMenuId(null);
      }
    };
    if (activeMenuId) {
      window.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      window.removeEventListener('mousedown', handleClickOutside);
    };
  }, [activeMenuId]);

  // Filter and Sort documents
  const filteredAndSorted = documents
    .filter((doc) =>
      doc.original_filename.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => {
      switch (sortBy) {
        case 'oldest':
          return new Date(a.uploaded_at || a.created_at) - new Date(b.uploaded_at || b.created_at);
        case 'name-az':
          return a.original_filename.localeCompare(b.original_filename);
        case 'name-za':
          return b.original_filename.localeCompare(a.original_filename);
        case 'status':
          return (a.status || '').localeCompare(b.status || '');
        case 'newest':
        default:
          return new Date(b.uploaded_at || b.created_at) - new Date(a.uploaded_at || a.created_at);
      }
    });

  if (filteredAndSorted.length === 0) {
    return (
      <div className="text-center py-12 bg-white border border-slate-200 rounded-xl">
        <p className="text-slate-500 font-medium">No documents match your search criteria.</p>
      </div>
    );
  }

  return (
    <div>
      {/* Desktop/Tablet Table Layout */}
      <div className="hidden md:block overflow-hidden bg-white border border-slate-200 rounded-xl shadow-xs">
        <table className="min-w-full border-collapse text-left">
          <thead>
            <tr className="bg-slate-50 text-slate-400 font-semibold text-xs tracking-wider uppercase border-b border-slate-100">
              <th className="px-6 py-4">Filename</th>
              <th className="px-6 py-4">Status</th>
              <th className="px-6 py-4">Chunks</th>
              <th className="px-6 py-4">Uploaded At</th>
              <th className="px-6 py-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {filteredAndSorted.map((doc) => (
              <DocumentRow
                key={doc.id}
                document={doc}
                onDeleteClick={onDeleteClick}
                onRetryClick={onRetryClick}
              />
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile Stacked Card Layout */}
      <div className="grid grid-cols-1 gap-4 md:hidden">
        {filteredAndSorted.map((doc) => {
          const isFailed = doc.status?.toLowerCase() === 'failed';
          const isMenuOpen = activeMenuId === doc.id;

          return (
            <Card key={doc.id} className="relative bg-white border border-slate-200 rounded-lg p-5 shadow-xs flex flex-col gap-3">
              <div className="flex items-start justify-between gap-2">
                <div className="flex-grow min-w-0">
                  <h4 className="font-semibold text-slate-800 break-all text-sm leading-tight pr-6">
                    {doc.original_filename}
                  </h4>
                  <div className="text-xs text-slate-400 font-medium mt-1">
                    {formatFileSize(doc.file_size)} • {doc.chunk_count || 0} Chunks
                  </div>
                </div>

                {/* Mobile Actions Button */}
                <div className="absolute right-3 top-3">
                  <button
                    onClick={() => setActiveMenuId(isMenuOpen ? null : doc.id)}
                    className="p-1 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-md transition cursor-pointer"
                    aria-label="Actions menu"
                  >
                    <MoreVertical size={16} />
                  </button>

                  {isMenuOpen && (
                    <div
                      ref={menuRef}
                      className="absolute right-0 mt-1 w-44 rounded-lg bg-white shadow-lg border border-slate-200 py-1 z-20"
                    >
                      <button
                        disabled
                        className="w-full text-left px-3 py-1.5 text-xs text-slate-400 flex items-center gap-2 cursor-not-allowed hover:bg-slate-50/50"
                      >
                        <Eye size={12} />
                        View Details
                      </button>
                      <button
                        disabled
                        className="w-full text-left px-3 py-1.5 text-xs text-slate-400 flex items-center gap-2 cursor-not-allowed hover:bg-slate-50/50"
                      >
                        <Download size={12} />
                        Download Original
                      </button>
                      <button
                        disabled
                        className="w-full text-left px-3 py-1.5 text-xs text-slate-400 flex items-center gap-2 cursor-not-allowed hover:bg-slate-50/50"
                      >
                        <RefreshCw size={12} />
                        Reindex
                      </button>
                      <hr className="border-slate-100 my-1" />
                      <button
                        onClick={() => {
                          setActiveMenuId(null);
                          onDeleteClick(doc);
                        }}
                        className="w-full text-left px-3 py-1.5 text-xs text-rose-600 hover:bg-rose-50 flex items-center gap-2 cursor-pointer transition font-medium"
                      >
                        <Trash2 size={12} />
                        Delete
                      </button>
                    </div>
                  )}
                </div>
              </div>

              {/* Status & Date block for mobile */}
              <div className="flex flex-wrap items-center justify-between gap-2 border-t border-slate-100 pt-3 mt-1">
                <div className="flex items-center gap-1.5">
                  <StatusBadge status={doc.status} />
                  {isFailed && (
                    <button
                      onClick={() => onRetryClick?.(doc)}
                      className="text-xs text-indigo-600 hover:text-indigo-500 font-bold flex items-center gap-0.5 ml-1 cursor-pointer"
                      disabled
                    >
                      <RefreshCw size={10} />
                      Retry
                    </button>
                  )}
                </div>
                <div className="text-xs text-slate-500 font-medium">
                  {formatDate(doc.uploaded_at)}
                </div>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
