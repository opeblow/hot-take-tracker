export default function Skeleton({ className = '', count = 1 }) {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className={`animate-pulse bg-surface rounded ${className}`}
          style={{ minHeight: '1rem' }}
        />
      ))}
    </>
  );
}
