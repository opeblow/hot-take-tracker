import { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { formatDistanceToNow } from 'date-fns';
import Skeleton from './ui/Skeleton.jsx';

export default function ReceiptsPanel({
  open,
  onClose,
  userId,
  contradictions,
  loading,
  fetchContradictions,
}) {
  useEffect(() => {
    if (open && userId) {
      fetchContradictions(userId);
    }
  }, [open, userId, fetchContradictions]);

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
            onClick={onClose}
          />
          <motion.aside
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            className="fixed top-0 right-0 bottom-0 w-full max-w-md z-50 bg-[#07070D] border-l border-glass-border overflow-y-auto scrollbar-thin"
          >
            <div className="sticky top-0 bg-[#07070D]/80 backdrop-blur-xl border-b border-glass-border px-6 py-4 flex items-center justify-between z-10">
              <div className="flex items-center gap-3">
                <h2 className="text-base font-semibold gradient-text">
                  Receipts
                </h2>
                {!loading && contradictions.length > 0 && (
                  <span className="text-[11px] font-medium text-secondary glass rounded-full px-2.5 py-0.5">
                    {contradictions.length}
                  </span>
                )}
              </div>
              <button
                onClick={onClose}
                className="text-secondary hover:text-primary transition-colors text-lg leading-none"
                aria-label="Close panel"
              >
                &times;
              </button>
            </div>

            <div className="px-6 py-5 space-y-4">
              {loading ? (
                <div className="space-y-4">
                  <Skeleton className="h-28 w-full" count={3} />
                </div>
              ) : contradictions.length === 0 ? (
                <div className="text-center py-16">
                  <div className="text-3xl mb-3 opacity-30">🎯</div>
                  <p className="text-sm text-secondary leading-relaxed">
                    No contradictions caught yet. Stay consistent, or don't.
                  </p>
                </div>
              ) : (
                contradictions.map((c, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.03 }}
                    className="glass rounded-xl p-5 space-y-3"
                  >
                    <div className="space-y-1.5">
                      <div className="text-[10px] font-semibold tracking-widest text-accent-red uppercase">
                        Then
                      </div>
                      <blockquote className="text-sm text-secondary border-l-2 border-glass-border pl-3 italic leading-relaxed">
                        &ldquo;{c.old_opinion.statement}&rdquo;
                      </blockquote>
                      <div className="text-[10px] text-secondary/70" title={c.old_opinion.timestamp}>
                        {formatDistanceToNow(new Date(c.old_opinion.timestamp), { addSuffix: true })}
                      </div>
                    </div>

                    <div className="flex items-center gap-2 text-xs text-secondary">
                      <div className="h-px flex-1 bg-glass-border" />
                      <span>Now</span>
                      <div className="h-px flex-1 bg-glass-border" />
                    </div>

                    <div className="space-y-1.5">
                      <blockquote className="text-sm text-primary border-l-2 border-accent-red/60 pl-3 leading-relaxed">
                        &ldquo;{c.new_opinion.statement}&rdquo;
                      </blockquote>
                      <div className="text-[10px] text-secondary/70" title={c.new_opinion.timestamp}>
                        {formatDistanceToNow(new Date(c.new_opinion.timestamp), { addSuffix: true })}
                      </div>
                    </div>
                  </motion.div>
                ))
              )}
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
