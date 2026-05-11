import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Page Configuration
    PAGE_TITLE = "SKAIA - SMK AI Assistant"
    PAGE_ICON = "🤖"
    LAYOUT = "wide"
    SCHOOL_NAME = "SMKN 1 GUNUNGPUTRI"
    SCHOOL_SHORT = "SKAIA"  # Nama bot
    
    # AI Model Configuration
    MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "gemini")  # gemini, groq, deepseek, ollama
    
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    #DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    
    # Ollama Configuration (local)
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")  # atau mistral, codellama, dll
    
    # Model options for each provider
    GEMINI_MODELS = ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash" , "gemini-3.1-flash-lite"]
    GROQ_MODELS = ["mixtral-8x7b-32768", "llama3-70b-8192", "llama3-8b-8192", "gemma2-9b-it"]
    #DEEPSEEK_MODELS = ["deepseek-chat", "deepseek-coder"]
    OLLAMA_MODELS = ["llama2", "mistral", "codellama", "phi", "neural-chat"]
    
    # Default model for each provider
    DEFAULT_GEMINI_MODEL = "gemini-3.1-flash-lite"
    DEFAULT_GROQ_MODEL = "mixtral-8x7b-32768"
    #DEFAULT_DEEPSEEK_MODEL = "deepseek-chat"
    DEFAULT_OLLAMA_MODEL = "llama2"
    
    # Current selected model
    SELECTED_MODEL = os.getenv("SELECTED_MODEL", DEFAULT_GEMINI_MODEL)
    
    # AI Parameters
    TEMPERATURE = 0.7
    MAX_TOKENS = 1000
    TOP_P = 0.9
    
    # RAG Configuration
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    VECTOR_STORE_PATH = "./chroma_db"
    
    # Subjects list
    SUBJECTS = ["Produktif", "Matematika", "Fisika", "Kimia", "Biologi", "Bahasa Indonesia", 
                "Bahasa Inggris", "Sejarah", "Geografi", "Ekonomi", "Sosiologi"]
