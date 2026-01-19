interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular';
  width?: string | number;
  height?: string | number;
  animation?: 'pulse' | 'wave' | 'none';
}

export function Skeleton({
  className = '',
  variant = 'rectangular',
  width,
  height,
  animation = 'pulse',
}: SkeletonProps) {
  const baseClasses = 'bg-gray-200 rounded';
  const variantClasses = {
    text: 'h-4 rounded',
    circular: 'rounded-full',
    rectangular: 'rounded',
  };
  const animationClasses = {
    pulse: 'animate-pulse',
    wave: 'animate-pulse',
    none: '',
  };

  const style: React.CSSProperties = {};
  if (width) style.width = typeof width === 'number' ? `${width}px` : width;
  if (height) style.height = typeof height === 'number' ? `${height}px` : height;

  return (
    <div
      className={`${baseClasses} ${variantClasses[variant]} ${animationClasses[animation]} ${className}`}
      style={style}
    />
  );
}

export function SkeletonCard() {
  return (
    <div className="bg-white rounded-xl shadow-sm p-6 space-y-4">
      <Skeleton variant="text" width="60%" height={24} />
      <Skeleton variant="rectangular" width="100%" height={100} />
      <div className="flex gap-2">
        <Skeleton variant="text" width="30%" height={20} />
        <Skeleton variant="text" width="30%" height={20} />
        <Skeleton variant="text" width="30%" height={20} />
      </div>
    </div>
  );
}

export function SkeletonTable({ rows = 5 }: { rows?: number }) {
  return (
    <div className="bg-white rounded-xl shadow-sm p-6 space-y-4">
      <Skeleton variant="text" width="40%" height={28} />
      <div className="space-y-3">
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="flex gap-4">
            <Skeleton variant="rectangular" width="30%" height={40} />
            <Skeleton variant="rectangular" width="20%" height={40} />
            <Skeleton variant="rectangular" width="20%" height={40} />
            <Skeleton variant="rectangular" width="20%" height={40} />
          </div>
        ))}
      </div>
    </div>
  );
}
