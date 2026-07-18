import Card from './Card';

export default function FeatureCard({ title, description, icon: Icon, className = '' }) {
  return (
    <Card className={`flex flex-col h-full ${className}`}>
      {Icon && (
        <div className="text-indigo-600 mb-4 p-2 bg-indigo-50 rounded-lg w-fit">
          <Icon size={24} />
        </div>
      )}
      <h3 className="text-xl font-semibold text-slate-900 mb-2">{title}</h3>
      <p className="text-slate-600 text-[16px] leading-[1.6] flex-grow">{description}</p>
    </Card>
  );
}
