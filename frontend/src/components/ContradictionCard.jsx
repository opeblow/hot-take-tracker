import { formatDistanceToNow } from 'date-fns';
import { motion } from 'framer-motion';

export default function ContradictionCard({ contradictedOpinion }) {
  if (!contradictedOpinion) return null;

  const pastDate = contradictedOpinion.timestamp;
  const relativeDate = formatDistanceToNow(new Date(pastDate), { addSuffix: true });

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, ease: [0.34, 1.56, 0.64, 1] }}
      className="glass rounded-xl p-5 space-y-3 gradient-border"
    >
      <div className="flex items-center gap-2">
        <span className="w-1.5 h-1.5 rounded-full bg-accent-red animate-pulse" />
        <span className="text-[11px] font-semibold tracking-widest text-accent-red uppercase">
          Contradiction caught
        </span>
      </div>

      <div className="space-y-1.5">
        <div className="text-xs text-secondary/70" title={pastDate}>
          Said {relativeDate}:
        </div>
        <blockquote className="text-sm text-secondary border-l-2 border-glass-border pl-3 italic leading-relaxed">
          &ldquo;{contradictedOpinion.statement}&rdquo;
        </blockquote>
      </div>

      <div className="flex items-center gap-2 text-xs text-secondary">
        <div className="h-px flex-1 bg-glass-border" />
        <span>now says</span>
        <div className="h-px flex-1 bg-glass-border" />
      </div>

      <div className="space-y-1.5">
        <div className="text-xs text-secondary/70">Today:</div>
        <div className="text-sm text-primary font-medium">
          (new statement above)
        </div>
      </div>
    </motion.div>
  );
}
