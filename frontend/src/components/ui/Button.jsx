export default function Button({
  children,
  variant = 'primary',
  className = '',
  ...props
}) {
  const baseStyle = 'inline-flex items-center justify-center h-[48px] px-6 py-3 rounded-lg font-medium text-[16px] transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none';
  
  const variants = {
    primary: 'bg-indigo-600 text-white hover:bg-indigo-500 active:bg-indigo-700 border border-transparent shadow-sm',
    secondary: 'bg-white text-slate-800 border border-slate-300 hover:bg-slate-50 active:bg-slate-100 shadow-sm',
  };

  return (
    <button
      className={`${baseStyle} ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
