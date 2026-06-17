import { motion } from 'framer-motion';

const variants = {
  primary:
    'bg-accent-gradient text-white hover:bg-accent-gradient-hover disabled:opacity-30 disabled:cursor-not-allowed shadow-glow',
  ghost:
    'glass text-secondary hover:text-primary glass-hover disabled:opacity-30 disabled:cursor-not-allowed',
};

export default function Button({ children, variant = 'primary', onClick, disabled, className = '', ...props }) {
  return (
    <motion.button
      whileTap={disabled ? undefined : { scale: 0.97 }}
      onClick={onClick}
      disabled={disabled}
      className={`inline-flex items-center justify-center px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </motion.button>
  );
}
