#!/usr/bin/env python3
"""
SmartPlant Instrumentation Documentation RAG System
A local LLM system for querying SmartPlant documentation
"""

import os
import sys
import logging
from pathlib import Path
import argparse

from document_loader import DocumentLoader
from rag_system import SmartPlantRAG
from config import DOCS_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_system():
    """Initialize the RAG system with documents."""
    print("🚀 Setting up SmartPlant RAG System...")
    
    # Load documents
    print("📚 Loading documents...")
    loader = DocumentLoader()
    documents = loader.load_all_documents()
    
    if not documents:
        print("⚠️  No documents found! Please add some SmartPlant documentation to the 'data/docs' folder.")
        print("   Supported formats: PDF, TXT, MD, HTML")
        return None
    
    # Initialize RAG system
    print("🤖 Initializing RAG system...")
    rag = SmartPlantRAG()
    
    # Index documents
    print("📊 Indexing documents...")
    rag.index_documents(documents)
    rag.save_system_state()
    
    print(f"✅ System ready! Indexed {len(documents)} documents.")
    return rag

def interactive_mode(rag):
    """Run interactive query mode."""
    print("\n" + "="*60)
    print("🎯 SmartPlant Documentation Assistant")
    print("="*60)
    print("Ask questions about SmartPlant instrumentation!")
    print("Type 'quit' or 'exit' to stop.")
    print("Type 'help' for example questions.")
    print("-"*60)
    
    while True:
        try:
            question = input("\n❓ Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if question.lower() == 'help':
                print("\n📖 Example questions:")
                print("  • How do I configure a pressure transmitter?")
                print("  • What are the steps for instrument calibration?")
                print("  • How to set up SmartPlant Instrumentation?")
                print("  • What are the system requirements?")
                print("  • How to create a new project?")
                continue
            
            if not question:
                continue
            
            print("\n🔍 Searching documentation...")
            result = rag.query(question)
            
            print(f"\n💡 Answer:")
            print(f"   {result['answer']}")
            
            if result['sources']:
                print(f"\n📚 Sources:")
                for i, source in enumerate(result['sources'][:3], 1):
                    print(f"   {i}. {source['source']}")
                    if source.get('page'):
                        print(f"      Page: {source['page']}")
                    if source.get('relevance_score'):
                        print(f"      Relevance: {source['relevance_score']:.2f}")
            
            print("-"*60)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def single_query_mode(rag, question):
    """Run single query mode."""
    print(f"🔍 Query: {question}")
    result = rag.query(question)
    
    print(f"\n💡 Answer:")
    print(f"   {result['answer']}")
    
    if result['sources']:
        print(f"\n📚 Sources:")
        for i, source in enumerate(result['sources'][:3], 1):
            print(f"   {i}. {source['source']}")
            if source.get('page'):
                print(f"      Page: {source['page']}")

def main():
    parser = argparse.ArgumentParser(description="SmartPlant Documentation RAG System")
    parser.add_argument("--query", "-q", help="Single query to run")
    parser.add_argument("--setup", "-s", action="store_true", help="Setup/rebuild the system")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    # Check if system is already set up
    system_state_file = Path("data/embeddings/system_state.json")
    
    if args.setup or not system_state_file.exists():
        rag = setup_system()
        if not rag:
            return
    else:
        print("🔄 Loading existing RAG system...")
        rag = SmartPlantRAG()
    
    # Run appropriate mode
    if args.query:
        single_query_mode(rag, args.query)
    elif args.interactive or not args.query:
        interactive_mode(rag)

if __name__ == "__main__":
    main() 