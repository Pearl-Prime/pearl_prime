# Renderer Rebuild Plan

The renderer is rebuilt as a design-family router rather than a single deterministic card
template. For raster-led layouts it loads an image-bank candidate, crops to the native
platform canvas, scores quiet zones, and records the placement decision. For structured
families it uses deliberate composition systems: checklist rows, diagram rails, editorial
type columns, tactile page surfaces, and object-first crops.

This is a proof rebuild, not a live publishing implementation. The output is ready for
operator visual QA and further renderer extraction after the look gate.
