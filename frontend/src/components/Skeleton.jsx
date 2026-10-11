export function Skeleton({ h = 16, w = '100%', r }) {
  return <div className="skeleton" style={{ height: h, width: w, borderRadius: r }} aria-hidden="true" />;
}

export function CardSkeleton({ lines = 3, h = 120 }) {
  return (
    <div className="card col" aria-busy="true" aria-label="Loading">
      <Skeleton h={18} w="40%" />
      {Array.from({ length: lines }).map((_, i) => <Skeleton key={i} h={i === 0 ? h : 14} w={i === 0 ? '100%' : `${80 - i * 15}%`} />)}
    </div>
  );
}
