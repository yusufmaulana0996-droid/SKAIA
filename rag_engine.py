import chromadb
from chromadb.utils import embedding_functions
import hashlib
import json
import os
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

class RAGEngine:
    def __init__(self, persist_directory="./chroma_db"):
        """Initialize RAG Engine with ChromaDB"""
        self.persist_directory = persist_directory
        
        # Create directory if not exists
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Setup embedding function
        self.embedding_function = self._get_embedding_function()
        
        # Get or create collection
        self.collection_name = "school_documents"
        self.collection = self._get_or_create_collection()
        
    def _get_embedding_function(self):
        """Get appropriate embedding function based on available providers"""
        
        # Option 1: Try Gemini with correct model name
        try:
            gemini_key = os.getenv("GEMINI_API_KEY")
            if gemini_key:
                return embedding_functions.GoogleGenerativeAiEmbeddingFunction(
                    api_key=gemini_key,
                    model_name="models/text-embedding-004"
                )
        except Exception as e:
            st.warning(f"Gemini embedding not available: {e}")
        
        # Option 2: Try sentence-transformers (local, free)
        try:
            return embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
        except Exception as e:
            st.warning(f"SentenceTransformer not available: {e}")
        
        # Option 3: Fallback to simple embedding function
        return None
    
    def _get_or_create_collection(self):
        """Get or create ChromaDB collection"""
        try:
            # Try to get existing collection
            collection = self.client.get_collection(
                name=self.collection_name
            )
            return collection
        except:
            # Create new collection if doesn't exist
            return self.client.create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
    
    def add_documents(self, chunks):
        """
        Add documents to vector store
        Menerima format chunks dari PDFProcessor: List of Dict dengan keys: 'id', 'text', 'source'
        """
        if not chunks:
            return False
        
        try:
            # Extract data from chunks format
            documents = []  # untuk teks
            metadatas = []  # untuk metadata
            ids = []        # untuk ID unik
            
            for chunk in chunks:
                # Pastikan chunk adalah dictionary
                if isinstance(chunk, dict):
                    # Ambil text dari field 'text'
                    text = chunk.get('text', '')
                    if text and len(text.strip()) > 0:
                        documents.append(text)
                        
                        # Buat metadata
                        metadata = {
                            'source': chunk.get('source', 'Unknown'),
                            'chunk_index': chunk.get('chunk_index', 0),
                            'id': chunk.get('id', ''),
                            'timestamp': chunk.get('timestamp', datetime.now().isoformat())
                        }
                        metadatas.append(metadata)
                        
                        # Gunakan ID yang sudah ada atau buat baru
                        doc_id = chunk.get('id', hashlib.md5(text.encode('utf-8')).hexdigest())
                        ids.append(doc_id)
                
                elif isinstance(chunk, str):
                    # Jika chunk berupa string langsung
                    if chunk.strip():
                        documents.append(chunk)
                        doc_id = hashlib.md5(chunk.encode('utf-8')).hexdigest()
                        ids.append(doc_id)
                        metadatas.append({
                            'source': 'direct',
                            'timestamp': datetime.now().isoformat()
                        })
            
            # Add to collection jika ada dokumen
            if documents:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                
                # Save metadata about update
                self._save_update_metadata()
                st.success(f"✅ Berhasil menambahkan {len(documents)} chunks ke database")
                return True
            
            return False
            
        except Exception as e:
            st.error(f"Error adding documents: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
            return False
    
    def search_documents(self, query, n_results=3):
        """Search for relevant documents"""
        if not self.collection:
            return []
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            # Format results
            documents = []
            if results and 'documents' in results and results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    doc_info = {
                        'content': doc,
                        'source': results['metadatas'][0][i].get('source', 'Unknown') if results.get('metadatas') else 'Unknown',
                        'distance': results['distances'][0][i] if results.get('distances') else None
                    }
                    documents.append(doc_info)
            
            return documents
            
        except Exception as e:
            st.error(f"Error searching documents: {str(e)}")
            return []
    
    def generate_rag_prompt(self, original_query, relevant_docs):
        """Generate enhanced prompt with RAG context"""
        if not relevant_docs:
            return original_query
        
        # Build context from relevant documents
        context_parts = []
        for i, doc in enumerate(relevant_docs, 1):
            # Truncate long documents to avoid token limits
            content = doc['content']
            if len(content) > 2000:
                content = content[:2000] + "..."
            context_parts.append(f"[Dokumen {i} dari {doc['source']}]:\n{content}\n")
        
        context = "\n".join(context_parts)
        
        # Create RAG-enhanced prompt
        rag_prompt = f"""BERDASARKAN DOKUMEN SEKOLAH BERIKUT:

{context}

PERTANYAAN: {original_query}

INSTRUKSI:
1. Jawab berdasarkan informasi dari dokumen di atas
2. Jika informasi tidak ada di dokumen, katakan "Berdasarkan dokumen yang tersedia, informasi ini tidak ditemukan"
3. Gunakan bahasa yang ramah dan mudah dipahami
4. Sertakan referensi sumber jika relevan

JAWABAN:"""
        
        return rag_prompt
    
    def clear_store(self):
        """Clear all documents from vector store"""
        try:
            # Delete the collection
            self.client.delete_collection(self.collection_name)
            # Recreate collection
            self.collection = self._get_or_create_collection()
            self._save_update_metadata(clear=True)
            return True
        except Exception as e:
            st.error(f"Error clearing store: {str(e)}")
            return False
    
    def get_stats(self):
        """Get statistics about the vector store"""
        try:
            count = self.collection.count()
            last_updated = self._load_update_metadata()
            return {
                'total_documents': count,
                'last_updated': last_updated
            }
        except:
            return {
                'total_documents': 0,
                'last_updated': 'Unknown'
            }
    
    def _save_update_metadata(self, clear=False):
        """Save metadata about last update"""
        metadata_file = os.path.join(self.persist_directory, "rag_metadata.json")
        
        if clear:
            if os.path.exists(metadata_file):
                os.remove(metadata_file)
            return
        
        metadata = {
            'last_updated': datetime.now().isoformat(),
            'total_documents': self.collection.count() if self.collection else 0
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f)
    
    def _load_update_metadata(self):
        """Load metadata about last update"""
        metadata_file = os.path.join(self.persist_directory, "rag_metadata.json")
        
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
                return metadata.get('last_updated', 'Unknown')
        
        return 'Unknown'
