export default function SectionHeading({ title, subtitle, className = '' }) {
  return (
    <div className={`text-center max-w-2xl mx-auto mb-16 ${className}`}>
      <h2 className="text-3xl md:text-4xl font-bold tracking-tight text-slate-900 mb-4">
        {title}
      </h2>
      {subtitle && (
        <p className="text-slate-600 text-[16px] leading-[1.6]">
          {subtitle}
        </p>
      )}
    </div>
  );
}
