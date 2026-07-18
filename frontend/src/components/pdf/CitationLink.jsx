import React from 'react';
import { ExternalLink } from 'lucide-react';

export default function CitationLink({ documentId, documentName, page, onSelect }) {
  return (
    <button
      onClick={() => onSelect(documentId, documentName, page)}
      className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-800 transition cursor-pointer hover:underline focus:outline-none"
    >
      <span>{documentName} (Page {page})</span>
      <ExternalLink size={12} />
    </button>
  );
}
