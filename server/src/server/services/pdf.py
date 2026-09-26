import asyncio

import pymupdf
import pymupdf4llm


class InvalidOrEmptyPDF(Exception):
    @property
    def detail(self):
        return "Invalid or empty PDF"


def _pdf_to_markdown(pdf_bytes: bytes) -> str:
    try:
        with pymupdf.open(stream=pdf_bytes, filetype="pdf") as doc:
            md = pymupdf4llm.to_markdown(doc)
    except pymupdf.FileDataError:
        raise InvalidOrEmptyPDF from None

    if not isinstance(md, str):
        raise InvalidOrEmptyPDF
    return md


async def convert_pdf_to_markdown(pdf_bytes: bytes) -> str:
    return await asyncio.to_thread(_pdf_to_markdown, pdf_bytes)
