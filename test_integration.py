from pdf_processor import PDFProcessor
from rag_engine import RAGEngine
import streamlit as st

# Test PDF Processor
print("Testing PDF Processor...")
pdf_proc = PDFProcessor(data_folder="data")

# Create test PDF if needed
test_pdf_path = "data/test.pdf"
if not os.path.exists(test_pdf_path):
    print("Buat file PDF test dulu ya!")

# Extract PDFs
texts = pdf_proc.extract_all_pdfs()
print(f"Extracted {len(texts)} PDFs")

# Split into chunks
chunks = pdf_proc.split_text_into_chunks(texts)
print(f"Created {len(chunks)} chunks")
print(f"Sample chunk: {chunks[0] if chunks else 'None'}")

# Test RAG Engine
print("\nTesting RAG Engine...")
rag = RAGEngine()

# Add documents
if chunks:
    success = rag.add_documents(chunks)
    print(f"Add documents result: {success}")
    
    # Test search
    results = rag.search_documents("test")
    print(f"Search results: {len(results)} found")
