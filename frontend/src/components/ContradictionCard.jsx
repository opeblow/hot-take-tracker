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
      className="border border-accent-red/30 rounded p-4 bg-accent-red/5 space-y-3"
    >
      <div className="text-xs font-semibold tracking-wider text-accent-red uppercase">
        Contradiction
      </div>

      <div className="space-y-1">
        <div className="text-xs text-secondary" title={pastDate}>
          Said {relativeDate}:
        </div>
        <blockquote className="text-sm text-secondary border-l-2 border-border pl-3 italic leading-relaxed">
          &ldquo;{contradictedOpinion.statement}&rdquo;
        </blockquote>
      </div>

      <div className="flex items-center gap-2 text-xs text-secondary">
        <div className="h-px flex-1 bg-border" />
        <span>now says</span>
        <div className="h-px flex-1 bg-border" />
      </div>

      <div className="space-y-1">
        <div className="text-xs text-secondary">Today:</div>
        <div className="text-sm text-primary font-medium">
          (new statement above)
        </div>
      </div>
    </motion.div>
  );
}
