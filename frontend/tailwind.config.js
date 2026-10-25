/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: {
          DEFAULT: '#FAF6ED',      // Warm Ivory
          contrast: '#292444',     // Deep Navy Outer Framing
        },
        surface: {
          DEFAULT: '#FFFFFF',      // White Content Surfaces
          subtle: '#F5EFE3',       // Warm Ivory Pill / Subtle Surface
        },
        border: {
          DEFAULT: '#E8E0D2',      // Subtle Warm Border
          hover: '#D5CBBA',        // Interactive Border
        },
        brand: {
          coral: '#FF5B3D',        // Primary Action Coral
          'coral-hover': '#E8482A',
          'coral-active': '#D13B1F',
          navy: '#292444',         // Deep Navy Brand Text
        },
        text: {
          primary: '#292444',
          secondary: '#5E5875',
          muted: '#8E879E',
        },
        status: {
          success: '#15803D',
          warning: '#B45309',
          error: '#B91C1C',
        }
      },
      fontFamily: {
        display: ['Plus Jakarta Sans', 'Inter', 'system-ui', 'sans-serif'],
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      borderRadius: {
        'pill': '9999px',
        '2xl': '18px',
        '3xl': '24px',
      },
      boxShadow: {
        'warm': '0 4px 20px -2px rgba(41, 36, 68, 0.05)',
        'warm-lg': '0 10px 30px -4px rgba(41, 36, 68, 0.08)',
      }
    },
  },
  plugins: [],
};
