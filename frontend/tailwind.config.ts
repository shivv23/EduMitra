import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#fef7ee",
          100: "#fdedd3",
          200: "#f9d7a5",
          300: "#f5ba6d",
          400: "#f09333",
          500: "#ec7a12",
          600: "#dd5f08",
          700: "#b74609",
          800: "#92380f",
          900: "#763010",
          950: "#401606",
        },
        accent: {
          50: "#eefbf0",
          100: "#d5f5d9",
          200: "#adeab6",
          300: "#73d985",
          400: "#3ec15a",
          500: "#1aa53e",
          600: "#0f8530",
          700: "#106a29",
          800: "#125424",
          900: "#10451f",
          950: "#062610",
        },
        surface: {
          50: "#f6f7f9",
          100: "#eceef2",
          200: "#d5d9e3",
          300: "#b1b9cb",
          400: "#8895af",
          500: "#6a7894",
          600: "#55607a",
          700: "#464f63",
          800: "#3c4354",
          900: "#2d3340",
          950: "#0f1117",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
        display: ["Plus Jakarta Sans", "Inter", "system-ui", "sans-serif"],
      },
      animation: {
        "fade-in": "fadeIn 0.5s ease-out",
        "slide-up": "slideUp 0.5s ease-out",
        "slide-in-right": "slideInRight 0.3s ease-out",
        "pulse-soft": "pulseSoft 2s infinite",
        shimmer: "shimmer 2s infinite linear",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(20px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        slideInRight: {
          "0%": { opacity: "0", transform: "translateX(20px)" },
          "100%": { opacity: "1", transform: "translateX(0)" },
        },
        pulseSoft: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.7" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic": "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
      },
    },
  },
  plugins: [],
};

export default config;
