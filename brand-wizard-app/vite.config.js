import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": resolve(__dirname, "src"),
    },
  },
  build: {
    rollupOptions: {
      input: {
        wizard: resolve(__dirname, "wizard.html"),
        "wizard-ja": resolve(__dirname, "wizard-ja.html"),
        "wizard-zh": resolve(__dirname, "wizard-zh.html"),
        "wizard-tw": resolve(__dirname, "wizard-tw.html"),
        onboarding: resolve(__dirname, "onboarding.html"),
      },
    },
  },
});
