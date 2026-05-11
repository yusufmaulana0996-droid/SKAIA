import streamlit as st
from datetime import datetime
import json

class ChatMemory:
    def __init__(self):
        self.init_session()
    
    def init_session(self):
        """Initialize session state for memory"""
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'user_profile' not in st.session_state:
            st.session_state.user_profile = {
                'name': '',
                'class': '',
                'favorite_subjects': [],
                'deadlines': [],
                'scores': {},
                'interests': []
            }
        if 'conversation_context' not in st.session_state:
            st.session_state.conversation_context = {
                'current_topic': None,
                'questions_asked': 0,
                'last_subject': None
            }
    
    @property
    def user_profile(self):
        """Get user profile from session state"""
        return st.session_state.user_profile
    
    @property
    def conversation_context(self):
        """Get conversation context from session state"""
        return st.session_state.conversation_context
    
    def add_message(self, role, content):
        """Add message to chat history"""
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.chat_history.append(message)
    
    def get_recent_context(self, n=5):
        """Get recent conversation context"""
        return st.session_state.chat_history[-n:]
    
    def update_profile(self, key, value):
        """Update user profile"""
        st.session_state.user_profile[key] = value
    
    def add_deadline(self, task, date):
        """Add deadline reminder"""
        st.session_state.user_profile['deadlines'].append({
            'task': task,
            'date': date,
            'reminded': False
        })
    
    def get_upcoming_deadlines(self):
        """Get deadlines that haven't passed"""
        today = datetime.now()
        upcoming = []
        for deadline in st.session_state.user_profile['deadlines']:
            deadline_date = datetime.strptime(deadline['date'], "%Y-%m-%d")
            if deadline_date >= today and not deadline['reminded']:
                upcoming.append(deadline)
        return upcoming
    
    def clear_history(self):
        """Clear chat history but keep profile"""
        st.session_state.chat_history = []
        st.session_state.conversation_context = {
            'current_topic': None,
            'questions_asked': 0,
            'last_subject': None
        }
