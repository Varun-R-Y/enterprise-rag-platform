export default function Card({ children, className = '' }) {
  return (
    <div className={`bg-white border border-slate-200 rounded-xl shadow-sm p-6 ${className}`}>
      {children}
    </div>
  );
}
