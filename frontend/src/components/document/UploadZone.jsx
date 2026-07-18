import { useState, useRef } from 'react';
import { UploadCloud } from 'lucide-react';

export default function UploadZone({ onFilesSelect, onError }) {
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const maxUploadSizeMb = Number(import.meta.env.VITE_MAX_UPLOAD_SIZE_MB || 10);
  const maxBytes = maxUploadSizeMb * 1024 * 1024;

  const validateAndProcessFiles = (fileList) => {
    const files = Array.from(fileList);
    const validFiles = [];
    const errors = [];

    files.forEach((file) => {
      if (!file.name.toLowerCase().endsWith('.pdf') && file.type !== 'application/pdf') {
        errors.push(`"${file.name}" is not a PDF file.`);
      } else if (file.size <= 0) {
        errors.push(`"${file.name}" is empty.`);
      } else if (file.size > maxBytes) {
        errors.push(`"${file.name}" exceeds the maximum limit of ${maxUploadSizeMb} MB.`);
      } else {
        validFiles.push(file);
      }
    });

    if (errors.length > 0) {
      onError(errors.join(' '));
    }

    if (validFiles.length > 0) {
      onFilesSelect(validFiles);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndProcessFiles(e.dataTransfer.files);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files.length > 0) {
      validateAndProcessFiles(e.target.files);
      // Reset input value so same file can be selected again
      e.target.value = '';
    }
  };

  const onButtonClick = () => {
    fileInputRef.current.click();
  };

  return (
    <div
      onDragEnter={handleDrag}
      onDragOver={handleDrag}
      onDragLeave={handleDrag}
      onDrop={handleDrop}
      className={`relative flex flex-col items-center justify-center p-8 border-2 border-dashed rounded-xl transition-all duration-200 text-center ${
        dragActive
          ? 'border-indigo-600 bg-indigo-50/30'
          : 'border-slate-300 hover:border-indigo-400 bg-white hover:bg-slate-50/30'
      }`}
    >
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept=".pdf,application/pdf"
        onChange={handleChange}
        className="hidden"
        id="pdf-file-upload"
      />

      <div className="p-3 bg-indigo-50 text-indigo-600 rounded-full mb-3 shrink-0">
        <UploadCloud size={28} />
      </div>

      <p className="text-sm font-semibold text-slate-800 mb-1">
        Drag & drop your PDFs here, or{' '}
        <button
          type="button"
          onClick={onButtonClick}
          className="text-indigo-600 hover:text-indigo-500 font-bold hover:underline focus:outline-none cursor-pointer"
        >
          browse files
        </button>
      </p>
      
      <p className="text-xs text-slate-500">
        Accepts PDF documents up to {maxUploadSizeMb} MB
      </p>
    </div>
  );
}
