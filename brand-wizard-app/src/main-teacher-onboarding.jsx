import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import TeacherOnboarding from "./components/teacher-onboarding/TeacherOnboarding.jsx";
import { TeacherOnboardingI18nProvider } from "./i18n-teacher-onboarding.jsx";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <TeacherOnboardingI18nProvider>
      <TeacherOnboarding />
    </TeacherOnboardingI18nProvider>
  </StrictMode>
);
