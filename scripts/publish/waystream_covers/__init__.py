"""Waystream Sanctuary cover template system (Pearl_Dev).

A varied, per-author + per-topic book-cover renderer:
  * 8-family layout LIBRARY (4 image / 4 image-free)  -> templates.py
  * deterministic author -> (family, fonts, palette, symbol) assignment  -> assign.py
  * high-contrast per-topic symbol vocabulary w/ per-book count/arrangement -> symbols.py
  * contrast-guaranteed color math + gradients -> palette.py
  * verified macOS font resolution -> fonts.py

Contract: config/publishing/waystream_cover_system.yaml
Compositing is deterministic PIL; FLUX (schnell) only supplies imagery pools.
"""
