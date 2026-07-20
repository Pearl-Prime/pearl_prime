import { describe, it, expect, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import TeacherOnboarding from "./TeacherOnboarding.jsx";
import {
  TeacherOnboardingI18nProvider,
  TEACHER_ONBOARDING_LOCALE_KEY,
  TEACHER_ONBOARDING_LOCALES,
} from "../../i18n-teacher-onboarding.jsx";

function renderApp() {
  return render(
    <TeacherOnboardingI18nProvider>
      <TeacherOnboarding />
    </TeacherOnboardingI18nProvider>
  );
}

describe("Teacher onboarding flag-first locale gate", () => {
  beforeEach(() => {
    localStorage.removeItem(TEACHER_ONBOARDING_LOCALE_KEY);
  });

  it("renders the flag grid as the first content (no Identity section)", () => {
    renderApp();
    expect(screen.getByTestId("teacher-onboarding-flag-gate")).toBeTruthy();
    expect(screen.getByTestId("teacher-onboarding-flag-grid")).toBeTruthy();
    expect(screen.queryByText(/Who is the teacher/i)).toBeNull();
    expect(document.querySelector("#identity")).toBeNull();
  });

  it("clicking each of the 14 flags sets locale and reveals the form", async () => {
    for (const lane of TEACHER_ONBOARDING_LOCALES) {
      localStorage.removeItem(TEACHER_ONBOARDING_LOCALE_KEY);
      const { unmount } = renderApp();
      expect(screen.getByTestId("teacher-onboarding-flag-gate")).toBeTruthy();
      fireEvent.click(screen.getByTestId(`flag-${lane.code}`));
      expect(localStorage.getItem(TEACHER_ONBOARDING_LOCALE_KEY)).toBe(lane.code);
      // Form chrome appears
      expect(await screen.findByText("Teacher Onboarding")).toBeTruthy();
      expect(document.querySelector("#identity")).toBeTruthy();
      expect(screen.queryByTestId("teacher-onboarding-flag-gate")).toBeNull();
      unmount();
    }
  });

  it("does not render sections before a locale is chosen", () => {
    renderApp();
    for (const id of ["identity", "rights", "teachings", "stories", "practices", "voice", "activate"]) {
      expect(document.querySelector(`#${id}`)).toBeNull();
    }
  });
});
