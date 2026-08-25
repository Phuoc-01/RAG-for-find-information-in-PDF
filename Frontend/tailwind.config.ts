import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        paper: "#FAF9F6",
        ink: "#1F2320",
        moss: {
          50: "#F1F5F1",
          100: "#DDE7DD",
          300: "#9DBBA0",
          500: "#4C7A57",
          600: "#3C6246",
          700: "#2F4D38",
        },
        line: "#E4E1D9",
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        serif: ["var(--font-source-serif)", "Georgia", "serif"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(31,35,32,0.04), 0 1px 8px rgba(31,35,32,0.03)",
      },
    },
  },
  plugins: [],
};
export default config;
