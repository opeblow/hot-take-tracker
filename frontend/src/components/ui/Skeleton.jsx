export default function Skeleton({ className = '', count = 1 }) {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className={`skeleton-shimmer rounded-xl ${className}`}
          style={{ minHeight: '1rem' }}
        />
      ))}
    </>
  );
}
