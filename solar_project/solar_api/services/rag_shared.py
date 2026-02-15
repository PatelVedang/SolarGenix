import hashlib
import os
import re
from urllib.parse import urlparse

import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

# =====================================================
# LOAD ENV
# =====================================================
load_dotenv()

# =====================================================
# CONFIG
# =====================================================
CHUNK_SIZE = 220
DB_CONFIG = {
    "host": os.getenv("SQL_DATABASE_HOST"),
    "dbname": os.getenv("SQL_DATABASE"),
    "user": os.getenv("SQL_USER"),
    "password": os.getenv("SQL_PASSWORD"),
    "port": os.getenv("SQL_DATABASE_PORT", "5432"),
    "sslmode": "require"
}

# =====================================================
# GLOBALS
# =====================================================
_EMBEDDER = None

def get_embedder():
    """Lazy load the sentence transformer model."""
    global _EMBEDDER
    if _EMBEDDER is None:
        _EMBEDDER = SentenceTransformer(
            "nomic-ai/nomic-embed-text-v1",
            trust_remote_code=True
        )
    return _EMBEDDER

# =====================================================
# DB SETUP
# =====================================================
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

# =====================================================
# UTILS
# =====================================================
def normalize_url(url):
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")

def clean_text(text):
    return text.replace("\x00", "").strip()

def page_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def chunk_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def chunk_text(text, size=200, overlap=50):
    words = text.split()
    step = size - overlap
    for i in range(0, len(words), step):
        yield " ".join(words[i:i + size])

def extract_keywords(question):
    words = re.findall(r'\b[a-zA-Z]{3,}\b', question.lower())
    return list(set(words))