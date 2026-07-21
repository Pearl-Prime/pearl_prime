import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "path";

const onboardingSubmitProxy = {
  target: "http://127.0.0.1:8000",
  changeOrigin: true,
  rewrite: (path) => path.replace(/^\/api\/onboarding\/submit$/, "/api/v1/onboarding/submit"),
};

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
        brand_directors: resolve(__dirname, "brand_directors.html"),
        onboarding: resolve(__dirname, "onboarding.html"),
        teacher_onboarding: resolve(__dirname, "teacher_onboarding.html"),
        teacher_operator_queue: resolve(__dirname, "teacher_operator_queue.html"),
      },
    },
  },
  server: {
    proxy: {
      "/api/onboarding/submit": onboardingSubmitProxy,
      // Local teacher-portal v2 mock (node server/teacher_portal_dev_api.mjs)
      "/api/teacher-onboarding": {
        target: process.env.TEACHER_PORTAL_DEV_URL || "http://127.0.0.1:8790",
        changeOrigin: true,
      },
    },
  },
  preview: {
    proxy: {
      "/api/onboarding/submit": onboardingSubmitProxy,
      "/api/teacher-onboarding": {
        target: process.env.TEACHER_PORTAL_DEV_URL || "http://127.0.0.1:8790",
        changeOrigin: true,
      },
    },
  },
});
