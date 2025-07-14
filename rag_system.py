import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import numpy as np

from config import (
    EMBEDDING_MODEL, LLM_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, 
    TOP_K_RETRIEVAL, EMBEDDINGS_DIR, MODELS_DIR
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SmartPlantRAG:
    """RAG system for SmartPlant instrumentation documentation."""
    
    def __init__(self, use_local_llm: bool = True):
        self.use_local_llm = use_local_llm
        self.embedding_model = None
        self.llm = None
        self.tokenizer = None
        self.vector_db = None
        self.chunks = []
        
        self._initialize_models()
        self._initialize_vector_db()
    
    def _initialize_models(self):
        """Initialize embedding and language models."""
        logger.info("Initializing models...")
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        
        if self.use_local_llm:
            # Initialize local LLM
            logger.info(f"Loading local LLM: {LLM_MODEL}")
            self.tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL)
            self.model = AutoModelForCausalLM.from_pretrained(
                LLM_MODEL,
                torch_dtype=torch.float16,
                device_map="auto",
                load_in_8bit=True  # For memory efficiency
            )
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            self.llm = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_length=512,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        else:
            logger.info("Using external LLM (not implemented in this version)")
    
    def _initialize_vector_db(self):
        """Initialize ChromaDB vector database."""
        logger.info("Initializing vector database...")
        
        # Initialize ChromaDB
        self.vector_db = chromadb.PersistentClient(
            path=str(EMBEDDINGS_DIR),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        try:
            self.collection = self.vector_db.get_collection("smartplant_docs")
            logger.info("Loaded existing collection")
        except:
            self.collection = self.vector_db.create_collection("smartplant_docs")
            logger.info("Created new collection")
    
    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Split documents into chunks for better retrieval."""
        chunks = []
        
        for doc in documents:
            content = doc['content']
            source = doc['source']
            doc_type = doc['type']
            page = doc.get('page', None)
            
            # Simple chunking by character count
            for i in range(0, len(content), CHUNK_SIZE - CHUNK_OVERLAP):
                chunk_text = content[i:i + CHUNK_SIZE]
                if len(chunk_text.strip()) > 50:  # Minimum chunk size
                    chunks.append({
                        'content': chunk_text.strip(),
                        'source': source,
                        'type': doc_type,
                        'page': page,
                        'chunk_id': len(chunks)
                    })
        
        logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")
        return chunks
    
    def create_embeddings(self, chunks: List[Dict[str, Any]]) -> List[List[float]]:
        """Create embeddings for document chunks."""
        logger.info("Creating embeddings...")
        
        texts = [chunk['content'] for chunk in chunks]
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        
        return embeddings.tolist()
    
    def index_documents(self, documents: List[Dict[str, Any]]):
        """Index documents in the vector database."""
        logger.info("Indexing documents...")
        
        # Chunk documents
        self.chunks = self.chunk_documents(documents)
        
        # Create embeddings
        embeddings = self.create_embeddings(self.chunks)
        
        # Prepare data for ChromaDB
        ids = [f"chunk_{i}" for i in range(len(self.chunks))]
        texts = [chunk['content'] for chunk in self.chunks]
        metadatas = [
            {
                'source': chunk['source'],
                'type': chunk['type'],
                'page': chunk.get('page', ''),
                'chunk_id': chunk['chunk_id']
            }
            for chunk in self.chunks
        ]
        
        # Add to vector database
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Indexed {len(self.chunks)} chunks in vector database")
    
    def retrieve_relevant_chunks(self, query: str, top_k: int = TOP_K_RETRIEVAL) -> List[Dict[str, Any]]:
        """Retrieve relevant document chunks for a query."""
        # Create query embedding
        query_embedding = self.embedding_model.encode([query])
        
        # Search in vector database
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=top_k
        )
        
        # Format results
        relevant_chunks = []
        for i in range(len(results['documents'][0])):
            chunk = {
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i] if 'distances' in results else None
            }
            relevant_chunks.append(chunk)
        
        return relevant_chunks
    
    def generate_response(self, query: str, context: str) -> str:
        """Generate response using local LLM with context."""
        if not self.use_local_llm:
            return "Local LLM not available"
        
        # Create prompt with context
        prompt = f"""Context about SmartPlant instrumentation:
{context}

Question: {query}

Answer:"""
        
        try:
            # Generate response
            response = self.llm(prompt, max_length=len(prompt.split()) + 200)[0]['generated_text']
            
            # Extract only the new part (after the prompt)
            response = response[len(prompt):].strip()
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error generating response: {str(e)}"
    
    def query(self, question: str) -> Dict[str, Any]:
        """Main query function that combines retrieval and generation."""
        logger.info(f"Processing query: {question}")
        
        # Retrieve relevant chunks
        relevant_chunks = self.retrieve_relevant_chunks(question)
        
        if not relevant_chunks:
            return {
                'answer': 'No relevant documentation found for your question.',
                'sources': [],
                'context': ''
            }
        
        # Combine context from relevant chunks
        context = "\n\n".join([chunk['content'] for chunk in relevant_chunks])
        
        # Generate response
        answer = self.generate_response(question, context)
        
        # Prepare sources
        sources = []
        for chunk in relevant_chunks:
            source_info = {
                'source': chunk['metadata']['source'],
                'type': chunk['metadata']['type'],
                'page': chunk['metadata'].get('page', ''),
                'relevance_score': 1 - chunk.get('distance', 0) if chunk.get('distance') else 1.0
            }
            sources.append(source_info)
        
        return {
            'answer': answer,
            'sources': sources,
            'context': context[:500] + "..." if len(context) > 500 else context
        }
    
    def save_system_state(self):
        """Save system state for future use."""
        state = {
            'chunks_count': len(self.chunks),
            'embedding_model': EMBEDDING_MODEL,
            'llm_model': LLM_MODEL if self.use_local_llm else None,
            'indexed_at': str(Path().absolute())
        }
        
        with open(EMBEDDINGS_DIR / "system_state.json", 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info("System state saved")

if __name__ == "__main__":
    # Example usage
    rag = SmartPlantRAG()
    print("RAG system initialized successfully!") 