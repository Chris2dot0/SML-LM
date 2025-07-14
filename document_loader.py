import os
import requests
from pathlib import Path
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import PyPDF2
import io
from urllib.parse import urljoin, urlparse
import time
import logging

from config import DOCS_DIR, SUPPORTED_EXTENSIONS, HEXAGON_URLS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentLoader:
    """Loads and processes SmartPlant documentation from various sources."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def load_pdf(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract text from PDF files."""
        documents = []
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    if text.strip():
                        documents.append({
                            'content': text,
                            'source': str(file_path),
                            'page': page_num + 1,
                            'type': 'pdf'
                        })
                        
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {e}")
            
        return documents
    
    def load_text_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load text files."""
        documents = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                if content.strip():
                    documents.append({
                        'content': content,
                        'source': str(file_path),
                        'type': 'text'
                    })
        except Exception as e:
            logger.error(f"Error processing text file {file_path}: {e}")
            
        return documents
    
    def scrape_hexagon_docs(self, base_url: str, max_pages: int = 50) -> List[Dict[str, Any]]:
        """Scrape SmartPlant documentation from Hexagon website."""
        documents = []
        visited_urls = set()
        urls_to_visit = [base_url]
        
        page_count = 0
        
        while urls_to_visit and page_count < max_pages:
            url = urls_to_visit.pop(0)
            
            if url in visited_urls:
                continue
                
            visited_urls.add(url)
            
            try:
                logger.info(f"Scraping: {url}")
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract main content
                content = soup.get_text()
                if content.strip():
                    documents.append({
                        'content': content,
                        'source': url,
                        'type': 'web'
                    })
                
                # Find more links to visit
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(url, href)
                    
                    # Only follow links within the same domain
                    if (urlparse(full_url).netloc == urlparse(base_url).netloc and 
                        full_url not in visited_urls and 
                        full_url not in urls_to_visit):
                        urls_to_visit.append(full_url)
                
                page_count += 1
                time.sleep(1)  # Be respectful to the server
                
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
        
        return documents
    
    def load_all_documents(self) -> List[Dict[str, Any]]:
        """Load all documents from the docs directory and web sources."""
        all_documents = []
        
        # Load local documents
        for file_path in DOCS_DIR.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                logger.info(f"Loading local document: {file_path}")
                
                if file_path.suffix.lower() == '.pdf':
                    all_documents.extend(self.load_pdf(file_path))
                elif file_path.suffix.lower() in ['.txt', '.md']:
                    all_documents.extend(self.load_text_file(file_path))
        
        # Scrape web documentation
        for url in HEXAGON_URLS:
            logger.info(f"Scraping documentation from: {url}")
            all_documents.extend(self.scrape_hexagon_docs(url))
        
        logger.info(f"Loaded {len(all_documents)} documents total")
        return all_documents
    
    def save_documents_metadata(self, documents: List[Dict[str, Any]], filename: str = "documents_metadata.json"):
        """Save document metadata for future reference."""
        import json
        
        metadata = []
        for doc in documents:
            metadata.append({
                'source': doc['source'],
                'type': doc['type'],
                'content_length': len(doc['content']),
                'page': doc.get('page', None)
            })
        
        with open(DOCS_DIR / filename, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Saved metadata for {len(metadata)} documents")

if __name__ == "__main__":
    loader = DocumentLoader()
    documents = loader.load_all_documents()
    loader.save_documents_metadata(documents) 