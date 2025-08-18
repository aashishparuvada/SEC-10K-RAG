import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY in environment or .env")

# Chroma + data paths - use absolute paths relative to project root
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERSIST_DIR = os.getenv("PERSIST_DIR", os.path.join(_project_root, "chroma_store"))
DATA_DIR = os.getenv("DATA_DIR", os.path.join(_project_root, "data"))

# Embedding & chat models (adjust if you like)
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")

# Companies & years for the assignment
CIKS = {
    "GOOGL": "0001652044",  # Alphabet
    "MSFT": "0000789019",
    "NVDA": "0001045810",
}
YEARS = ["2022", "2023", "2024"]

SEC_BROWSE_URL = "https://www.sec.gov/cgi-bin/browse-edgar"
UA = {"User-Agent": "Company-Research-Bot/1.0 (educational use; contact@example.com)"}
