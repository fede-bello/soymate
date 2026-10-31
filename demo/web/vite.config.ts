import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In dev without the mock, /api is proxied to the FastAPI server (override with API_PROXY).
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: { "/api": { target: process.env.API_PROXY ?? "http://localhost:8000", changeOrigin: true } },
  },
  build: { target: "es2020", assetsInlineLimit: 4096 },
});
