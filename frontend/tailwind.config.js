/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        glass: {
          DEFAULT: 'rgba(255,255,255,0.04)',
          hover: 'rgba(255,255,255,0.08)',
          border: 'rgba(255,255,255,0.06)',
          'border-hover': 'rgba(255,255,255,0.12)',
          white: 'rgba(255,255,255,0.5)',
        },
        surface: '#18181B',
        border: '#27272A',
        primary: '#FAFAFA',
        secondary: '#A1A1AA',
        accent: {
          green: '#10B981',
          red: '#F43F5E',
          indigo: '#6366F1',
          violet: '#8B5CF6',
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'accent-gradient': 'linear-gradient(135deg, #6366F1, #8B5CF6)',
        'accent-gradient-hover': 'linear-gradient(135deg, #5558E6, #7C3AED)',
      },
      borderRadius: {
        DEFAULT: '8px',
      },
      boxShadow: {
        glass: '0 0 0 1px rgba(255,255,255,0.06), 0 4px 24px rgba(0,0,0,0.2)',
        'glass-lg': '0 0 0 1px rgba(255,255,255,0.06), 0 8px 40px rgba(0,0,0,0.3)',
        glow: '0 0 20px rgba(99,102,241,0.15)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
};
