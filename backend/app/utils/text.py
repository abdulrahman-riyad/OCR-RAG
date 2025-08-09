import re
from typing import List, Dict, Tuple, Optional
import nltk
from collections import Counter

# Download required NLTK data (run once)
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

class TextProcessor:
    """Text processing and analysis utilities"""
    
    def __init__(self):
        try:
            from nltk.corpus import stopwords
            self.stop_words = set(stopwords.words('english'))
        except:
            self.stop_words = set()
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep mathematical symbols
        text = re.sub(r'[^\w\s\-+*/=().,;:!?\[\]{}∫∑∏√∞αβγδθλμπσφω]', '', text)
        
        # Fix common OCR errors
        corrections = {
            'rn': 'm',
            'l ': 'I ',
            ' l ': ' I ',
            '0': 'O',  # Context-dependent, simplified here
        }
        
        for wrong, right in corrections.items():
            text = text.replace(wrong, right)
        
        return text.strip()
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[Tuple[str, int]]:
        """Extract keywords from text"""
        # Tokenize
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter stop words
        words = [w for w in words if w not in self.stop_words and len(w) > 2]
        
        # Count frequencies
        word_freq = Counter(words)
        
        return word_freq.most_common(top_n)
    
    def detect_language(self, text: str) -> str:
        """Simple language detection"""
        # Check for common English words
        english_words = {'the', 'is', 'at', 'which', 'on', 'and', 'a', 'to'}
        words = set(text.lower().split())
        
        if len(words.intersection(english_words)) > 2:
            return 'en'
        
        # Add more language detection as needed
        return 'unknown'
    
    def split_into_sections(self, text: str) -> List[Dict[str, str]]:
        """Split text into logical sections"""
        sections = []
        
        # Split by double newlines or numbering
        patterns = [
            r'\n\n+',  # Double newlines
            r'\n\d+\.',  # Numbered sections
            r'\n[A-Z][a-z]+:',  # Title case followed by colon
        ]
        
        current_section = []
        lines = text.split('\n')
        
        for line in lines:
            # Check if line looks like a section header
            if (line.isupper() and len(line) > 3) or \
               re.match(r'^\d+\.', line) or \
               re.match(r'^[A-Z][a-z]+:', line):
                
                if current_section:
                    sections.append({
                        'title': current_section[0],
                        'content': '\n'.join(current_section[1:])
                    })
                current_section = [line]
            else:
                current_section.append(line)
        
        # Add last section
        if current_section:
            sections.append({
                'title': current_section[0] if current_section else 'Untitled',
                'content': '\n'.join(current_section[1:]) if len(current_section) > 1 else ''
            })
        
        return sections
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities (simplified version)"""
        entities = {
            'dates': [],
            'numbers': [],
            'equations': [],
            'urls': [],
            'emails': []
        }
        
        # Date patterns
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b'
        ]
        for pattern in date_patterns:
            entities['dates'].extend(re.findall(pattern, text))
        
        # Numbers
        entities['numbers'] = re.findall(r'\b\d+\.?\d*\b', text)
        
        # Simple equation patterns
        entities['equations'] = re.findall(r'[a-zA-Z]+\s*=\s*[^,\n]+', text)
        
        # URLs
        entities['urls'] = re.findall(r'https?://[^\s]+', text)
        
        # Emails
        entities['emails'] = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        
        return entities
    
    def calculate_readability_score(self, text: str) -> float:
        """Calculate simple readability score"""
        sentences = re.split(r'[.!?]+', text)
        words = re.findall(r'\b\w+\b', text)
        
        if not sentences or not words:
            return 0.0
        
        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Simple readability formula
        score = 206.835 - 1.015 * avg_sentence_length - 84.6 * (avg_word_length / 5)
        
        # Normalize to 0-100
        return max(0, min(100, score))

# Global instance
text_processor = TextProcessor()