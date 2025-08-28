import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  base: "/reference-library/", // 👈 IMPORTANT for GitHub Pages
});