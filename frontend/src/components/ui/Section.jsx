export default function Section({
  id,
  children,
  bg = 'light',
  className = '',
}) {
  const backgrounds = {
    light: 'bg-white',
    gray: 'bg-slate-50',
  };

  return (
    <section
      id={id}
      className={`py-16 md:py-24 border-b border-slate-100 ${backgrounds[bg]} ${className}`}
    >
      {children}
    </section>
  );
}
