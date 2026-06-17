import { motion } from 'framer-motion';

const variants = {
  primary:
    'bg-accent-indigo text-white hover:bg-[#5558E6] disabled:opacity-40 disabled:cursor-not-allowed',
  ghost:
    'bg-transparent border border-border text-secondary hover:text-primary hover:border-[#3f3f46] disabled:opacity-40 disabled:cursor-not-allowed',
};

export default function Button({ children, variant = 'primary', onClick, disabled, className = '', ...props }) {
  return (
    <motion.button
      whileTap={disabled ? undefined : { scale: 0.97 }}
      onClick={onClick}
      disabled={disabled}
      className={`inline-flex items-center justify-center px-4 py-2 text-sm font-medium rounded transition-colors duration-150 ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </motion.button>
  );
}
