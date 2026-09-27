"""Deterministic resume guide normalizations (not LLM-dependent)."""

from __future__ import annotations

import re
from datetime import date

from server.schemas.candidate import EducationEntry, ProfileLink
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
_VOLUNTEER_TAG_RE = re.compile(
    r"\s*[\(\[{]?\s*volunteer\s*[\)\]}]?\s*",
    re.IGNORECASE,
)


def abbreviate_degree(degree: str | None) -> str | None:
    """Map spelled-out degrees to guide form (B.A., B.S., M.A., PhD, …)."""
    if not degree:
        return degree
    text = degree.strip()
    for pattern, abbr in _DEGREE_PATTERNS:
        if pattern.search(text):
            return abbr
    return text


def normalize_job_title(title: str | None) -> str | None:
    """Strip downgrading volunteer tags and fix ALL-CAPS titles."""
    if not title:
        return title
    text = _VOLUNTEER_TAG_RE.sub(" ", title).strip()
    text = re.sub(r"\s{2,}", " ", text).strip(" -|,")
    letters = [c for c in text if c.isalpha()]
    if letters and all(c.isupper() for c in letters) and len(letters) > 3:
        text = text.title()
        text = text.replace("&Amp;", "&").replace(" And ", " & ")
    return text or title.strip()


def education_status_label(graduation: str | None) -> str | None:
    """Guide-shaped right-side education status.

    - Graduated (>3 years): Status - Graduated
    - Still enrolled / future year: Expected YYYY
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
        return f"Expected {year_match.group(1)}"
    if year_match:
        year = int(year_match.group(1))
        if year > date.today().year:
            return f"Expected {year}"
        return str(year)
    return text


def normalize_education_entry(entry: EducationEntry) -> EducationEntry:
    return entry.model_copy(update={"degree": abbreviate_degree(entry.degree)})


_LINK_PRIORITY = ("linkedin", "github", "gitlab")


def merge_profile_links(
    primary: list[ProfileLink],
    secondary: list[ProfileLink],
) -> list[ProfileLink]:
    """Dedupe by URL (case-insensitive); prefer labeled / priority hosts."""
    by_url: dict[str, ProfileLink] = {}
    for link in [*primary, *secondary]:
        url = (link.url or "").strip().rstrip("/")
        if not url:
            continue
        key = url.lower()
        existing = by_url.get(key)
        if existing is None:
            by_url[key] = ProfileLink(url=url, label=link.label)
            continue
        if not existing.label and link.label:
            by_url[key] = ProfileLink(url=existing.url, label=link.label)

    def sort_key(link: ProfileLink) -> tuple[int, str]:
        host = link.url.lower()
        for i, token in enumerate(_LINK_PRIORITY):
            if token in host:
                return (i, host)
        return (len(_LINK_PRIORITY), host)

    return sorted(by_url.values(), key=sort_key)


def tighten_profile_summary(summary: str | None, *, max_chars: int = 420) -> str | None:
    """Keep profile summaries to ~2 sentences with room for visa/availability."""
    if not summary:
        return summary
    text = re.sub(r"\s+", " ", summary).strip()
    if not text:
        return None
    parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+", text) if p.strip()]
    if len(parts) > 2:
        text = " ".join(parts[:2]).strip()
    if len(text) <= max_chars:
        return text
    kept: list[str] = []
    for part in parts[:2]:
        candidate = " ".join([*kept, part]).strip()
        if kept and len(candidate) > max_chars:
            break
        kept.append(part)
    out = " ".join(kept).strip() or text[:max_chars].rsplit(" ", 1)[0]
    return out.rstrip(",;") + ("." if out and out[-1] not in ".!?" else "")


def normalize_tailored_resume(resume: TailoredResume) -> TailoredResume:
    """Apply guide formatting fixes the LLM may miss."""
    updates: dict = {}
    if resume.education:
        updates["education"] = [
            normalize_education_entry(e) for e in resume.education
        ]
    if resume.work_history:
        updates["work_history"] = [
            role.model_copy(update={"title": normalize_job_title(role.title)})
            for role in resume.work_history
        ]
    tightened = tighten_profile_summary(resume.summary)
    if tightened != resume.summary:
        updates["summary"] = tightened
    if not updates:
        return resume
    return resume.model_copy(update=updates)
