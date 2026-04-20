import { useState, useEffect, useRef, lazy, Suspense } from "react";
import HeroSection from "@/components/onboarding/HeroSection";
import CountrySelection from "@/components/onboarding/CountrySelection";
import SystemOverview from "@/components/onboarding/SystemOverview";
import ValueLadder from "@/components/onboarding/ValueLadder";
import Social48 from "@/components/onboarding/Social48";
import TeacherExpression from "@/components/onboarding/TeacherExpression";
import WizardHandoff from "@/components/onboarding/WizardHandoff";

const RevenueModel = lazy(() => import("@/components/onboarding/RevenueModel"));
const MarketFit = lazy(() => import("@/components/onboarding/MarketFit"));
const RealExamples = lazy(() => import("@/components/onboarding/RealExamples"));

// ---------- Scroll tracking hook ----------
function useSectionTracking(sectionIds) {
  const viewsRef = useRef({});
  const activeRef = useRef(null);
  const [activeId, setActiveId] = useState(null);

  useEffect(() => {
    const closeActive = () => {
      const current = activeRef.current;
      if (current && viewsRef.current[current]?.enteredAt) {
        const v = viewsRef.current[current];
        v.totalMs += Date.now() - v.enteredAt;
        v.enteredAt = 0;
      }
    };

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

        if (!visible) return;

        const id = visible.target.id;
        if (id === activeRef.current) return;

        closeActive();

        const step = Number(visible.target.dataset.step ?? 0);
        const existing = viewsRef.current[id];
        viewsRef.current[id] = {
          id,
          step,
          enteredAt: Date.now(),
          totalMs: existing?.totalMs ?? 0,
        };
        activeRef.current = id;
        setActiveId(id);
      },
      { threshold: [0.25, 0.5, 0.75] }
    );

    sectionIds.forEach((id) => {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    });

    const handleUnload = () => { closeActive(); };
    const handleVisibility = () => {
      if (document.visibilityState === "hidden") closeActive();
    };

    window.addEventListener("beforeunload", handleUnload);
    document.addEventListener("visibilitychange", handleVisibility);

    return () => {
      observer.disconnect();
      window.removeEventListener("beforeunload", handleUnload);
      document.removeEventListener("visibilitychange", handleVisibility);
      closeActive();
    };
  }, [sectionIds.join(",")]);

  return { activeId, views: viewsRef };
}

// ---------- Page ----------
export default function Index() {
  const [market, setMarket] = useState("us");

  const sections = [
    { id: "hero",      step: 1,  component: <HeroSection /> },
    { id: "market",    step: 2,  component: <CountrySelection selected={market} onSelect={setMarket} /> },
    { id: "system",    step: 3,  component: <SystemOverview /> },
    { id: "value",     step: 4,  component: <ValueLadder /> },
    { id: "social",    step: 5,  component: <Social48 /> },
    { id: "revenue",   step: 6,  component: <RevenueModel />, lazy: true },
    { id: "marketFit", step: 7,  component: <MarketFit market={market} />, lazy: true },
    { id: "examples",  step: 8,  component: <RealExamples />, lazy: true },
    { id: "teacher",   step: 9,  component: <TeacherExpression /> },
    { id: "handoff",   step: 10, component: <WizardHandoff /> },
  ];

  const visibleSections = sections.filter(
    (s) => !s.visibleFor || s.visibleFor.includes(market)
  );

  const { activeId } = useSectionTracking(visibleSections.map((s) => s.id));

  const progress = activeId
    ? (visibleSections.findIndex((s) => s.id === activeId) + 1) / visibleSections.length
    : 0;

  return (
    <div style={{ minHeight: "100vh", background: "#0e0a06", color: "#faf6f0" }}>
      {/* Scroll progress bar */}
      <div
        style={{
          position: "fixed", top: 0, left: 0, right: 0, height: 2,
          background: "#b45309", zIndex: 50,
          width: `${progress * 100}%`, transition: "width 0.3s ease"
        }}
        aria-hidden
      />

      {visibleSections.map(({ id, step, component, lazy: isLazy }) => (
        <section key={id} id={id} data-step={step} style={{ scrollMarginTop: "4rem" }}>
          {isLazy ? (
            <Suspense fallback={
              <div style={{ padding: "5rem 0", textAlign: "center", color: "rgba(250,246,240,.4)" }}>
                Loading…
              </div>
            }>
              {component}
            </Suspense>
          ) : (
            component
          )}
        </section>
      ))}

      <footer style={{ padding: "3rem 0", borderTop: "1px solid rgba(180,83,9,.15)" }}>
        <div style={{ maxWidth: 1152, margin: "0 auto", padding: "0 1.5rem", textAlign: "center" }}>
          <p style={{ fontSize: ".875rem", color: "rgba(250,246,240,.35)" }}>
            Phoenix Brand Growth System — built for teachers who want to reach the world.
          </p>
        </div>
      </footer>
    </div>
  );
}
