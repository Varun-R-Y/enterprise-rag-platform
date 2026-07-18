import { AlertCircle, CheckCircle, Info } from 'lucide-react';

export default function Alert({ type = 'info', message, onClose, className = '' }) {
  const styles = {
    info: 'bg-indigo-50 text-indigo-800 border-indigo-200',
    success: 'bg-emerald-50 text-emerald-800 border-emerald-200',
    error: 'bg-rose-50 text-rose-800 border-rose-200',
    warning: 'bg-amber-50 text-amber-800 border-amber-200',
  };

  const icons = {
    info: <Info size={18} className="text-indigo-500 shrink-0" />,
    success: <CheckCircle size={18} className="text-emerald-500 shrink-0" />,
    error: <AlertCircle size={18} className="text-rose-500 shrink-0" />,
    warning: <AlertCircle size={18} className="text-amber-500 shrink-0" />,
  };

  return (
    <div className={`flex items-start gap-3 p-4 border rounded-lg text-sm font-medium ${styles[type]} ${className}`} role="alert">
      {icons[type]}
      <div className="flex-grow">{message}</div>
      {onClose && (
        <button onClick={onClose} className="text-slate-400 hover:text-slate-600 transition cursor-pointer font-bold text-lg leading-none" aria-label="Dismiss Alert">
          &times;
        </button>
      )}
    </div>
  );
}
