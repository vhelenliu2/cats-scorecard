"""CATS Scale + Revenue/FTE staging ingestion skill (MVP, staging-only).

This package reads approved source data, computes the CATS Scale metrics and
Revenue / S+M FTE per the Operations Runbook methodology, validates the result,
and writes an isolated STAGING sheet. It never writes to the production
dashboard or to any source workbook (see cats_ingest.safety).
"""

__version__ = "0.1.0"
