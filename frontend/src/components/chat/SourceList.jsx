import CitationCard from './CitationCard';

export default function SourceList({ sources, onSelectCitation }) {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="space-y-2 mt-4 pt-3 border-t border-slate-100">
      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
        Retrieved Sources ({sources.length})
      </span>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
        {sources.map((src, idx) => (
          <CitationCard key={idx} source={src} onSelectCitation={onSelectCitation} />
        ))}
      </div>
    </div>
  );
}
