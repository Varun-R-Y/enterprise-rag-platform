export default function TechBadge({ category, items = [] }) {
  return (
    <div className="flex flex-col gap-2 p-4 border border-slate-200 rounded-lg bg-white shadow-sm">
      <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{category}</span>
      <div className="flex flex-wrap gap-1.5">
        {items.map((item, idx) => (
          <span key={idx} className="inline-flex items-center px-2.5 py-1 rounded bg-slate-100 text-slate-800 text-sm font-medium">
            {item}
          </span>
        ))}
      </div>
    </div>
  );
}
