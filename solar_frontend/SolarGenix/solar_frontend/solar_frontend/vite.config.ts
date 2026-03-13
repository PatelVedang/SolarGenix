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
        target: "http://localhost:5000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/auth-api/, ""),
      },
      "/prediction-api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/prediction-api/, ""),
      },
    },
    allowedHosts: [
      "marcy-confirmable-bunny.ngrok-free.dev"
    ]
  }
});