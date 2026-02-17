import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--bg)",
        foreground: "var(--text-primary)",
        card: "var(--panel)",
        "card-foreground": "var(--text-primary)",
        muted: "var(--panel-2)",
        "muted-foreground": "var(--text-muted)",
        border: "var(--border)",
        primary: "var(--accent)",
      },
      borderRadius: {
        sm: "var(--radius-sm)",
        md: "var(--radius-md)",
      },
    },
  },
  plugins: [],
};

export default config;
