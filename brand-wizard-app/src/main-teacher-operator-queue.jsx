import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import TeacherOperatorQueue from "./components/teacher-onboarding/TeacherOperatorQueue.jsx";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <TeacherOperatorQueue />
  </StrictMode>
);
