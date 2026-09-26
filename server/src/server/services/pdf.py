import asyncio

import pymupdf
import pymupdf4llm


def _pdf_to_markdown(pdf_bytes: bytes) -> str:
    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as doc:
        return pymupdf4llm.to_markdown(doc)


async def convert_pdf_to_markdown(pdf_bytes: bytes) -> str:
    return await asyncio.to_thread(_pdf_to_markdown, pdf_bytes)
