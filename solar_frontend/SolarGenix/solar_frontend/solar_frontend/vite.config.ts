import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  base: "/",
  
  plugins: [
    react(),
    tailwindcss()
  ],

  server: {
    host: "127.0.0.1",
    port: 5173,
    proxy: {
      "/auth-api": {
        target: process.env.VITE_AUTH_API_URL || "https://solargenix.onrender.com",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/auth-api/, ""),
      },
      "/prediction-api": {
        target: process.env.VITE_PREDICTION_API_URL || "https://vedang2004-prediction-api.hf.space",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/prediction-api/, ""),
      },
    },
    allowedHosts: [
      "marcy-confirmable-bunny.ngrok-free.dev"
    ]
  }
});