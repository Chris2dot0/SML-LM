# 🏭 SmartPlant Instrumentation Documentation RAG System

A local LLM system for querying SmartPlant instrumentation documentation using Retrieval-Augmented Generation (RAG). This system can process PDFs, web-scraped documentation, and other text sources to provide accurate answers about SmartPlant instrumentation.

## 🎯 Features

- **Local Operation**: Runs entirely on your machine - no API costs or internet dependency
- **Multi-format Support**: Handles PDFs, text files, and web-scraped content
- **Smart Retrieval**: Uses semantic search to find relevant documentation
- **Technical Focus**: Optimized for CAD/CAE and engineering design systems
- **Web Interface**: Beautiful Streamlit interface for easy interaction
- **Command Line**: Simple CLI for quick queries and automation

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd smartplant-rag

# Install dependencies
pip install -r requirements.txt
```

### 2. Add Your Documentation

Place your SmartPlant documentation files in the `data/docs/` folder:
- PDF files (`.pdf`)
- Text files (`.txt`, `.md`)
- The system will also automatically scrape Hexagon documentation sites

### 3. Setup the System

```bash
# Setup and index all documents
python main.py --setup
```

### 4. Start Using

**Web Interface (Recommended):**
```bash
streamlit run web_interface.py
```

**Command Line:**
```bash
# Interactive mode
python main.py --interactive

# Single query
python main.py --query "How do I configure a pressure transmitter?"
```

## 📁 Project Structure

```
smartplant-rag/
├── config.py              # Configuration settings
├── document_loader.py     # Document processing and web scraping
├── rag_system.py         # Core RAG implementation
├── main.py               # Command-line interface
├── web_interface.py      # Streamlit web interface
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── data/
    ├── docs/            # Your documentation files
    └── embeddings/      # Vector database and embeddings
```

## 🔧 Configuration

Edit `config.py` to customize:

- **Models**: Change embedding and LLM models
- **Chunking**: Adjust document chunk size and overlap
- **Web Scraping**: Add more Hexagon documentation URLs
- **Performance**: Tune retrieval parameters

### Model Options

**Embedding Models** (for semantic search):
- `sentence-transformers/all-MiniLM-L6-v2` (default - small, fast)
- `sentence-transformers/all-mpnet-base-v2` (better quality, larger)
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (multilingual)

**Language Models** (for text generation):
- `microsoft/DialoGPT-medium` (default - small, conversational)
- `microsoft/DialoGPT-large` (better quality, larger)
- `gpt2-medium` (alternative option)

## 📚 Adding Documentation

### Method 1: Local Files
Simply copy your SmartPlant documentation files to `data/docs/`:
- PDF manuals
- Help files
- Technical specifications
- User guides

### Method 2: Web Scraping
Edit `config.py` and add Hexagon documentation URLs:
```python
HEXAGON_URLS = [
    "https://docs.hexagonppm.com/",
    "https://your-specific-docs-url.com/",
    # Add more URLs here
]
```

### Method 3: Web Interface
Use the Streamlit interface to upload files directly through the browser.

## 💡 Example Queries

Try these example questions:

- "How do I configure a pressure transmitter?"
- "What are the steps for instrument calibration?"
- "How to set up SmartPlant Instrumentation?"
- "What are the system requirements?"
- "How to create a new project?"
- "What is the difference between SmartPlant Instrumentation and SmartPlant P&ID?"
- "How do I import data from other systems?"
- "What are the best practices for instrument tagging?"

## 🔍 How It Works

1. **Document Processing**: PDFs and text files are loaded and chunked into smaller pieces
2. **Embedding Creation**: Each chunk is converted to a numerical vector (embedding)
3. **Vector Storage**: Embeddings are stored in a local ChromaDB vector database
4. **Query Processing**: Your question is converted to an embedding
5. **Semantic Search**: The system finds the most similar document chunks
6. **Answer Generation**: A local LLM generates an answer using the retrieved context

## ⚙️ System Requirements

- **Python**: 3.8 or higher
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 2-5GB for models and embeddings
- **GPU**: Optional but recommended for faster processing

## 🛠️ Troubleshooting

### Common Issues

**"No documents found"**
- Check that files are in `data/docs/` folder
- Verify file extensions are supported (`.pdf`, `.txt`, `.md`)
- Run `python main.py --setup` to rebuild the index

**"Error loading models"**
- Ensure you have enough RAM (8GB+)
- Try using smaller models in `config.py`
- Check internet connection for model downloads

**"Slow performance"**
- Use smaller models in `config.py`
- Reduce chunk size in configuration
- Consider using GPU acceleration

### Performance Optimization

1. **Use smaller models** for faster processing
2. **Adjust chunk size** based on your documents
3. **Enable GPU acceleration** if available
4. **Limit web scraping** to specific URLs

## 🔒 Privacy & Security

- **100% Local**: All processing happens on your machine
- **No Data Sharing**: No information is sent to external services
- **Offline Capable**: Works without internet connection after setup
- **Customizable**: Full control over data and processing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the configuration options
3. Open an issue on GitHub

## 🎯 Why RAG for SmartPlant?

**RAG (Retrieval-Augmented Generation)** is perfect for technical documentation because:

- **Accuracy**: Provides factual answers from your actual documentation
- **Updatability**: Easy to add new documentation without retraining
- **Transparency**: Shows sources for every answer
- **Efficiency**: Small, fast models that run locally
- **Cost-effective**: No API costs or external dependencies

This approach is much more practical than training a custom model from scratch, especially for technical documentation that changes frequently. 