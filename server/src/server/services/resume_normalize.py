"""Deterministic resume guide normalizations (not LLM-dependent)."""

from __future__ import annotations

import re
from datetime import date

from server.schemas.candidate import EducationEntry
from server.schemas.tailored_resume import TailoredResume

# Longest / most specific first so "Master of Business Administration" wins over "Master".
_DEGREE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bmaster\s+of\s+business\s+administration\b", re.I), "MBA"),
    (re.compile(r"\bbachelor\s+of\s+business\s+administration\b", re.I), "B.B.A."),
    (re.compile(r"\bbachelor\s+of\s+science\b", re.I), "B.S."),
    (re.compile(r"\bbachelor\s+of\s+arts\b", re.I), "B.A."),
    (re.compile(r"\bbachelor\s+of\s+engineering\b", re.I), "B.Eng."),
    (re.compile(r"\bbachelor\s+of\s+fine\s+arts\b", re.I), "B.F.A."),
    (re.compile(r"\bmaster\s+of\s+science\b", re.I), "M.S."),
    (re.compile(r"\bmaster\s+of\s+arts\b", re.I), "M.A."),
    (re.compile(r"\bmaster\s+of\s+engineering\b", re.I), "M.Eng."),
    (re.compile(r"\bmaster\s+of\s+fine\s+arts\b", re.I), "M.F.A."),
    (re.compile(r"\bdoctor\s+of\s+philosophy\b", re.I), "PhD"),
    (re.compile(r"\bassociate\s+of\s+science\b", re.I), "A.S."),
    (re.compile(r"\bassociate\s+of\s+arts\b", re.I), "A.A."),
    (re.compile(r"\bbachelor'?s?\s+degree\b", re.I), "B.S."),
    (re.compile(r"\bmaster'?s?\s+degree\b", re.I), "M.S."),
]

_YEAR_RE = re.compile(r"(20\d{2}|19\d{2})")


def abbreviate_degree(degree: str | None) -> str | None:
    """Map spelled-out degrees to guide form (B.A., B.S., M.A., PhD, …)."""
    if not degree:
        return degree
    text = degree.strip()
    for pattern, abbr in _DEGREE_PATTERNS:
        if pattern.search(text):
            return abbr
    return text


def education_status_label(graduation: str | None) -> str | None:
    """Guide-shaped right-side education status.

    - Graduated (>3 years): Status - Graduated
    - Still enrolled / future year: Status - Expected YYYY
    - Recent graduation year: YYYY
    """
    if not graduation:
        return None
    text = graduation.strip()
    lower = text.lower()
    if lower in {"graduated", "status - graduated", "status graduated"}:
        return "Status - Graduated"
    year_match = _YEAR_RE.search(text)
    if "expected" in lower and year_match:
        return f"Status - Expected {year_match.group(1)}"
    if year_match:
        year = int(year_match.group(1))
        if year > date.today().year:
            return f"Status - Expected {year}"
        return str(year)
    return text


def normalize_education_entry(entry: EducationEntry) -> EducationEntry:
    return entry.model_copy(update={"degree": abbreviate_degree(entry.degree)})


def normalize_tailored_resume(resume: TailoredResume) -> TailoredResume:
    """Apply guide formatting fixes the LLM may miss."""
    if not resume.education:
        return resume
    return resume.model_copy(
        update={
            "education": [normalize_education_entry(e) for e in resume.education],
        }
    )
