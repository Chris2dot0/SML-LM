import streamlit as st
import os
from pathlib import Path
import json

from rag_system import SmartPlantRAG
from document_loader import DocumentLoader

# Page configuration
st.set_page_config(
    page_title="SmartPlant Documentation Assistant",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .source-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .answer-box {
        background-color: #e8f4fd;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_rag_system():
    """Load the RAG system (cached for performance)."""
    try:
        return SmartPlantRAG()
    except Exception as e:
        st.error(f"Error loading RAG system: {e}")
        return None

def main():
    # Header
    st.markdown('<h1 class="main-header">🏭 SmartPlant Documentation Assistant</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ System Status")
        
        # Check system state
        system_state_file = Path("data/embeddings/system_state.json")
        if system_state_file.exists():
            with open(system_state_file, 'r') as f:
                state = json.load(f)
            
            st.success("✅ System Ready")
            st.info(f"📊 Indexed chunks: {state.get('chunks_count', 'Unknown')}")
            st.info(f"🤖 Model: {state.get('llm_model', 'Unknown')}")
        else:
            st.warning("⚠️ System not set up")
            if st.button("🔄 Setup System"):
                setup_system()
        
        st.header("📚 Quick Actions")
        if st.button("📖 Load New Documents"):
            load_new_documents()
        
        if st.button("🔄 Rebuild Index"):
            rebuild_index()
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 System Info", "📚 Document Management"])
    
    with tab1:
        chat_interface()
    
    with tab2:
        system_info()
    
    with tab3:
        document_management()

def chat_interface():
    """Main chat interface."""
    st.header("💬 Ask about SmartPlant Instrumentation")
    
    # Load RAG system
    rag = load_rag_system()
    if not rag:
        st.error("RAG system not available. Please check the system status.")
        return
    
    # Chat input
    question = st.text_area(
        "Enter your question:",
        placeholder="e.g., How do I configure a pressure transmitter?",
        height=100
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔍 Search", type="primary"):
            if question.strip():
                process_question(rag, question)
            else:
                st.warning("Please enter a question.")
    
    with col2:
        if st.button("💡 Example Questions"):
            show_examples()

def process_question(rag, question):
    """Process a question and display results."""
    with st.spinner("🔍 Searching documentation..."):
        result = rag.query(question)
    
    # Display answer
    st.markdown('<div class="answer-box">', unsafe_allow_html=True)
    st.markdown(f"**Answer:** {result['answer']}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display sources
    if result['sources']:
        st.subheader("📚 Sources")
        for i, source in enumerate(result['sources'][:5], 1):
            with st.expander(f"Source {i}: {source['source']}"):
                st.write(f"**Type:** {source['type']}")
                if source.get('page'):
                    st.write(f"**Page:** {source['page']}")
                if source.get('relevance_score'):
                    st.write(f"**Relevance:** {source['relevance_score']:.2f}")
                
                # Show a preview of the content
                if 'context' in result and result['context']:
                    st.write("**Content Preview:**")
                    st.text(result['context'][:300] + "...")

def show_examples():
    """Show example questions."""
    examples = [
        "How do I configure a pressure transmitter?",
        "What are the steps for instrument calibration?",
        "How to set up SmartPlant Instrumentation?",
        "What are the system requirements?",
        "How to create a new project?",
        "What is the difference between SmartPlant Instrumentation and SmartPlant P&ID?",
        "How do I import data from other systems?",
        "What are the best practices for instrument tagging?"
    ]
    
    st.subheader("💡 Example Questions")
    for example in examples:
        if st.button(example, key=f"example_{example}"):
            st.session_state.example_question = example
            st.rerun()

def system_info():
    """Display system information."""
    st.header("📊 System Information")
    
    # Model information
    st.subheader("🤖 Models")
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("**Embedding Model:**\nsentence-transformers/all-MiniLM-L6-v2")
        st.info("**Vector Database:**\nChromaDB (Local)")
    
    with col2:
        st.info("**Language Model:**\nmicrosoft/DialoGPT-medium")
        st.info("**Storage:**\nLocal embeddings")
    
    # Performance metrics
    st.subheader("📈 Performance")
    system_state_file = Path("data/embeddings/system_state.json")
    if system_state_file.exists():
        with open(system_state_file, 'r') as f:
            state = json.load(f)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Indexed Chunks", state.get('chunks_count', 0))
        with col2:
            st.metric("Documents", len(list(Path("data/docs").rglob("*"))))
        with col3:
            st.metric("Storage", f"{get_directory_size('data/embeddings')} MB")

def document_management():
    """Document management interface."""
    st.header("📚 Document Management")
    
    # Upload new documents
    st.subheader("📤 Upload Documents")
    uploaded_files = st.file_uploader(
        "Choose files",
        type=['pdf', 'txt', 'md'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if st.button("📥 Process Uploaded Files"):
            process_uploaded_files(uploaded_files)
    
    # Document list
    st.subheader("📋 Current Documents")
    docs_dir = Path("data/docs")
    if docs_dir.exists():
        for file_path in docs_dir.rglob("*"):
            if file_path.is_file():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"📄 {file_path.name}")
                with col2:
                    st.write(f"{file_path.stat().st_size / 1024:.1f} KB")
                with col3:
                    if st.button("🗑️", key=f"delete_{file_path}"):
                        delete_document(file_path)

def setup_system():
    """Setup the RAG system."""
    with st.spinner("🚀 Setting up SmartPlant RAG System..."):
        try:
            from main import setup_system as setup
            rag = setup()
            if rag:
                st.success("✅ System setup complete!")
                st.rerun()
            else:
                st.error("❌ Setup failed. Check if documents are available.")
        except Exception as e:
            st.error(f"❌ Setup error: {e}")

def load_new_documents():
    """Load new documents."""
    with st.spinner("📚 Loading documents..."):
        try:
            loader = DocumentLoader()
            documents = loader.load_all_documents()
            st.success(f"✅ Loaded {len(documents)} documents")
        except Exception as e:
            st.error(f"❌ Error loading documents: {e}")

def rebuild_index():
    """Rebuild the document index."""
    with st.spinner("🔄 Rebuilding index..."):
        try:
            rag = SmartPlantRAG()
            loader = DocumentLoader()
            documents = loader.load_all_documents()
            rag.index_documents(documents)
            rag.save_system_state()
            st.success("✅ Index rebuilt successfully!")
        except Exception as e:
            st.error(f"❌ Error rebuilding index: {e}")

def process_uploaded_files(files):
    """Process uploaded files."""
    docs_dir = Path("data/docs")
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    for file in files:
        file_path = docs_dir / file.name
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
    
    st.success(f"✅ Uploaded {len(files)} files")
    st.info("💡 Run 'Rebuild Index' to include new documents")

def delete_document(file_path):
    """Delete a document."""
    try:
        file_path.unlink()
        st.success(f"✅ Deleted {file_path.name}")
        st.rerun()
    except Exception as e:
        st.error(f"❌ Error deleting file: {e}")

def get_directory_size(path):
    """Get directory size in MB."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total_size += os.path.getsize(filepath)
    return round(total_size / (1024 * 1024), 2)

if __name__ == "__main__":
    main() 