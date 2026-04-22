import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import BrandWizard from "./BrandWizard-zh.jsx";
import { I18nProvider } from "./i18n.jsx";
import stringsZh from "./strings-zh.json";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <I18nProvider locale="zh" strings={stringsZh}>
      <BrandWizard />
    </I18nProvider>
  </React.StrictMode>
);
