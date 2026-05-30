import clsx from 'clsx';

const variants = {
  primary: 'badge-primary',
  success: 'badge-success',
  warning: 'badge-warning',
  danger: 'badge-danger',
  slate: 'badge-slate',
};

export default function Badge({ children, variant = 'slate', className }) {
  return <span className={clsx(variants[variant], className)}>{children}</span>;
}
