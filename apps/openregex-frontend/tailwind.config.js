/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
      },
      colors: {
        theme: {
          base: 'var(--theme-base)',
          surface: 'var(--theme-surface)',
          border: 'var(--theme-border)',
          text: 'var(--theme-text)',
          muted: 'var(--theme-muted)',
          primary: 'var(--theme-primary)',
        },
        ide: {
          bg: 'var(--ide-bg)',
          panel: 'var(--ide-panel)',
          border: 'var(--ide-border)',
          text: 'var(--ide-text)',
          dim: 'var(--ide-dim)',
          matchBg: 'var(--ide-matchBg)',
          matchBorder: 'var(--ide-matchBorder)',
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}