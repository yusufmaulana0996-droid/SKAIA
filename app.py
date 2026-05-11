import streamlit as st
import google.generativeai as genai
from groq import Groq
from openai import OpenAI
import requests
import json
import os
from dotenv import load_dotenv
from datetime import datetime
import base64

from config import Config
from memory import ChatMemory
from recommender import EducationRecommender
from prompts import SYSTEM_PROMPT, RECOMMENDATION_PROMPT
from pdf_processor import PDFProcessor
from rag_engine import RAGEngine

# Load environment
load_dotenv()

# Page config
st.set_page_config(
    page_title=Config.PAGE_TITLE,
    page_icon=Config.PAGE_ICON,
    layout=Config.LAYOUT
)

# Custom system prompt untuk SKAIA
CUSTOM_SYSTEM_PROMPT = """Kamu adalah **SKAIA** (SMK AI Assistant), asisten AI resmi dari **SMKN 1 Gunungputri**.

Identitas kamu:
- Nama: SKAIA
- Institusi: SMKN 1 Gunungputri (Bogor, Jawa Barat)
- Tugas: Membantu siswa SMK dalam belajar, memberikan informasi sekolah, dan membantu tugas-tugas akademik

Kepribadian kamu:
- Ramah, sabar, dan penuh semangat
- Menggunakan bahasa Indonesia yang baik dan santai
- Suka memberikan motivasi kepada siswa
- Fokus pada pendidikan SMK dan pengembangan karir

Aturan penting:
1. Perkenalkan dirimu sebagai SKAIA dari SMKN 1 Gunungputri
2. Bantu siswa dengan pertanyaan pelajaran SMK
3. Berikan tips belajar yang praktis
4. Motivasi siswa untuk terus belajar dan berkembang
5. Jangan pernah mengaku sebagai AI dari sekolah lain

Ingat: Kamu adalah SKAIA, asisten AI SMKN 1 Gunungputri. Bukan dari sekolah lain!"""

# Function to load background image
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Custom CSS with light theme and background image
def load_css():
    # Try to load background image if exists
    bg_image_path = "images/wallpaper.jpg"
    bg_image_base64 = ""
    if os.path.exists(bg_image_path):
        bg_image_base64 = get_base64_of_bin_file(bg_image_path)
        bg_image_css = f"""
        .stApp {{
            background-image: url("data:image/jpg;base64,{bg_image_base64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        """
    else:
        bg_image_css = """
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        """
    
    st.markdown(f"""
    <style>
        {bg_image_css}
        
        /* Main container styling */
        .main-header {{
            text-align: center;
            padding: 1.5rem;
            background: linear-gradient(135deg, #4A90E2, #357ABD);
            color: white;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        /* Chat message styling */
        .stChatMessage {{
            background-color: rgba(255, 255, 255, 0.95) !important;
            border-radius: 15px !important;
            margin-bottom: 10px !important;
            padding: 15px !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
        }}
        
        /* User message styling */
        [data-testid="stChatMessage"]:has(div:contains("user")) {{
            background: linear-gradient(135deg, #E8F0FE, #D4E4FC) !important;
            border-left: 4px solid #4A90E2 !important;
        }}
        
        /* Assistant message styling */
        [data-testid="stChatMessage"]:has(div:contains("assistant")) {{
            background: linear-gradient(135deg, #F0F9FF, #E0F0FF) !important;
            border-left: 4px solid #357ABD !important;
        }}
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%) !important;
            border-right: 1px solid #dee2e6 !important;
            box-shadow: 2px 0 5px rgba(0,0,0,0.05) !important;
        }}
        
        /* Button styling */
        .stButton > button {{
            background: linear-gradient(135deg, #4A90E2, #357ABD) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 8px 16px !important;
            transition: all 0.3s ease !important;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
        }}
        
        /* Input field styling */
        .stTextInput > div > div > input, .stTextArea > div > div > textarea {{
            background-color: white !important;
            border: 1px solid #ced4da !important;
            border-radius: 8px !important;
        }}
        
        /* Select box styling */
        .stSelectbox > div > div {{
            background-color: white !important;
            border-radius: 8px !important;
        }}
        
        /* Expander styling */
        .streamlit-expanderHeader {{
            background-color: #f8f9fa !important;
            border-radius: 8px !important;
            color: #4A90E2 !important;
        }}
        
        /* Alert boxes */
        .deadline-alert {{
            background: linear-gradient(135deg, #FFF3CD, #FFE9A7);
            border-left: 4px solid #FFC107;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }}
        
        .success-alert {{
            background: linear-gradient(135deg, #D4EDDA, #C8E6D9);
            border-left: 4px solid #28A745;
            padding: 15px;
            border-radius: 10px;
            margin: 10px 0;
        }}
        
        .recommendation-box {{
            background: linear-gradient(135deg, rgba(74,144,226,0.1), rgba(53,125,186,0.1));
            border: 2px solid #4A90E2;
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
        }}
        
        .rag-badge {{
            background: linear-gradient(135deg, #28A745, #20C997);
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            display: inline-block;
        }}
        
        .model-badge {{
            background: linear-gradient(135deg, #4A90E2, #357ABD);
            color: white;
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 0.7rem;
            display: inline-block;
        }}
        
        /* Card styling */
        .card {{
            background-color: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin: 10px 0;
        }}
        
        /* Info box styling */
        .stAlert {{
            background-color: rgba(255,255,255,0.95) !important;
            border-radius: 10px !important;
        }}
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {{
            color: #2C3E50 !important;
        }}
        
        /* Markdown text */
        p, li, span {{
            color: #2C3E50 !important;
        }}
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background-color: rgba(255,255,255,0.9);
            border-radius: 8px 8px 0 0;
            padding: 10px 20px;
        }}
        
        /* Chat input styling - make it cleaner */
        .stChatInputContainer {{
            padding: 10px !important;
            background-color: rgba(255,255,255,0.95) !important;
            border-radius: 10px !important;
            margin-top: 10px !important;
        }}
        
        .stChatInputContainer > div {{
            border: 1px solid #ced4da !important;
            border-radius: 10px !important;
        }}
        
        .stChatInputContainer textarea {{
            background-color: white !important;
            border-radius: 10px !important;
            font-size: 14px !important;
        }}
        
        /* Disable form submit on enter for chat input */
        .stChatInputContainer form {{
            margin: 0 !important;
            padding: 0 !important;
        }}
    </style>
    """, unsafe_allow_html=True)

# Initialize components
memory = ChatMemory()
recommender = EducationRecommender()
pdf_processor = PDFProcessor(data_folder="data")
rag_engine = RAGEngine(persist_directory="./chroma_db")

# Initialize session state
if 'rag_enabled' not in st.session_state:
    st.session_state.rag_enabled = True
if 'vector_store_ready' not in st.session_state:
    st.session_state.vector_store_ready = False
if 'pdf_files' not in st.session_state:
    st.session_state.pdf_files = pdf_processor.list_pdfs()
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
if 'show_profile' not in st.session_state:
    st.session_state.show_profile = False
if 'show_career' not in st.session_state:
    st.session_state.show_career = False
if 'show_study_rec' not in st.session_state:
    st.session_state.show_study_rec = False
if 'show_tips' not in st.session_state:
    st.session_state.show_tips = False
if 'profile_initialized' not in st.session_state:
    st.session_state.profile_initialized = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'selected_model_provider' not in st.session_state:
    st.session_state.selected_model_provider = Config.MODEL_PROVIDER
if 'selected_model_name' not in st.session_state:
    st.session_state.selected_model_name = Config.SELECTED_MODEL
if 'last_prompt' not in st.session_state:
    st.session_state.last_prompt = ""
if 'db_load_shown' not in st.session_state:
    st.session_state.db_load_shown = False

# Load CSS
load_css()

# Initialize AI Model with multiple providers
@st.cache_resource
def get_ai_model(provider=None, model_name=None):
    """Initialize AI model based on provider selection"""
    provider = provider or st.session_state.selected_model_provider
    model_name = model_name or st.session_state.selected_model_name
    
    if provider == 'gemini':
        if not Config.GEMINI_API_KEY:
            st.error("🔑 Gemini API key not found! Check your .env file")
            return None, None
        genai.configure(api_key=Config.GEMINI_API_KEY)
        return genai.GenerativeModel(model_name), provider
    
    elif provider == 'groq':
        if not Config.GROQ_API_KEY:
            st.error("🔑 GROQ API key not found! Check your .env file")
            return None, None
        client = Groq(api_key=Config.GROQ_API_KEY)
        return client, provider
    
    elif provider == 'ollama':
        return "ollama", provider
    
    else:
        st.error(f"❌ Unknown provider: {provider}")
        return None, None

def generate_response(prompt, system_prompt=None, use_rag=True):
    """Generate AI response with optional RAG enhancement and multi-provider support"""
    
    # Gunakan custom system prompt untuk SKAIA
    if system_prompt is None:
        system_prompt = CUSTOM_SYSTEM_PROMPT
    
    # Get recent context
    recent_messages = memory.get_recent_context(5)
    
    # RAG Enhancement
    relevant_docs = []
    if use_rag and st.session_state.rag_enabled and st.session_state.vector_store_ready:
        relevant_docs = rag_engine.search_documents(prompt, n_results=3)
        if relevant_docs:
            prompt = rag_engine.generate_rag_prompt(prompt, relevant_docs)
    
    # Format messages for AI
    formatted_messages = [{"role": "system", "content": system_prompt}]
    
    # Add relevant reminders
    deadlines = memory.get_upcoming_deadlines()
    if deadlines:
        deadline_reminder = "\n📅 Pengingat deadline:\n"
        for d in deadlines[:3]:
            deadline_reminder += f"- {d['task']} (Batas: {d['date']})\n"
        formatted_messages.append({"role": "system", "content": deadline_reminder})
    
    # Add recent conversation context
    for msg in recent_messages:
        formatted_messages.append({"role": msg['role'], "content": msg['content']})
    
    # Add current prompt
    formatted_messages.append({"role": "user", "content": prompt})
    
    try:
        model_obj, provider = get_ai_model()
        if model_obj is None:
            return "Maaf, model AI tidak tersedia. Periksa konfigurasi API key."
        
        response_text = ""
        
        # Gemini
        if provider == 'gemini':
            gemini_messages = []
            for msg in formatted_messages:
                gemini_messages.append(f"{msg['role']}: {msg['content']}")
            full_prompt = "\n".join(gemini_messages)
            
            response = model_obj.generate_content(
                full_prompt,
                generation_config={
                    'temperature': Config.TEMPERATURE,
                    'max_output_tokens': Config.MAX_TOKENS,
                    'top_p': Config.TOP_P
                }
            )
            response_text = response.text
        
        # Groq
        elif provider == 'groq':
            response = model_obj.chat.completions.create(
                model=st.session_state.selected_model_name,
                messages=formatted_messages,
                temperature=Config.TEMPERATURE,
                max_tokens=Config.MAX_TOKENS,
                top_p=Config.TOP_P
            )
            response_text = response.choices[0].message.content
        
        # Ollama (local)
        elif provider == 'ollama':
            response = requests.post(
                f"{Config.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": st.session_state.selected_model_name,
                    "prompt": "\n".join([f"{m['role']}: {m['content']}" for m in formatted_messages]),
                    "stream": False,
                    "options": {
                        "temperature": Config.TEMPERATURE,
                        "num_predict": Config.MAX_TOKENS,
                        "top_p": Config.TOP_P
                    }
                },
                timeout=60
            )
            if response.status_code == 200:
                response_text = response.json()['response']
            else:
                response_text = f"Error: Ollama server returned {response.status_code}. Pastikan Ollama running."
        
        # Pastikan response tidak menyebutkan nama sekolah lain
        response_text = response_text.replace("SmartEduBot", "SKAIA")
        response_text = response_text.replace("smartEduBot", "SKAIA")
        response_text = response_text.replace("SMA 88 Cerdas Bangsa", "SMKN 1 Gunungputri")
        response_text = response_text.replace("SMA 88", "SMKN 1 Gunungputri")
        response_text = response_text.replace("Cerdas Bangsa", "SMKN 1 Gunungputri")
        
        return response_text
    
    except Exception as e:
        st.error(f"❌ Error generating response with {provider}: {str(e)}")
        return f"Maaf, terjadi kesalahan pada sistem. Silakan coba lagi."

# Auto-initialize vector store on startup - tanpa pesan berhasil yang mengganggu
if not st.session_state.initialized:
    with st.spinner("🔄 Mempersiapkan SKAIA..."):
        pdf_files = pdf_processor.list_pdfs()
        
        if pdf_files:
            try:
                if pdf_processor.check_for_updates() or rag_engine.get_stats()['total_documents'] == 0:
                    texts = pdf_processor.extract_all_pdfs()
                    if texts:
                        chunks = pdf_processor.split_text_into_chunks(texts)
                        if chunks:
                            if rag_engine.add_documents(chunks):
                                st.session_state.vector_store_ready = True
                                st.session_state.pdf_files = pdf_files
                                # Tidak menampilkan pesan sukses yang mengganggu
                            else:
                                st.session_state.rag_enabled = False
                        else:
                            st.session_state.rag_enabled = False
                    else:
                        st.session_state.rag_enabled = False
                else:
                    st.session_state.vector_store_ready = True
                    st.session_state.pdf_files = pdf_files
            except Exception as e:
                st.session_state.rag_enabled = False
        else:
            # Tidak ada pesan info yang mengganggu
            pass
    
    st.session_state.initialized = True
    st.session_state.db_load_shown = True
    st.rerun()

# Sidebar
with st.sidebar:
    if os.path.exists("SKAIA.png"):
        st.image("SKAIA.png", width=100)
    else:
        st.markdown("## 🤖 SKAIA")
    st.markdown(f"*Asisten AI untuk SMKN 1 Gunungputri*")
    
    # Model Selection Section
    st.markdown("### 🤖 Model AI")
    
    # Provider selection
    provider_options = ["gemini", "ollama"]
    provider_labels = {
        "gemini": "Google Gemini",
        "ollama": "Ollama (Local/Free)"
    }
    
    current_provider = st.session_state.selected_model_provider
    if current_provider not in provider_options:
        current_provider = "gemini"
        st.session_state.selected_model_provider = "gemini"
    
    selected_provider = st.selectbox(
        "Pilih Provider AI",
        options=provider_options,
        format_func=lambda x: provider_labels.get(x, x),
        index=provider_options.index(current_provider) if current_provider in provider_options else 0
    )
    
    # Model selection based on provider
    if selected_provider == 'gemini':
        model_options = Config.GEMINI_MODELS
    else:  # ollama
        model_options = Config.OLLAMA_MODELS
    
    default_index = 0
    if st.session_state.selected_model_name in model_options:
        default_index = model_options.index(st.session_state.selected_model_name)
    
    selected_model = st.selectbox(
        "Pilih Model",
        options=model_options,
        index=default_index
    )
    
    if selected_provider != st.session_state.selected_model_provider or selected_model != st.session_state.selected_model_name:
        st.session_state.selected_model_provider = selected_provider
        st.session_state.selected_model_name = selected_model
        st.cache_resource.clear()
        st.rerun()
    
    if selected_provider == 'ollama':
        st.info("🔄 **Ollama Mode** - Pastikan Ollama running di local")
        st.code(f"ollama pull {selected_model}", language="bash")
    
    if st.session_state.rag_enabled and st.session_state.vector_store_ready:
        st.markdown('<span class="rag-badge">🧠 RAG Aktif</span>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # User Profile Section
    st.markdown("### 👤 Profil Siswa")
    
    if st.button("📝 Edit Profil" if st.session_state.profile_initialized else "📝 Buat Profil", use_container_width=True):
        st.session_state.show_profile = not st.session_state.show_profile
    
    if st.session_state.show_profile:
        with st.form("profile_form"):
            name = st.text_input("Nama", value=memory.user_profile.get('name', ''))
            kelas = st.selectbox("Kelas", ["X", "XI", "XII"])
            jurusan = st.selectbox("Jurusan", ["RPL", "ELEKTRO", "KIMIA", "LAS", "MESIN"])
            
            favorite = st.multiselect(
                "Mata Pelajaran Favorit",
                Config.SUBJECTS,
                default=memory.user_profile.get('favorite_subjects', [])
            )
            
            learning_style = st.selectbox(
                "Gaya Belajar",
                recommender.learning_styles,
                index=recommender.learning_styles.index(
                    memory.user_profile.get('learning_style', 'Visual')
                ) if 'learning_style' in memory.user_profile else 0
            )
            
            interests = st.text_area("Minat/Hobi", value=', '.join(memory.user_profile.get('interests', [])))
            
            submitted = st.form_submit_button("💾 Simpan Profil", use_container_width=True)
            if submitted:
                if name:
                    memory.update_profile('name', name)
                    memory.update_profile('class', kelas)
                    memory.update_profile('major', jurusan)
                    memory.update_profile('favorite_subjects', favorite)
                    memory.update_profile('learning_style', learning_style)
                    memory.update_profile('interests', [i.strip() for i in interests.split(',') if i.strip()])
                    st.session_state.profile_initialized = True
                    st.success("✅ Profil berhasil disimpan!")
                    st.session_state.show_profile = False
                    st.rerun()
                else:
                    st.error("❌ Nama harus diisi!")
    
    st.markdown("---")
    
    # Features
    st.markdown("### 🚀 Fitur")
    tab1, tab2 = st.tabs(["⚙️ Menu", "📊 Rekomendasi"])
    
    with tab1:
        if st.button("🎯 Rekomendasi Karir", use_container_width=True):
            if st.session_state.profile_initialized:
                st.session_state.show_career = True
            else:
                st.warning("⚠️ Isi profil dulu ya!")
        
        if st.button("📚 Rekomendasi Belajar", use_container_width=True):
            if st.session_state.profile_initialized:
                st.session_state.show_study_rec = True
            else:
                st.warning("⚠️ Isi profil dulu ya!")
        
        if st.button("🎯 Tips Belajar", use_container_width=True):
            if st.session_state.profile_initialized:
                st.session_state.show_tips = True
            else:
                st.warning("⚠️ Isi profil dulu ya!")
    
    with tab2:
        st.markdown("**Filter Rekomendasi:**")
        rec_subject = st.selectbox("Mata Pelajaran", ["Semua"] + Config.SUBJECTS)
    
    st.markdown("---")
    
    # Deadline Manager
    st.markdown("### 📅 Deadline Manager")
    with st.expander("➕ Tambah Deadline"):
        with st.form("deadline_form"):
            task = st.text_input("Tugas/Kegiatan")
            deadline = st.date_input("Tanggal Deadline")
            if st.form_submit_button("💾 Simpan Deadline", use_container_width=True):
                if task and deadline:
                    memory.add_deadline(task, deadline.strftime("%Y-%m-%d"))
                    st.success("✅ Deadline tersimpan!")
                    st.rerun()
    
    upcoming = memory.get_upcoming_deadlines()
    if upcoming:
        st.markdown("**📅 Deadline Mendatang:**")
        for d in upcoming[:5]:
            st.markdown(f"📌 {d['task']} - {d['date']}")
    
    st.markdown("---")
    
    if st.button("🗑️ Hapus Riwayat Chat", use_container_width=True):
        memory.clear_history()
        st.session_state.chat_history = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("Made with ❤️ by Yusuf Maulana")
    
    model_display = f"{provider_labels.get(selected_provider, selected_provider)} - {selected_model}"
    st.markdown(f"🤖 **Model Aktif:** {model_display}")

# Main Content
st.markdown('<div class="main-header"><h1>🤖 SKAIA</h1><p>SMK AI Assistant - SMKN 1 Gunungputri</p></div>', unsafe_allow_html=True)

if st.session_state.profile_initialized and memory.user_profile.get('name'):
    st.markdown(f"### 👋 Selamat datang, **{memory.user_profile['name']}**!")
    
    with st.expander("📋 Profil Singkat"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**Kelas:** {memory.user_profile.get('class', '-')}")
            st.markdown(f"**Jurusan:** {memory.user_profile.get('major', '-')}")
        with col2:
            fav_subjects = memory.user_profile.get('favorite_subjects', [])
            st.markdown(f"**Mapel Favorit:** {', '.join(fav_subjects) if fav_subjects else '-'}")
        with col3:
            st.markdown(f"**Gaya Belajar:** {memory.user_profile.get('learning_style', '-')}")

# Show Recommendations (sama seperti sebelumnya, tidak berubah)
if st.session_state.get('show_career', False):
    st.markdown("## 🎯 Rekomendasi Karir")
    with st.container():
        st.markdown('<div class="recommendation-box">', unsafe_allow_html=True)
        
        fav_subjects = memory.user_profile.get('favorite_subjects', [])
        interests = memory.user_profile.get('interests', [])
        
        if fav_subjects:
            career_rec = recommender.recommend_career(fav_subjects, interests)
            
            st.markdown("### 🚀 Karir yang Cocok untuk Kamu:")
            for i, career in enumerate(career_rec['top_careers'], 1):
                score = career_rec['scores'][career]
                stars = "⭐" * min(score, 5)
                st.markdown(f"**{i}. {career}** {stars}")
            
            career_prompt = f"""
            Berikan penjelasan motivasi untuk pilihan karir ini:
            {', '.join(career_rec['top_careers'][:3])}
            
            Untuk siswa SMK dengan minat: {', '.join(interests) if interests else 'belum ditentukan'}
            
            Jelaskan:
            1. Mengapa karir ini cocok
            2. Jurusan kuliah yang sesuai
            3. Skill yang perlu dikembangkan
            """
            
            with st.spinner("🤔 Menganalisis rekomendasi karir..."):
                explanation = generate_response(career_prompt, use_rag=False)
                st.markdown("### 💡 Insight:")
                st.markdown(explanation)
        else:
            st.warning("⚠️ Pilih mata pelajaran favorit di profil untuk rekomendasi karir")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("❌ Tutup Rekomendasi Karir"):
        st.session_state.show_career = False
        st.rerun()

if st.session_state.get('show_study_rec', False):
    st.markdown("## 📚 Rekomendasi Materi Belajar")
    subject = st.selectbox("Pilih Mata Pelajaran", Config.SUBJECTS, key="study_subject")
    resources = recommender.recommend_study_materials(subject)
    
    col1, col2, col3 = st.columns(3)
    columns = [col1, col2, col3]
    
    for i, resource in enumerate(resources):
        with columns[i % 3]:
            st.markdown(f"**{resource['type']}**: {resource['name']}")
    
    study_prompt = f"Berikan tips belajar {subject} untuk siswa SMK yang efektif dan menyenangkan."
    
    with st.spinner("🔍 Mencari tips belajar terbaik..."):
        study_tips = generate_response(study_prompt)
        st.markdown("### 💡 Tips Belajar:")
        st.markdown(study_tips)
    
    if st.button("❌ Tutup Rekomendasi Belajar"):
        st.session_state.show_study_rec = False
        st.rerun()

if st.session_state.get('show_tips', False):
    st.markdown("## 🎯 Tips Belajar Personal")
    
    learning_style = memory.user_profile.get('learning_style', 'Visual')
    tips = recommender.suggest_learning_technique(learning_style)
    
    st.markdown(f"### Gaya Belajar Kamu: **{learning_style}**")
    st.markdown("### Teknik Belajar yang Direkomendasikan:")
    for i, tip in enumerate(tips, 1):
        st.markdown(f"{i}. ✅ {tip}")
    
    tips_prompt = f"Berikan tips belajar tambahan untuk siswa dengan gaya belajar {learning_style}."
    
    with st.spinner("🧠 Menyusun tips personal..."):
        personal_tips = generate_response(tips_prompt, use_rag=False)
        st.markdown("### 💡 Tips Tambahan dari SKAIA:")
        st.markdown(personal_tips)
    
    if st.button("❌ Tutup Tips Belajar"):
        st.session_state.show_tips = False
        st.rerun()

# Chat Interface
st.markdown("---")
st.markdown("### 💬 Chat dengan SKAIA - SMKN 1 Gunungputri")

if st.session_state.rag_enabled and st.session_state.vector_store_ready:
    st.info("🧠 **RAG Aktif** - SKAIA dapat mengakses dokumen sekolah")

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "timestamp" in message:
            st.caption(f"_{message['timestamp']}_")

# Chat input
with st.form(key="chat_form", clear_on_submit=True):
    prompt = st.text_input("Tanyakan sesuatu tentang sekolah...", key="chat_input", label_visibility="collapsed")
    submitted = st.form_submit_button("Kirim", use_container_width=False)
    
    if submitted and prompt and prompt != st.session_state.last_prompt:
        st.session_state.last_prompt = prompt
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.chat_history.append({"role": "user", "content": prompt, "timestamp": timestamp})
        memory.add_message("user", prompt)
        
        with st.chat_message("user"):
            st.markdown(prompt)
            st.caption(f"_{timestamp}_")
        
        with st.chat_message("assistant"):
            with st.spinner(f"🤔 SKAIA sedang berpikir..."):
                response = generate_response(prompt, use_rag=st.session_state.rag_enabled)
                st.markdown(response)
                st.caption(f"_{datetime.now().strftime('%H:%M:%S')}_")
        
        st.session_state.chat_history.append({"role": "assistant", "content": response, "timestamp": timestamp})
        memory.add_message("assistant", response)
        memory.conversation_context['questions_asked'] = memory.conversation_context.get('questions_asked', 0) + 1
        
        st.rerun()

if memory.user_profile.get('name') and memory.get_upcoming_deadlines():
    with st.expander("📅 ⚠️ Pengingat Deadline Penting!"):
        st.markdown('<div class="deadline-alert">', unsafe_allow_html=True)
        st.markdown("**Jangan lupa deadline berikut:**")
        for deadline in memory.get_upcoming_deadlines()[:5]:
            st.markdown(f"- 📌 {deadline['task']} ({deadline['date']})")
        st.markdown('</div>', unsafe_allow_html=True)

with st.expander("❓ Bantuan & Fitur"):
    st.markdown("""
    ### Fitur SKAIA - SMKN 1 Gunungputri:
    
    **💬 Chat AI:**
    - Tanya jawab seputar pelajaran SMK
    - Konsultasi masalah belajar
    - Informasi sekolah
    
    **🤖 Multi-Model AI:**
    - **Google Gemini**: Model canggih dari Google
    - **Ollama**: Model lokal GRATIS
    
    **🧠 RAG System:**
    - Menggunakan dokumen PDF sebagai sumber pengetahuan
    - SKAIA akan mencari jawaban dari dokumen yang tersedia
    
    **📅 Deadline Manager:**
    - Catat deadline tugas
    - Pengingat otomatis
    
    **🎯 Rekomendasi:**
    - Karir berdasarkan minat
    - Materi belajar
    - Tips belajar personal
    """)

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>SKAIA - SMK AI Assistant SMKN 1 Gunungputri v3.0 | Yusuf Maulana</p>
</div>
""", unsafe_allow_html=True)
