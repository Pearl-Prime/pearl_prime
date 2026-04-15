import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App.jsx";
import { detectLocale, loadLocale, I18nProvider } from "./i18n.jsx";

const locale = detectLocale();

loadLocale(locale).then(({ strings }) => {
  ReactDOM.createRoot(document.getElementById("root")).render(
    <React.StrictMode>
      <I18nProvider locale={locale} strings={strings}>
        <App />
      </I18nProvider>
    </React.StrictMode>
  );
});
