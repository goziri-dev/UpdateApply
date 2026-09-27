import asyncio
import re
from urllib.parse import urlparse

import pymupdf
import pymupdf4llm


class InvalidOrEmptyPDF(Exception):
    @property
    def detail(self):
        return "Invalid or empty PDF"


_URL_RE = re.compile(
    r"(?i)\b(?:https?://|www\.)[^\s<>\"')\]]+",
)
_BARE_PROFILE_RE = re.compile(
    r"(?i)\b(?:linkedin\.com/in/[^\s<>\"')\]]+|github\.com/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)?)",
)


def _infer_link_label(url: str) -> str | None:
    host = urlparse(url).netloc.lower()
    if "linkedin.com" in host:
        return "LinkedIn"
    if "github.com" in host:
        return "GitHub"
    if "gitlab.com" in host:
        return "GitLab"
    if "behance.net" in host:
        return "Behance"
    if "dribbble.com" in host:
        return "Dribbble"
    if "medium.com" in host:
        return "Medium"
    return None


def _normalize_uri(uri: str) -> str | None:
    text = (uri or "").strip().rstrip(".,;:)")
    if not text:
        return None
    lower = text.lower()
    if lower.startswith(("mailto:", "tel:", "javascript:")):
        return None
    if not lower.startswith(("http://", "https://")):
        if lower.startswith("www.") or lower.startswith(
            ("linkedin.com/", "github.com/", "gitlab.com/")
        ):
            text = f"https://{text}"
        else:
            return None
    return text.rstrip("/")


def _add_uri(
    seen: set[str],
    out: list[tuple[str, str | None]],
    raw: str,
) -> None:
    uri = _normalize_uri(raw)
    if not uri:
        return
    key = uri.lower()
    if key in seen:
        return
    seen.add(key)
    out.append((uri, _infer_link_label(uri)))


def extract_pdf_uris(
    doc: pymupdf.Document,
    markdown: str = "",
) -> list[tuple[str, str | None]]:
    """Collect profile URLs from annotations and visible/markdown text."""
    seen: set[str] = set()
    out: list[tuple[str, str | None]] = []

    for page in doc:
        for link in page.get_links():
            _add_uri(seen, out, link.get("uri") or "")
        # Some exporters put URIs only in annotation objects.
        for annot in page.annots() or []:
            info = annot.info or {}
            for key in ("content", "title", "subject", "name"):
                val = info.get(key) or ""
                if "http" in val.lower() or "linkedin" in val.lower():
                    for match in _URL_RE.findall(val):
                        _add_uri(seen, out, match)
            try:
                uri = annot.uri  # type: ignore[attr-defined]
            except AttributeError:
                uri = None
            if uri:
                _add_uri(seen, out, str(uri))
        raw_text = page.get_text("text")
        text = raw_text if isinstance(raw_text, str) else ""
        for match in _URL_RE.findall(text):
            _add_uri(seen, out, match)
        for match in _BARE_PROFILE_RE.findall(text):
            _add_uri(seen, out, match)

    for match in _URL_RE.findall(markdown or ""):
        _add_uri(seen, out, match)
    for match in _BARE_PROFILE_RE.findall(markdown or ""):
        _add_uri(seen, out, match)

    return out


def _pdf_to_markdown(pdf_bytes: bytes) -> tuple[str, list[tuple[str, str | None]]]:
    try:
        with pymupdf.open(stream=pdf_bytes, filetype="pdf") as doc:
            md = pymupdf4llm.to_markdown(doc)
            if not isinstance(md, str):
                raise InvalidOrEmptyPDF
            uris = extract_pdf_uris(doc, md)
    except pymupdf.FileDataError:
        raise InvalidOrEmptyPDF from None

    if uris:
        lines = "\n".join(
            f"- {label}: {url}" if label else f"- {url}" for url, label in uris
        )
        md = f"{md.rstrip()}\n\n## Extracted hyperlinks\n{lines}\n"

    return md, uris


async def convert_pdf_to_markdown(
    pdf_bytes: bytes,
) -> tuple[str, list[tuple[str, str | None]]]:
    return await asyncio.to_thread(_pdf_to_markdown, pdf_bytes)
