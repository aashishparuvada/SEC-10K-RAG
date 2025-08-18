import os
import re
from typing import List, Dict, Tuple
import pdfplumber
import tiktoken
from config import DATA_DIR

def _read_pdf_text_with_pages(path: str) -> List[Tuple[int, str]]:
    text_pages = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            try:
                txt = page.extract_text() or ""
            except Exception:
                txt = ""
            txt = re.sub(r"[ \t]+", " ", txt)
            text_pages.append((i, txt.strip()))
    return text_pages

def _read_html_text(path: str) -> str:
    # Simple HTML stripper (lightweight). For richer HTML, you can use BeautifulSoup.get_text()
    from bs4 import BeautifulSoup
    with open(path, "rb") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    return soup.get_text(separator="\n")

def load_docs_raw(data_dir: str = DATA_DIR) -> Dict[str, List[Tuple[int, str]]]:
    docs: Dict[str, List[Tuple[int, str]]] = {}
    for fn in os.listdir(data_dir):
        fpath = os.path.join(data_dir, fn)
        if fn.lower().endswith(".pdf"):
            pages = _read_pdf_text_with_pages(fpath)
            docs[fn] = pages
        elif fn.lower().endswith((".htm", ".html")):
            txt = _read_html_text(fpath)
            # fake page = 1 for html
            docs[fn] = [(1, txt)]
    return docs

def token_chunks(text: str, chunk_tokens: int = 700, overlap_tokens: int = 80, model: str = "gpt-4o-mini") -> List[str]:
    # Use a close tokenizer (tiktoken for cl100k_base) — good enough for OpenAI chat models
    enc = tiktoken.get_encoding("cl100k_base")
    toks = enc.encode(text)
    chunks = []
    step = chunk_tokens - overlap_tokens
    for i in range(0, len(toks), step):
        seg = toks[i:i+chunk_tokens]
        chunks.append(enc.decode(seg))
    return chunks
