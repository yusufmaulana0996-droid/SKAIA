import os
from typing import List, Dict
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
import hashlib
import json
import streamlit as st
from datetime import datetime

class PDFProcessor:
    def __init__(self, data_folder="data"):
        self.data_folder = data_folder
        self.supported_formats = ['.pdf']
        self.metadata_file = "pdf_metadata.json"
        
        # Create data folder if not exists
        os.makedirs(data_folder, exist_ok=True)
        
    def list_pdfs(self) -> List[str]:
        """List all PDF files in data folder"""
        pdfs = []
        for file in os.listdir(self.data_folder):
            if any(file.lower().endswith(fmt) for fmt in self.supported_formats):
                pdfs.append(os.path.join(self.data_folder, file))
        return pdfs
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from a PDF file"""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract metadata
                metadata = pdf_reader.metadata
                
                # Extract text from each page
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        # Add page marker
                        text += f"\n[Halaman {page_num}]\n{page_text}\n"
                
                # Add file name marker
                filename = os.path.basename(pdf_path)
                text = f"[File: {filename}]\n{text}"
                
        except Exception as e:
            st.error(f"Error extracting PDF {pdf_path}: {str(e)}")
        
        return text
    
    def extract_all_pdfs(self) -> Dict[str, str]:
        """Extract text from all PDFs in data folder"""
        all_texts = {}
        pdf_files = self.list_pdfs()
        
        if not pdf_files:
            st.warning("Tidak ada file PDF di folder data/")
            return all_texts
        
        progress_bar = st.progress(0)
        for i, pdf_path in enumerate(pdf_files):
            filename = os.path.basename(pdf_path)
            st.info(f"Memproses: {filename}")
            
            text = self.extract_text_from_pdf(pdf_path)
            if text.strip():
                all_texts[filename] = text
            
            progress_bar.progress((i + 1) / len(pdf_files))
        
        return all_texts
    
    def split_text_into_chunks(self, texts: Dict[str, str]) -> List[Dict]:
        """Split extracted text into smaller chunks"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # Ukuran per chunk
            chunk_overlap=200,  # Overlap antar chunk
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        all_chunks = []
        
        for filename, text in texts.items():
            chunks = text_splitter.split_text(text)
            
            for i, chunk in enumerate(chunks):
                chunk_data = {
                    'id': f"{filename}_chunk_{i}",
                    'text': chunk,
                    'source': filename,
                    'chunk_index': i,
                    'timestamp': datetime.now().isoformat()
                }
                all_chunks.append(chunk_data)
        
        return all_chunks
    
    def get_file_hash(self, pdf_path: str) -> str:
        """Get MD5 hash of PDF file for caching"""
        with open(pdf_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def check_for_updates(self) -> bool:
        """Check if PDFs have been updated"""
        metadata = self.load_metadata()
        current_hashes = {}
        
        for pdf_path in self.list_pdfs():
            current_hashes[os.path.basename(pdf_path)] = self.get_file_hash(pdf_path)
        
        if metadata.get('file_hashes') != current_hashes:
            self.save_metadata({'file_hashes': current_hashes})
            return True
        
        return False
    
    def load_metadata(self) -> Dict:
        """Load PDF metadata"""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_metadata(self, metadata: Dict):
        """Save PDF metadata"""
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def upload_pdf(self, uploaded_file) -> bool:
        """Handle PDF upload from Streamlit"""
        if uploaded_file is None:
            return False
        
        # Save file
        file_path = os.path.join(self.data_folder, uploaded_file.name)
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"✅ {uploaded_file.name} berhasil diupload!")
        return True
    
    def delete_pdf(self, filename: str) -> bool:
        """Delete a PDF file"""
        file_path = os.path.join(self.data_folder, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
