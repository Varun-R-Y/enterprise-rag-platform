import React, { useState, useEffect, useRef } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import pdfService from '../../services/pdfService';
import PdfToolbar from './PdfToolbar';
import PdfLoading from './PdfLoading';
import PdfError from './PdfError';

// Configure the worker source using Vite's bundling method
pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs',
  import.meta.url,
).toString();

export default function PdfViewer({ documentId, initialPage = 1, title, onClose }) {
  const [blob, setBlob] = useState(null);
  const [fileUrl, setFileUrl] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [numPages, setNumPages] = useState(null);
  const [page, setPage] = useState(initialPage);
  const [scale, setScale] = useState(1.0);
  const containerRef = useRef(null);

  // Reset page and scale when the document or the cited page changes
  useEffect(() => {
    setPage(initialPage);
    setScale(1.0);
  }, [documentId, initialPage]);

  const loadFile = async (docId, isMounted) => {
    try {
      const fileBlob = await pdfService.getDocumentFile(docId);
      if (isMounted) {
        setBlob(fileBlob);
        const url = URL.createObjectURL(fileBlob);
        setFileUrl((prevUrl) => {
          if (prevUrl) {
            URL.revokeObjectURL(prevUrl);
          }
          return url;
        });
        setLoading(false);
      }
    } catch (err) {
      console.error('Error fetching PDF:', err);
      if (isMounted) {
        setError('Failed to fetch the PDF file from the server. Ensure the document exists and you are authenticated.');
        setLoading(false);
      }
    }
  };

  // Fetch the PDF blob when the document ID changes
  useEffect(() => {
    if (!documentId) return;

    let isMounted = true;
    setLoading(true);
    setError(null);
    setBlob(null);

    loadFile(documentId, isMounted);

    return () => {
      isMounted = false;
    };
  }, [documentId]);

  // Cleanup fileUrl object URL on unmount
  useEffect(() => {
    return () => {
      if (fileUrl) {
        URL.revokeObjectURL(fileUrl);
      }
    };
  }, [fileUrl]);

  const onDocumentLoadSuccess = ({ numPages }) => {
    setNumPages(numPages);
  };

  const onDocumentLoadError = (err) => {
    console.error('Error rendering PDF:', err);
    setError('Failed to render the PDF file. It might be corrupted or in an unsupported format.');
  };

  const handlePageChange = (newPage) => {
    setPage(newPage);
  };

  const handleZoomIn = () => {
    setScale((prev) => Math.min(prev + 0.25, 3.0));
  };

  const handleZoomOut = () => {
    setScale((prev) => Math.max(prev - 0.25, 0.5));
  };

  const handleZoomReset = () => {
    setScale(1.0);
  };

  const handleDownload = () => {
    if (blob) {
      const a = document.createElement('a');
      const url = URL.createObjectURL(blob);
      a.href = url;
      a.download = title || 'document.pdf';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  const handleRetry = () => {
    setLoading(true);
    setError(null);
    loadFile(documentId, true);
  };

  return (
    <div className="flex flex-col h-full bg-slate-100/90 text-slate-800 border-l border-slate-200 min-w-[280px]">
      {/* Toolbar */}
      <PdfToolbar
        page={page}
        numPages={numPages}
        onPageChange={handlePageChange}
        scale={scale}
        onZoomIn={handleZoomIn}
        onZoomOut={handleZoomOut}
        onZoomReset={handleZoomReset}
        onDownload={blob ? handleDownload : null}
        onClose={onClose}
        title={title}
      />

      {/* Main Content Area */}
      <div
        ref={containerRef}
        className="flex-grow overflow-auto p-4 md:p-6 flex items-start justify-center"
      >
        {loading && <PdfLoading message="Downloading PDF from server..." />}

        {error && <PdfError message={error} onRetry={handleRetry} />}

        {!loading && !error && fileUrl && (
          <div className="shadow-lg border border-slate-300 rounded-md bg-white select-none relative max-w-full">
            <Document
              file={fileUrl}
              onLoadSuccess={onDocumentLoadSuccess}
              onLoadError={onDocumentLoadError}
              loading={<PdfLoading message="Rendering document..." />}
              error={<PdfError message="Failed to parse the PDF." />}
            >
              <Page
                pageNumber={page}
                scale={scale}
                renderTextLayer={false}
                renderAnnotationLayer={false}
                loading={<div className="h-[400px] w-[300px] animate-pulse bg-slate-200" />}
              />
            </Document>
          </div>
        )}
      </div>
    </div>
  );
}
