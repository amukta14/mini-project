/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        navy: '#0A192F',
        rust: '#C75B12',
        ink: '#E9EEF6',
        mist: '#9FB3C8',
        line: 'rgba(159, 179, 200, 0.18)',
      },
      fontFamily: {
        sans: ['Poppins', 'Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        glow: '0 24px 60px rgba(199, 91, 18, 0.18)',
        panel: '0 20px 55px rgba(4, 11, 24, 0.42)',
      },
      backgroundImage: {
        'hero-gradient':
          'radial-gradient(circle at top left, rgba(199, 91, 18, 0.18), transparent 30%), radial-gradient(circle at top right, rgba(59, 130, 246, 0.12), transparent 24%), linear-gradient(145deg, #081220 0%, #0A192F 50%, #10233F 100%)',
      },
      animation: {
        float: 'float 10s ease-in-out infinite',
        pulseSoft: 'pulseSoft 2.8s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-12px)' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '0.45', transform: 'scale(0.98)' },
          '50%': { opacity: '0.9', transform: 'scale(1.02)' },
        },
      },
    },
  },
  plugins: [],
}
