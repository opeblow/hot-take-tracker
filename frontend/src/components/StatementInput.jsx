import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';

const MAX_LENGTH = 500;

export default function StatementInput({ onSubmit, disabled, error }) {
  const [text, setText] = useState('');
  const textareaRef = useRef(null);

  useEffect(() => {
    if (!disabled && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [disabled]);

  const handleSubmit = async () => {
    const trimmed = text.trim();
    if (!trimmed || disabled) return;

    const success = await onSubmit(trimmed);
    if (success) {
      setText('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const overLimit = text.length > MAX_LENGTH;

  return (
    <div className="pt-4 pb-6">
      <div className="glass rounded-xl p-1">
        <div className="flex items-end gap-3 p-3">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={text}
              onChange={(e) => setText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="What's your World Cup take?"
              disabled={disabled}
              rows={2}
              className={`w-full bg-transparent border-0 rounded px-1 py-2 text-sm text-primary placeholder-glass-white resize-none outline-none disabled:opacity-50`}
            />
            <div className="flex justify-between items-center mt-1 px-1">
              <span className="text-xs text-secondary">
                {text.length > 0 && `${text.length}/${MAX_LENGTH}`}
              </span>
              {overLimit && (
                <motion.span
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="text-xs text-accent-red"
                >
                  Over character limit
                </motion.span>
              )}
            </div>
            {error?.type === 'validation' && (
              <motion.p
                initial={{ opacity: 0, y: -4 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-xs text-accent-red mt-1 px-1"
              >
                {error.message}
              </motion.p>
            )}
          </div>
          <motion.button
            whileTap={disabled ? undefined : { scale: 0.97 }}
            onClick={handleSubmit}
            disabled={disabled || !text.trim() || overLimit}
            className="shrink-0 h-[42px] px-5 bg-accent-gradient text-white text-sm font-medium rounded-lg transition-all duration-200 hover:bg-accent-gradient-hover disabled:opacity-30 disabled:cursor-not-allowed shadow-glow"
          >
            Send
          </motion.button>
        </div>
      </div>
    </div>
  );
}
