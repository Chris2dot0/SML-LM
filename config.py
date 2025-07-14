import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = DATA_DIR / "docs"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"
MODELS_DIR = BASE_DIR / "models"

# Create directories if they don't exist
for dir_path in [DATA_DIR, DOCS_DIR, EMBEDDINGS_DIR, MODELS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Model configurations
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Small, fast, good quality
LLM_MODEL = "microsoft/DialoGPT-medium"  # Small conversational model

# RAG settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_RETRIEVAL = 5

# Hexagon documentation URLs (you can add more)
HEXAGON_URLS = [
    "https://docs.hexagonppm.com/",
    # Add more specific SmartPlant URLs here
]

# File extensions to process
SUPPORTED_EXTENSIONS = ['.pdf', '.txt', '.md', '.html'] 