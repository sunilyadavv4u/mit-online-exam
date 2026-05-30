import clsx from 'clsx';

export default function EmptyState({ icon: Icon, title, description, action, className }) {
  return (
    <div className={clsx('flex flex-col items-center justify-center text-center py-12', className)}>
      {Icon && (
        <div className="mb-4 rounded-full bg-primary-50 p-4 text-primary-600">
          <Icon className="h-8 w-8" />
        </div>
      )}
      <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
      {description && <p className="mt-1 max-w-sm text-sm text-slate-500">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
