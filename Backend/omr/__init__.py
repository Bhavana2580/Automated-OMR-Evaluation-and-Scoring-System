# backend/omr/_init_.py

"""
OMR (Optical Mark Recognition) backend package.

Contains:
- processor.py   → Core OMR pipeline (preprocessing, bubble detection, scoring).
- utils.py       → Helper functions (image loading, saving, grayscale, etc.).
- classifier.py  → ML-based mark/unmark classifier (optional fallback).
- pdf_utils.py   → Utilities for handling PDFs.
"""

_version_ = "0.1.0"
_all_ = ["processor", "utils", "classifier", "pdf_utils"]