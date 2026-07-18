export default function Container({ children, className = '' }) {
  return (
    <div className={`w-full max-w-[1280px] mx-auto px-4 md:px-6 ${className}`}>
      {children}
    </div>
  );
}
