/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        'sans': ['Source Sans 3', 'system-ui', 'sans-serif'],
      },
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
        spotify: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#1ED760',
          600: '#1ED760',
          700: '#1ED760',
          800: '#1ED760',
          900: '#1ED760',
        },
        youtube: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',
          500: '#FF0033',
          600: '#FF0033',
          700: '#FF0033',
          800: '#FF0033',
          900: '#FF0033',
        },
        gray: {
          50: '#f9fafb',
          100: '#f3f4f6',
          200: '#e5e7eb',
          300: '#d1d5db',
          400: '#9ca3af',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
          800: '#2a2a2a', // Our custom dark surface
          900: '#202020', // Our custom dark background
        },
        // Custom text colors for better dark mode contrast
        'gray-text': {
          100: '#f5f5f5', // Light text for dark mode
          200: '#a3a3a3', // Muted text for dark mode
        }
      }
    },
  },
  plugins: [],
}
