import { Link } from 'react-router-dom';
import clsx from 'clsx';

/**
 * MIT logo + institute name. Links to the public home page (/).
 */
export default function InstituteBrand({ collapsed = false, className = '', variant = 'default' }) {
  const onDark = variant === 'onDark';
  return (
    <Link
      to="/"
      className={clsx(
        'flex items-center gap-3 rounded-lg transition hover:opacity-90 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500',
        className,
      )}
      title="Mewati Institute of Technology — Home"
    >
      <div
        className={clsx(
          'flex h-9 w-9 shrink-0 items-center justify-center rounded-lg font-bold text-white',
          onDark ? 'bg-white/20' : 'bg-gradient-to-br from-primary-500 to-primary-700',
        )}
      >
        MIT
      </div>
      {!collapsed && (
        <div>
          <p
            className={clsx(
              'text-sm font-semibold leading-tight',
              onDark ? 'text-white' : 'text-slate-900',
            )}
          >
            Mewati Institute
          </p>
          <p
            className={clsx(
              'text-xs leading-tight',
              onDark ? 'text-primary-100' : 'text-slate-500',
            )}
          >
            of Technology
          </p>
        </div>
      )}
    </Link>
  );
}
