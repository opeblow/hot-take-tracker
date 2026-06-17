import { motion, AnimatePresence } from 'framer-motion';

export default function ErrorBanner({ error, onDismiss }) {
  return (
    <AnimatePresence>
      {error && (
        <motion.div
          initial={{ y: -40, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: -40, opacity: 0 }}
          transition={{ type: 'spring', stiffness: 400, damping: 30 }}
          className="flex items-center justify-between gap-4 px-4 py-3 bg-accent-red/10 border border-accent-red/30 rounded text-sm text-accent-red"
        >
          <span className="flex-1">{error.message}</span>
          <button
            onClick={onDismiss}
            className="text-secondary hover:text-primary transition-colors shrink-0"
            aria-label="Dismiss error"
          >
            &times;
          </button>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
