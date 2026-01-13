"""
Skill Extractor Service
=======================

Service for extracting skills from resume text using NLP.
"""

import re
from typing import List, Dict, Set
from loguru import logger

# Try to import NLP libraries
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except:
    nlp = None
    logger.warning("spaCy model not loaded. Using keyword-based extraction.")


class SkillExtractorService:
    """
    Service for extracting skills from text using NLP and keyword matching.
    """
    
    # Comprehensive skills database
    SKILLS_DATABASE = {
        # Programming Languages
        "python": "technical",
        "javascript": "technical",
        "typescript": "technical",
        "java": "technical",
        "c++": "technical",
        "c#": "technical",
        "go": "technical",
        "golang": "technical",
        "rust": "technical",
        "ruby": "technical",
        "php": "technical",
        "swift": "technical",
        "kotlin": "technical",
        "scala": "technical",
        "r": "technical",
        "matlab": "technical",
        "sql": "technical",
        
        # Web Technologies
        "html": "technical",
        "css": "technical",
        "react": "technical",
        "reactjs": "technical",
        "react.js": "technical",
        "angular": "technical",
        "vue": "technical",
        "vuejs": "technical",
        "vue.js": "technical",
        "nodejs": "technical",
        "node.js": "technical",
        "express": "technical",
        "django": "technical",
        "flask": "technical",
        "fastapi": "technical",
        "spring": "technical",
        "spring boot": "technical",
        "asp.net": "technical",
        "tailwindcss": "technical",
        "bootstrap": "technical",
        "sass": "technical",
        "webpack": "technical",
        "nextjs": "technical",
        "next.js": "technical",
        
        # Databases
        "mysql": "technical",
        "postgresql": "technical",
        "mongodb": "technical",
        "redis": "technical",
        "elasticsearch": "technical",
        "sqlite": "technical",
        "oracle": "technical",
        "cassandra": "technical",
        "dynamodb": "technical",
        
        # Cloud & DevOps
        "aws": "technical",
        "amazon web services": "technical",
        "azure": "technical",
        "gcp": "technical",
        "google cloud": "technical",
        "docker": "technical",
        "kubernetes": "technical",
        "k8s": "technical",
        "terraform": "technical",
        "ansible": "technical",
        "jenkins": "technical",
        "ci/cd": "technical",
        "github actions": "technical",
        "gitlab ci": "technical",
        "linux": "technical",
        "unix": "technical",
        "bash": "technical",
        
        # Data Science & ML
        "machine learning": "technical",
        "deep learning": "technical",
        "artificial intelligence": "technical",
        "ai": "technical",
        "ml": "technical",
        "tensorflow": "technical",
        "pytorch": "technical",
        "keras": "technical",
        "scikit-learn": "technical",
        "sklearn": "technical",
        "pandas": "technical",
        "numpy": "technical",
        "scipy": "technical",
        "matplotlib": "technical",
        "data analysis": "technical",
        "data science": "technical",
        "nlp": "technical",
        "natural language processing": "technical",
        "computer vision": "technical",
        "opencv": "technical",
        "neural networks": "technical",
        "transformers": "technical",
        "bert": "technical",
        "gpt": "technical",
        "llm": "technical",
        "huggingface": "technical",
        
        # Tools & Platforms
        "git": "technical",
        "github": "technical",
        "gitlab": "technical",
        "jira": "technical",
        "confluence": "technical",
        "slack": "technical",
        "figma": "technical",
        "postman": "technical",
        "swagger": "technical",
        "graphql": "technical",
        "rest api": "technical",
        "restful": "technical",
        "microservices": "technical",
        "agile": "methodological",
        "scrum": "methodological",
        "kanban": "methodological",
        
        # Soft Skills
        "leadership": "soft",
        "communication": "soft",
        "teamwork": "soft",
        "problem solving": "soft",
        "problem-solving": "soft",
        "critical thinking": "soft",
        "time management": "soft",
        "project management": "soft",
        "analytical": "soft",
        "creative": "soft",
        "detail-oriented": "soft",
        "self-motivated": "soft",
        "adaptability": "soft",
        "collaboration": "soft",
        "mentoring": "soft",
        "presentation": "soft",
    }
    
    # Skill aliases
    SKILL_ALIASES = {
        "reactjs": "react",
        "react.js": "react",
        "vuejs": "vue",
        "vue.js": "vue",
        "nodejs": "node.js",
        "nextjs": "next.js",
        "golang": "go",
        "k8s": "kubernetes",
        "postgres": "postgresql",
        "mongo": "mongodb",
        "sklearn": "scikit-learn",
        "tf": "tensorflow",
    }
    
    async def extract(self, text: str) -> List[str]:
        """
        Extract skills from text.
        
        Args:
            text: Resume text
            
        Returns:
            List of extracted skills
        """
        if not text:
            return []
        
        # Normalize text
        text_lower = text.lower()
        
        # Extract using keyword matching
        keyword_skills = self._extract_by_keywords(text_lower)
        
        # Extract using NLP if available
        if nlp:
            nlp_skills = self._extract_by_nlp(text)
            keyword_skills.update(nlp_skills)
        
        # Normalize and deduplicate
        normalized = self._normalize_skills(keyword_skills)
        
        return list(normalized)
    
    def _extract_by_keywords(self, text: str) -> Set[str]:
        """Extract skills using keyword matching."""
        found_skills = set()
        
        for skill in self.SKILLS_DATABASE.keys():
            # Build regex pattern for the skill
            # Handle special characters in skill names
            pattern = r'\b' + re.escape(skill) + r'\b'
            
            if re.search(pattern, text, re.IGNORECASE):
                found_skills.add(skill)
        
        return found_skills
    
    def _extract_by_nlp(self, text: str) -> Set[str]:
        """Extract skills using spaCy NLP."""
        found_skills = set()
        
        try:
            doc = nlp(text)
            
            # Extract noun phrases as potential skills
            for chunk in doc.noun_chunks:
                chunk_text = chunk.text.lower().strip()
                
                # Check if it matches a known skill
                if chunk_text in self.SKILLS_DATABASE:
                    found_skills.add(chunk_text)
            
            # Extract named entities
            for ent in doc.ents:
                ent_text = ent.text.lower().strip()
                
                if ent_text in self.SKILLS_DATABASE:
                    found_skills.add(ent_text)
                    
        except Exception as e:
            logger.warning(f"NLP extraction error: {e}")
        
        return found_skills
    
    def _normalize_skills(self, skills: Set[str]) -> Set[str]:
        """Normalize skill names using aliases."""
        normalized = set()
        
        for skill in skills:
            # Check if there's an alias
            if skill in self.SKILL_ALIASES:
                normalized.add(self.SKILL_ALIASES[skill])
            else:
                normalized.add(skill)
        
        return normalized
    
    def get_skill_category(self, skill: str) -> str:
        """Get the category of a skill."""
        skill_lower = skill.lower()
        
        # Check alias first
        if skill_lower in self.SKILL_ALIASES:
            skill_lower = self.SKILL_ALIASES[skill_lower]
        
        return self.SKILLS_DATABASE.get(skill_lower, "other")
    
    def categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """Categorize skills by type."""
        categorized = {
            "technical": [],
            "soft": [],
            "methodological": [],
            "other": []
        }
        
        for skill in skills:
            category = self.get_skill_category(skill)
            categorized[category].append(skill)
        
        return categorized
