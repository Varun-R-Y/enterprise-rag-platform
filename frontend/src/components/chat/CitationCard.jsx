import { FileText } from 'lucide-react';

export default function CitationCard({ source, onSelectCitation }) {
  // Format score returned from backend (e.g. 0.912 -> 91% relevance)
  const relevance = typeof source.score === 'number'
    ? `${Math.round(source.score * 100)}%`
    : null;

  const handleClick = () => {
    if (onSelectCitation) {
      onSelectCitation(source.document_id, source.document, source.page);
    }
  };

  return (
    <button
      onClick={handleClick}
      type="button"
      className="w-full text-left flex items-start gap-3 p-3 bg-slate-50 border border-slate-200 rounded-lg text-xs hover:border-indigo-300 hover:bg-slate-100/50 hover:shadow-xs active:bg-slate-100 transition duration-150 shadow-2xs cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
    >
      <div className="p-1.5 bg-indigo-50 text-indigo-600 rounded-md shrink-0">
        <FileText size={14} />
      </div>
      <div className="min-w-0 flex-1">
        <div className="font-semibold text-slate-800 truncate" title={source.document}>
          {source.document}
        </div>
        <div className="text-slate-500 mt-0.5 font-medium flex items-center gap-1.5">
          <span>Page {source.page}</span>
          {relevance && (
            <>
              <span className="w-1 h-1 bg-slate-300 rounded-full shrink-0" />
              <span className="text-indigo-600 font-semibold">Relevance: {relevance}</span>
            </>
          )}
        </div>
      </div>
    </button>
  );
}
