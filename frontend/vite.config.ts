import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: true, // escucha en 0.0.0.0, necesario para acceder desde Windows cuando corre en WSL
    port: 5173,
  },
});
