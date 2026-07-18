export default function Badge({ children, variant = 'primary', className = '' }) {
  const baseStyle = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold tracking-wide';
  
  const variants = {
    primary: 'bg-slate-100 text-slate-800 border border-slate-200',
    secondary: 'bg-slate-800 text-white border border-transparent',
    success: 'bg-emerald-50 text-emerald-700 border border-emerald-200',
  };

  return (
    <span className={`${baseStyle} ${variants[variant]} ${className}`}>
      {children}
    </span>
  );
}
