import streamlit as st
from typing import List, Dict
import random

class EducationRecommender:
    def __init__(self):
        self.career_paths = {
            'Matematika': ['Data Scientist', 'Aktuaris', 'Insinyur', 'Analis Keuangan'],
            'Fisika': ['Insinyur', 'Peneliti', 'Astronom', 'Fisikawan Medis'],
            'Biologi': ['Dokter', 'Peneliti', 'Ahli Gizi', 'Bioteknologi'],
            'Kimia': ['Farmasi', 'Analis Lab', 'Teknik Kimia', 'Food Scientist'],
            'Bahasa': ['Jurnalis', 'Content Writer', 'Penerjemah', 'Diplomat'],
            'Ekonomi': ['Akuntan', 'Business Analyst', 'Financial Advisor', 'Ekonom'],
            'Sejarah': ['Arkeolog', 'Museum Kurator', 'Peneliti Sejarah', 'Dosen'],
            'Geografi': ['GIS Specialist', 'Urban Planner', 'Ahli Lingkungan', 'Geolog'],
            'Sosiologi': ['Sosiolog', 'Social Worker', 'HR', 'Researcher'],
            'Komputer': ['Software Engineer', 'AI Engineer', 'UI/UX Designer', 'Cybersecurity']
        }
        
        self.learning_styles = ['Visual', 'Auditory', 'Kinesthetic', 'Reading/Writing']
        
        self.study_tips = {
            'Visual': [
                'Gunakan mind mapping',
                'Tonton video pembelajaran',
                'Buat diagram dan grafik'
            ],
            'Auditory': [
                'Rekam dan dengarkan materi',
                'Diskusi kelompok',
                'Gunakan mnemonic devices'
            ],
            'Kinesthetic': [
                'Praktik langsung',
                'Gunakan model 3D',
                'Belajar sambil bergerak'
            ],
            'Reading/Writing': [
                'Buat catatan rapi',
                'Baca berbagai sumber',
                'Tulis rangkuman'
            ]
        }
    
    def recommend_career(self, favorite_subjects: List[str], interests: List[str]) -> Dict:
        """Generate career recommendations based on subjects and interests"""
        potential_careers = []
        for subject in favorite_subjects:
            if subject in self.career_paths:
                potential_careers.extend(self.career_paths[subject])
        
        # Remove duplicates and add relevance score
        career_scores = {}
        for career in set(potential_careers):
            count = potential_careers.count(career)
            career_scores[career] = count
        
        # Sort by relevance
        sorted_careers = sorted(career_scores.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'top_careers': [career[0] for career in sorted_careers[:5]],
            'scores': dict(sorted_careers[:5])
        }
    
    def recommend_study_materials(self, subject: str, level: str = "SMA") -> List[Dict]:
        """Recommend study resources"""
        resources = {
            'Matematika': [
                {'type': 'Video', 'name': 'Khan Academy - Mathematics', 'link': 'https://khanacademy.org'},
                {'type': 'Aplikasi', 'name': 'Photomath', 'link': '#'},
                {'type': 'Website', 'name': 'Wolfram Alpha', 'link': 'https://wolframalpha.com'}
            ],
            'Fisika': [
                {'type': 'Simulasi', 'name': 'PhET Interactive', 'link': 'https://phet.colorado.edu'},
                {'type': 'Video', 'name': 'Veritasium', 'link': 'https://youtube.com/veritasium'},
                {'type': 'Website', 'name': 'Physics Classroom', 'link': 'https://physicsclassroom.com'}
            ],
            'default': [
                {'type': 'Video', 'name': 'Khan Academy', 'link': 'https://khanacademy.org'},
                {'type': 'Website', 'name': 'Wikipedia', 'link': 'https://wikipedia.org'},
                {'type': 'Aplikasi', 'name': 'Quizlet', 'link': 'https://quizlet.com'}
            ]
        }
        
        return resources.get(subject, resources['default'])
    
    def suggest_learning_technique(self, learning_style: str) -> List[str]:
        """Suggest learning techniques based on learning style"""
        return self.study_tips.get(learning_style, self.study_tips['Visual'])
