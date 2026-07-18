import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export default function MessageBubble({ isUser, text }) {
  if (isUser) {
    return (
      <div className="text-sm leading-relaxed whitespace-pre-wrap select-text text-white">
        {text}
      </div>
    );
  }

  // Styling custom components for ReactMarkdown to integrate beautifully with Tailwind
  const markdownComponents = {
    h1: ({ children }) => <h1 className="text-lg font-bold text-slate-800 mb-2 mt-4 first:mt-0">{children}</h1>,
    h2: ({ children }) => <h2 className="text-md font-bold text-slate-800 mb-2 mt-3 first:mt-0">{children}</h2>,
    h3: ({ children }) => <h3 className="text-sm font-bold text-slate-800 mb-2 mt-2 first:mt-0">{children}</h3>,
    p: ({ children }) => <p className="mb-3 leading-relaxed last:mb-0 text-slate-700 text-sm">{children}</p>,
    strong: ({ children }) => <strong className="font-semibold text-slate-900">{children}</strong>,
    em: ({ children }) => <em className="italic text-slate-800">{children}</em>,
    a: ({ href, children }) => (
      <a href={href} target="_blank" rel="noopener noreferrer" className="text-indigo-600 font-semibold underline hover:text-indigo-500">
        {children}
      </a>
    ),
    ul: ({ children }) => <ul className="list-disc pl-5 mb-3 space-y-1 text-slate-700 text-sm">{children}</ul>,
    ol: ({ children }) => <ol className="list-decimal pl-5 mb-3 space-y-1 text-slate-700 text-sm">{children}</ol>,
    li: ({ children }) => <li className="mb-0.5 last:mb-0">{children}</li>,
    code: ({ inline, className, children }) => {
      const isInline = !className;
      if (isInline) {
        return (
          <code className="text-indigo-600 bg-indigo-50/70 font-semibold px-1 py-0.5 rounded text-xs font-mono">
            {children}
          </code>
        );
      }
      return (
        <code className="block text-xs font-mono text-slate-100 p-4 bg-slate-800 rounded-lg overflow-x-auto my-3 leading-normal border border-slate-700">
          {children}
        </code>
      );
    },
    table: ({ children }) => (
      <div className="overflow-x-auto mb-4 border border-slate-200 rounded-lg shadow-2xs">
        <table className="min-w-full divide-y divide-slate-200 text-sm">{children}</table>
      </div>
    ),
    thead: ({ children }) => <thead className="bg-slate-50">{children}</thead>,
    tbody: ({ children }) => <tbody className="divide-y divide-slate-100 bg-white">{children}</tbody>,
    tr: ({ children }) => <tr>{children}</tr>,
    th: ({ children }) => <th className="px-4 py-2 text-left font-bold text-slate-700 border-b border-slate-200">{children}</th>,
    td: ({ children }) => <td className="px-4 py-2 text-slate-600 border-b border-slate-100">{children}</td>,
  };

  return (
    <div className="select-text">
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
        {text}
      </ReactMarkdown>
    </div>
  );
}
