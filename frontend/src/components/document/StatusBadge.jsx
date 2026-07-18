import Badge from '../ui/Badge';

export default function StatusBadge({ status }) {
  const normalizedStatus = status ? status.toLowerCase() : '';

  const config = {
    pending: { label: 'Pending', variant: 'secondary' },
    processing: { label: 'Processing', variant: 'primary' },
    completed: { label: 'Completed', variant: 'success' },
    failed: { label: 'Failed', className: 'bg-rose-50 text-rose-700 border border-rose-200' },
  };

  const item = config[normalizedStatus] || { label: status || 'Unknown', variant: 'secondary' };

  if (item.variant) {
    return <Badge variant={item.variant}>{item.label}</Badge>;
  }

  return (
    <Badge className={item.className}>
      {item.label}
    </Badge>
  );
}
