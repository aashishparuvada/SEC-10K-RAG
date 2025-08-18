import os
import re
import time
import requests
from bs4 import BeautifulSoup
from config import CIKS, YEARS, SEC_BROWSE_URL, UA, DATA_DIR

def _first_10k_filing_docs_url(cik: str, year: str) -> str | None:
    # Date upper bound = 31 Dec of the given year to prefer that year’s 10-K
    url = f"{SEC_BROWSE_URL}?CIK={cik}&type=10-K&dateb={year}1231&owner=exclude&count=100"
    time.sleep(0.5)  # Be respectful to SEC servers
    r = requests.get(url, headers=UA, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    btn = soup.find("a", id="documentsbutton")
    if not btn:
        return None
    return "https://www.sec.gov" + btn["href"]

def _pick_pdf_url_from_docs(doc_soup: BeautifulSoup) -> str | None:
    # Prioritise the main 10-K PDF if available; fallback to any .htm if no pdf
    rows = doc_soup.select("table.tableFile tr")
    pdf_href, htm_href = None, None
    for tr in rows:
        cells = tr.find_all("td")
        if len(cells) >= 3:
            doc_type = cells[3].get_text(strip=True) if len(cells) > 3 else ""
            link = cells[2].find("a") if len(cells) > 2 else None
            href = link["href"] if link and link.has_attr("href") else None
            if not href:
                continue
            if href.lower().endswith(".pdf") and ("10-k" in doc_type.lower() or "form 10-k" in doc_type.lower()):
                pdf_href = "https://www.sec.gov" + href
            if href.lower().endswith((".htm", ".html")) and not htm_href:
                htm_href = "https://www.sec.gov" + href
    return pdf_href or htm_href

def download_filings(output_dir: str = DATA_DIR) -> None:
    os.makedirs(output_dir, exist_ok=True)
    for ticker, cik in CIKS.items():
        for year in YEARS:
            out_pdf = os.path.join(output_dir, f"{ticker}_{year}.pdf")
            out_htm = os.path.join(output_dir, f"{ticker}_{year}.html")

            if os.path.exists(out_pdf) or os.path.exists(out_htm):
                print(f"[skip] Already have {ticker} {year}")
                continue

            docs_url = _first_10k_filing_docs_url(cik, year)
            if not docs_url:
                print(f"[warn] No docs URL for {ticker} {year}")
                continue

            # Add delay to be respectful to SEC servers
            time.sleep(1)
            dr = requests.get(docs_url, headers=UA, timeout=30)
            dr.raise_for_status()
            soup = BeautifulSoup(dr.text, "html.parser")
            file_url = _pick_pdf_url_from_docs(soup)
            if not file_url:
                print(f"[warn] No primary file found for {ticker} {year}")
                continue

            fr = requests.get(file_url, headers=UA, timeout=60)
            fr.raise_for_status()
            is_pdf = file_url.lower().endswith(".pdf")
            path = out_pdf if is_pdf else out_htm
            with open(path, "wb") as f:
                f.write(fr.content)
            print(f"[ok] Downloaded {ticker} {year} -> {path}")
