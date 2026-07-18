# Mobile, Accessibility, Performance Notes

The shared report UI uses responsive grid tracks, visible labels, keyboard-native form controls, and no animation dependency. It adds one small CSS/JS surface to already-loaded shared assets.

Local mobile smoke, 2026-07-14:

- Viewport: 390x844 through `agent-browser set viewport`.
- Page: `/free/way_stream_sanctuary/somatic-body-scan/`.
- Result: old form hidden, tool visible, report offer present, completion control present, no horizontal overflow.

Full Lighthouse/per-device capture is deferred until a deployed preview URL is available.
