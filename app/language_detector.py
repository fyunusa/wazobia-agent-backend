"""
Language Detection Service
=========================
Detect and identify Nigerian languages (Hausa, Nigerian Pidgin, Yoruba) and English.

Author: Umar Farouk Yunusa
Date: December 15, 2025
"""

import re
from typing import Dict, Optional, List, Tuple
from collections import Counter


class LanguageDetector:
    """
    Detects Nigerian languages (Hausa, Pidgin, Yoruba) and English using
    keyword matching, character patterns, and linguistic features.
    """
    
    def __init__(self):
        # Language-specific keywords and patterns
        self.hausa_keywords = {
            # Common Hausa words
            'da', 'ba', 'na', 'ta', 'ya', 'za', 'ko', 'amma', 'kuma', 'don',
            'ina', 'yaya', 'kai', 'shi', 'ita', 'mu', 'ku', 'su',
            'wannan', 'wancan', 'wane', 'wace', 'yana', 'tana', 'suna',
            'sannu', 'yaushe', 'ina', 'kana', 'aikawa', 'zuwa', 'daga',
            # Greetings
            'salama', 'barka', 'gaisuwa', 'alheri', 'lafiya'
        }
        
        self.pidgin_keywords = {
            # Distinctive Pidgin words
            'dey', 'dem', 'wey', 'una', 'wetin', 'abi', 'sha', 'sef',
            'wahala', 'belle', 'chop', 'yab', 'yarn', 'gist', 'kpai',
            'pipul', 'pesin', 'pikin', 'haus', 'mek', 'fit', 'don',
            'go', 'come', 'see', 'hear', 'tok', 'no', 'dey', 'abeg',
            # Common constructions
            'how far', 'na so', 'na im', 'na wa', 'e good', 'make',
            'for where', 'wetin dey', 'how you dey', 'i dey'
        }
        
        self.yoruba_keywords = {
            # Common Yoruba words (both with and without diacritics)
            'ni', 'ti', 'ko', 'si', 'bi', 'je', 'se', 'ninu', 'lati',
            'mo', 'o', 'a', 'won', 'awa', 'eyin', 'awon', 'bawo',
            'jowo', 'emi', 'iwo', 'oun', 'wa', 'ki', 'lo', 'lon',
            'shele', 'sele', 'wi', 'ri', 'fun', 'wa', 'ba', 'pe',
            # Common everyday words
            'owo', 'ooo', 'abi', 'kan', 'waso', 'muri', 'nkan',
            'mi', 're', 'fi', 'gba', 'mu', 'ra', 'lo', 'bo',
            'de', 'fe', 'ran', 'gb', 'to', 'da', 'ja', 'pa',
            # With diacritics
            'ẹ', 'ọ', 'ṣ', 'ń', 'è', 'ò', 'à', 'ì', 'ù',
            # Common phrases (without diacritics for better matching)
            'bawo ni', 'se daadaa', 'o dabo', 'se dada', 'daadaa',
            'ki lon', 'ki lo', 'kini', 'kilode', 'kiloni',
            # Greetings (both with and without diacritics)
            'e kaaro', 'e kaasan', 'e ku irole', 'pele', 'e ku ise',
            'ẹ káàárọ̀', 'ẹ káàásán', 'ẹ kú irọlẹ́', 'pẹlẹ', 'ẹ kú iṣẹ́'
        }
        
        self.english_keywords = {
            'the', 'is', 'are', 'was', 'were', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'should', 'could',
            'can', 'may', 'might', 'must', 'this', 'that', 'these',
            'those', 'what', 'which', 'who', 'where', 'when', 'why',
            'how', 'hello', 'hi', 'please', 'thank', 'you'
        }
        
        # Character patterns specific to each language
        self.yoruba_diacritics = set('ẹọṣńèòàìùáéíóúâêîôûḿǹṅ')
        
        # Common greetings for quick detection
        self.greetings = {
            'ha': ['sannu', 'barka', 'ina kwana', 'ina wuni', 'yaya dai'],
            'pcm': ['how far', 'wetin dey', 'how you dey', 'abeg', 'na wa'],
            'yo': ['bawo', 'bawo ni', 'ki lon', 'ki lo', 'pele', 'pẹlẹ', 
                   'ẹ káàárọ̀', 'e kaaro', 'se daadaa', 'se dada', 'o dabo'],
            'en': ['hello', 'hi', 'good morning', 'good afternoon', 'how are you']
        }
    
    def detect_language(self, text: str) -> Dict[str, any]:
        """
        Detect the language of the given text.
        
        Args:
            text: Input text to analyze
        
        Returns:
            Dictionary containing:
                - language: Detected language code (ha, pcm, yo, en, unknown)
                - confidence: Confidence score (0.0 to 1.0)
                - scores: Individual scores for each language
                - is_mixed: Boolean indicating if text appears to be mixed language
        
        Example:
            detector = LanguageDetector()
            result = detector.detect_language("Sannu, yaya kuke?")
            # {'language': 'ha', 'confidence': 0.85, ...}
        """
        if not text or not text.strip():
            return {
                'language': 'unknown',
                'confidence': 0.0,
                'scores': {},
                'is_mixed': False
            }
        
        # Normalize text
        normalized_text = text.lower().strip()
        
        # Check for greetings first (quick detection)
        greeting_lang = self._check_greetings(normalized_text)
        if greeting_lang:
            return {
                'language': greeting_lang,
                'confidence': 0.9,
                'scores': {greeting_lang: 0.9},
                'is_mixed': False
            }
        
        # Calculate scores for each language
        scores = {
            'ha': self._score_hausa(normalized_text),
            'pcm': self._score_pidgin(normalized_text),
            'yo': self._score_yoruba(text),  # Use original for diacritics
            'en': self._score_english(normalized_text)
        }
        
        # Determine primary language
        max_lang = max(scores, key=scores.get)
        max_score = scores[max_lang]
        
        # Check for mixed language
        sorted_scores = sorted(scores.values(), reverse=True)
        is_mixed = len(sorted_scores) > 1 and sorted_scores[1] > 0.2
        
        # Determine confidence
        confidence = self._calculate_confidence(max_score, sorted_scores)
        
        # If score is too low, mark as unknown
        # Lower threshold to handle code-switching better
        if max_score < 0.15:
            max_lang = 'unknown'
            confidence = 0.0
        # If English score is high but another Nigerian language scores higher, prefer Nigerian language
        elif max_lang == 'en' and any(scores[lang] > 0.2 for lang in ['ha', 'pcm', 'yo']):
            # Find the Nigerian language with highest score
            nigerian_langs = {k: v for k, v in scores.items() if k in ['ha', 'pcm', 'yo']}
            max_lang = max(nigerian_langs, key=nigerian_langs.get)
            max_score = nigerian_langs[max_lang]
            confidence = self._calculate_confidence(max_score, sorted_scores)
        
        return {
            'language': max_lang,
            'confidence': confidence,
            'scores': scores,
            'is_mixed': is_mixed
        }
    
    def _check_greetings(self, text: str) -> Optional[str]:
        """Check if text starts with a common greeting."""
        text_lower = text.lower()
        
        for lang, greetings in self.greetings.items():
            for greeting in greetings:
                if text_lower.startswith(greeting):
                    return lang
        
        return None
    
    def _score_hausa(self, text: str) -> float:
        """Calculate Hausa language score."""
        words = re.findall(r'\b\w+\b', text)
        if not words:
            return 0.0
        
        # Count Hausa keywords
        hausa_count = sum(1 for word in words if word in self.hausa_keywords)
        
        # Hausa-specific patterns
        pattern_score = 0.0
        
        # Common Hausa verb patterns (yana, tana, suna, etc.)
        if re.search(r'\b(ya|ta|su|mu|ku)na\b', text):
            pattern_score += 0.2
        
        # Hausa question words
        if re.search(r'\b(yaya|ina|yaushe|wane|wace|wanda)\b', text):
            pattern_score += 0.1
        
        # Calculate final score
        keyword_score = hausa_count / len(words)
        total_score = min(1.0, (keyword_score * 0.7) + (pattern_score * 0.3))
        
        return total_score
    
    def _score_pidgin(self, text: str) -> float:
        """Calculate Nigerian Pidgin score."""
        words = re.findall(r'\b\w+\b', text)
        if not words:
            return 0.0
        
        # Count Pidgin keywords
        pidgin_count = sum(1 for word in words if word in self.pidgin_keywords)
        
        # Pidgin-specific patterns
        pattern_score = 0.0
        
        # Common Pidgin constructions
        pidgin_patterns = [
            r'\b(wetin|wahala|abi|sha|sef)\b',
            r'\b(dem|una)\b',
            r'\bdey\b',
            r'\b(pipul|pesin|pikin)\b',
            r'\b(mek|fit)\s+\w+',
            r'\bhow\s+(far|you\s+dey)',
            r'\b(na|e)\s+(so|good|bad)',
        ]
        
        for pattern in pidgin_patterns:
            if re.search(pattern, text):
                pattern_score += 0.15
        
        # Pidgin verb constructions (e.g., "don go", "go chop")
        if re.search(r'\b(don|go|come|dey)\s+\w+', text):
            pattern_score += 0.1
        
        # Calculate final score
        keyword_score = pidgin_count / len(words)
        total_score = min(1.0, (keyword_score * 0.6) + (pattern_score * 0.4))
        
        return total_score
    
    def _score_yoruba(self, text: str) -> float:
        """Calculate Yoruba score (uses original text for diacritics)."""
        words = re.findall(r'\b\w+\b', text.lower())
        if not words:
            return 0.0
        text_lower = text.lower()
        
        # Count Yoruba keywords
        yoruba_count = sum(1 for word in words if word in self.yoruba_keywords)
        
        # Check for Yoruba diacritics (strong indicator)
        diacritic_score = 0.0
        diacritic_count = sum(1 for char in text if char in self.yoruba_diacritics)
        if diacritic_count > 0:
            # Strong indicator of Yoruba
            diacritic_score = min(0.5, diacritic_count * 0.1)
        
        # Yoruba-specific patterns
        pattern_score = 0.0
        
        # Common Yoruba phrases (without diacritics)
        yoruba_phrases = [
            r'\b(bawo\s+ni|bawo)\b',           # How are you
            r'\b(ki\s+lo?n?|ki\s+lo)\b',       # What/How (ki lon, ki lo)
            r'\b(she?le|sele)\b',              # Happen/What's up
            r'\b(se\s+da+da+|se\s+dada)\b',   # Are you fine
            r'\b(pe?le?)\b',                   # Sorry/greeting
            r'\b(o\s+dabo|odabo)\b',          # Goodbye
            r'\b(e\s+kaaro|e\s+kaasan)\b',    # Good morning/afternoon
        ]
        
        for phrase in yoruba_phrases:
            if re.search(phrase, text_lower):
                pattern_score += 0.2
        
        # Yoruba pronouns and verb patterns
        if re.search(r'\b(mo|emi|iwo|oun|awa|eyin|won|awon)\b', text_lower):
            pattern_score += 0.1
        
        # Yoruba emphasis particles and common words
        if re.search(r'\b(ooo|abi|kan|owo|nkan)\b', text_lower):
            pattern_score += 0.15
        
        # Yoruba question words
        if re.search(r'\b(ki|kini|kilode|kiloni|bawo|nibo)\b', text_lower):
            pattern_score += 0.15
        
        # Calculate final score
        keyword_score = yoruba_count / len(words)
        # Give more weight to keyword matches for code-switching scenarios
        total_score = min(1.0, (keyword_score * 0.4) + (diacritic_score * 0.2) + (pattern_score * 0.4))
        
        return total_score
    
    def _score_english(self, text: str) -> float:
        """Calculate English score."""
        words = re.findall(r'\b\w+\b', text)
        if not words:
            return 0.0
        
        # Count English keywords
        english_count = sum(1 for word in words if word in self.english_keywords)
        
        # English-specific patterns
        pattern_score = 0.0
        
        # Common English constructions
        english_patterns = [
            r'\b(the|a|an)\s+\w+',
            r'\b(is|are|was|were)\b',
            r'\b(have|has|had)\b',
            r'\b(will|would|should|could)\b',
            r'\b(this|that|these|those)\b',
        ]
        
        for pattern in english_patterns:
            if re.search(pattern, text):
                pattern_score += 0.1
        
        # Calculate final score
        keyword_score = english_count / len(words)
        total_score = min(1.0, (keyword_score * 0.7) + (pattern_score * 0.3))
        
        return total_score
    
    def _calculate_confidence(self, max_score: float, sorted_scores: List[float]) -> float:
        """
        Calculate confidence based on score distribution.
        High confidence if there's a clear winner.
        """
        if max_score < 0.3:
            return 0.2
        
        # Calculate gap between top and second scores
        if len(sorted_scores) > 1:
            gap = max_score - sorted_scores[1]
            # Higher gap = higher confidence
            confidence = min(1.0, max_score * (0.5 + gap * 0.5))
        else:
            confidence = max_score
        
        return confidence
    
    def detect_languages_in_text(self, text: str) -> List[Dict[str, any]]:
        """
        Detect multiple languages if text contains code-switching.
        
        Args:
            text: Input text to analyze
        
        Returns:
            List of detected languages with their segments
        """
        # Split by sentences
        sentences = re.split(r'[.!?]+', text)
        
        results = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                detection = self.detect_language(sentence)
                results.append({
                    'text': sentence,
                    **detection
                })
        
        return results
    
    def get_language_name(self, language_code: str) -> str:
        """
        Get full language name from code.
        
        Args:
            language_code: Language code (ha, pcm, yo, en)
        
        Returns:
            Full language name
        """
        names = {
            'ha': 'Hausa',
            'pcm': 'Nigerian Pidgin',
            'yo': 'Yoruba',
            'en': 'English',
            'unknown': 'Unknown'
        }
        return names.get(language_code, 'Unknown')


# Singleton instance
_detector_instance = None


def get_language_detector() -> LanguageDetector:
    """
    Get the singleton LanguageDetector instance.
    
    Returns:
        LanguageDetector instance
    """
    global _detector_instance
    
    if _detector_instance is None:
        _detector_instance = LanguageDetector()
    
    return _detector_instance
