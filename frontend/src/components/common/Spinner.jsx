import clsx from 'clsx';

export default function Spinner({ size = 'md', className }) {
  const dim = { sm: 'h-4 w-4', md: 'h-6 w-6', lg: 'h-10 w-10' }[size] || 'h-6 w-6';
  return (
    <div
      className={clsx(
        'inline-block animate-spin rounded-full border-2 border-current border-t-transparent text-primary-600',
        dim,
        className
      )}
      role="status"
      aria-label="Loading"
    />
  );
}
