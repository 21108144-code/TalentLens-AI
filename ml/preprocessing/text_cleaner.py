"""
Text Cleaner Module
===================

Text preprocessing utilities for NLP pipeline.
"""

import re
import string
from typing import List, Optional

# Try to import NLP libraries
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.stem import WordNetLemmatizer
    
    # Download required resources
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)
    
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet', quiet=True)
    
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False


class TextCleaner:
    """
    Text preprocessing utilities for cleaning and normalizing text.
    """
    
    def __init__(self):
        if NLTK_AVAILABLE:
            self.stop_words = set(stopwords.words('english'))
            self.lemmatizer = WordNetLemmatizer()
        else:
            # Basic stop words fallback
            self.stop_words = {
                'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves',
                'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him',
                'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its',
                'itself', 'they', 'them', 'their', 'theirs', 'themselves',
                'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those',
                'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
                'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as',
                'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about',
                'against', 'between', 'into', 'through', 'during', 'before',
                'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in',
                'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then',
                'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all',
                'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
                'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
                'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'
            }
            self.lemmatizer = None
    
    def clean_text(
        self,
        text: str,
        lowercase: bool = True,
        remove_punctuation: bool = True,
        remove_numbers: bool = False,
        remove_stopwords: bool = True,
        lemmatize: bool = True
    ) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Input text
            lowercase: Convert to lowercase
            remove_punctuation: Remove punctuation marks
            remove_numbers: Remove numeric characters
            remove_stopwords: Remove common stop words
            lemmatize: Apply lemmatization
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Lowercase
        if lowercase:
            text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\.\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove numbers
        if remove_numbers:
            text = re.sub(r'\d+', '', text)
        
        # Remove punctuation
        if remove_punctuation:
            # Keep some punctuation that might be meaningful
            text = re.sub(r'[^\w\s\-\+\#]', ' ', text)
        
        # Tokenize
        tokens = self._tokenize(text)
        
        # Remove stopwords
        if remove_stopwords:
            tokens = [t for t in tokens if t not in self.stop_words]
        
        # Lemmatize
        if lemmatize and self.lemmatizer:
            tokens = [self.lemmatizer.lemmatize(t) for t in tokens]
        
        # Remove extra whitespace
        text = ' '.join(tokens)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        if NLTK_AVAILABLE:
            try:
                return word_tokenize(text)
            except:
                pass
        
        # Fallback to simple split
        return text.split()
    
    def extract_sentences(self, text: str) -> List[str]:
        """Extract sentences from text."""
        if NLTK_AVAILABLE:
            try:
                from nltk.tokenize import sent_tokenize
                return sent_tokenize(text)
            except:
                pass
        
        # Fallback: split on sentence-ending punctuation
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace in text."""
        return ' '.join(text.split())
    
    def remove_special_characters(self, text: str, keep_chars: str = "") -> str:
        """Remove special characters from text."""
        pattern = f'[^a-zA-Z0-9\\s{re.escape(keep_chars)}]'
        return re.sub(pattern, '', text)


def clean_resume_text(text: str) -> str:
    """Convenience function for cleaning resume text."""
    cleaner = TextCleaner()
    return cleaner.clean_text(
        text,
        lowercase=True,
        remove_punctuation=True,
        remove_numbers=False,  # Keep numbers for years, etc.
        remove_stopwords=True,
        lemmatize=True
    )


def clean_job_description(text: str) -> str:
    """Convenience function for cleaning job descriptions."""
    cleaner = TextCleaner()
    return cleaner.clean_text(
        text,
        lowercase=True,
        remove_punctuation=True,
        remove_numbers=False,
        remove_stopwords=True,
        lemmatize=True
    )
