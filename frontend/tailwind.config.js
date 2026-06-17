/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        surface: '#18181B',
        border: '#27272A',
        primary: '#FAFAFA',
        secondary: '#A1A1AA',
        accent: {
          green: '#22C55E',
          red: '#EF4444',
          indigo: '#6366F1',
        },
      },
      borderRadius: {
        DEFAULT: '8px',
      },
    },
  },
  plugins: [],
};
