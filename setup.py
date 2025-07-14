#!/usr/bin/env python3
"""
Setup script for SmartPlant RAG System
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_system_requirements():
    """Check system requirements."""
    print("\n🔍 Checking system requirements...")
    
    # Check RAM (approximate)
    try:
        import psutil
        ram_gb = psutil.virtual_memory().total / (1024**3)
        if ram_gb < 8:
            print(f"⚠️  RAM: {ram_gb:.1f}GB (8GB recommended)")
        else:
            print(f"✅ RAM: {ram_gb:.1f}GB")
    except ImportError:
        print("⚠️  Could not check RAM (psutil not installed)")
    
    # Check disk space
    try:
        import shutil
        disk_usage = shutil.disk_usage('.')
        free_gb = disk_usage.free / (1024**3)
        if free_gb < 5:
            print(f"⚠️  Free disk space: {free_gb:.1f}GB (5GB recommended)")
        else:
            print(f"✅ Free disk space: {free_gb:.1f}GB")
    except:
        print("⚠️  Could not check disk space")

def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories."""
    print("\n📁 Creating directories...")
    
    directories = [
        "data",
        "data/docs",
        "data/embeddings",
        "models"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {directory}")

def download_sample_docs():
    """Download sample documentation if none exists."""
    docs_dir = Path("data/docs")
    
    if not any(docs_dir.glob("*")):
        print("\n📚 No documentation found. Creating sample file...")
        
        sample_content = """
SmartPlant Instrumentation - Sample Documentation

This is a sample documentation file for SmartPlant Instrumentation.
Replace this with your actual SmartPlant documentation files.

Common SmartPlant Instrumentation Topics:

1. System Setup and Configuration
   - Installation requirements
   - Database configuration
   - User management

2. Instrument Configuration
   - Pressure transmitters
   - Temperature sensors
   - Flow meters
   - Control valves

3. Project Management
   - Creating new projects
   - Importing data
   - Exporting reports

4. Best Practices
   - Instrument tagging
   - Documentation standards
   - Quality assurance

5. Troubleshooting
   - Common issues
   - Error messages
   - Performance optimization

For more information, visit the official Hexagon documentation site.
        """
        
        with open(docs_dir / "sample_documentation.txt", "w") as f:
            f.write(sample_content)
        
        print("✅ Created sample documentation file")
        print("💡 Replace with your actual SmartPlant documentation")

def setup_environment():
    """Setup environment variables and configurations."""
    print("\n⚙️  Setting up environment...")
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        env_content = """# SmartPlant RAG System Environment Variables

# Model configurations
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_MODEL=microsoft/DialoGPT-medium

# System settings
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RETRIEVAL=5

# Web scraping settings
MAX_SCRAPE_PAGES=50
SCRAPE_DELAY=1
        """
        
        with open(env_file, "w") as f:
            f.write(env_content)
        
        print("✅ Created .env file")

def main():
    """Main setup function."""
    print("🚀 SmartPlant RAG System Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check system requirements
    check_system_requirements()
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed. Please check the error messages above.")
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Download sample docs
    download_sample_docs()
    
    print("\n" + "=" * 40)
    print("✅ Setup completed successfully!")
    print("\n🎯 Next steps:")
    print("1. Add your SmartPlant documentation to 'data/docs/'")
    print("2. Run: python main.py --setup")
    print("3. Start the web interface: streamlit run web_interface.py")
    print("\n📖 For more information, see README.md")

if __name__ == "__main__":
    main() 