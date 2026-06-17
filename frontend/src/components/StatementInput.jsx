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
    <div className="border-t border-border bg-[#09090B] pt-4 pb-6">
      <div className="flex items-end gap-3">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="What's your World Cup take?"
            disabled={disabled}
            rows={2}
            className={`w-full bg-surface border ${
              overLimit ? 'border-accent-red' : 'border-border'
            } rounded px-4 py-3 text-sm text-primary placeholder-secondary resize-none outline-none transition-colors duration-150 focus:border-accent-indigo disabled:opacity-50`}
          />
          <div className="flex justify-between items-center mt-1.5">
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
              className="text-xs text-accent-red mt-1"
            >
              {error.message}
            </motion.p>
          )}
        </div>
        <motion.button
          whileTap={disabled ? undefined : { scale: 0.97 }}
          onClick={handleSubmit}
          disabled={disabled || !text.trim() || overLimit}
          className="shrink-0 h-[42px] px-5 bg-accent-indigo text-white text-sm font-medium rounded transition-colors duration-150 hover:bg-[#5558E6] disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Send
        </motion.button>
      </div>
    </div>
  );
}
