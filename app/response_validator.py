"""
Response Validator and Quality Checker
======================================
Validates and scores agent responses to ensure quality and accuracy.

Author: Umar Farouk Yunusa
Date: December 23, 2025
"""

from typing import Dict, Any, List, Optional, Tuple
import re
from difflib import SequenceMatcher


class ResponseValidator:
    """
    Validates agent responses for quality, accuracy, and appropriateness.
    """
    
    def __init__(self, llm_client: Any = None):
        """
        Initialize the response validator.
        
        Args:
            llm_client: LLM client for intelligent validation
        """
        self.llm_client = llm_client
        
    def validate_response(
        self, 
        response: str, 
        user_message: str,
        detected_language: str,
        knowledge_context: Optional[List[Dict]] = None,
        intent: str = 'general'
    ) -> Dict[str, Any]:
        """
        Validate a response and return quality metrics.
        
        Args:
            response: The generated response
            user_message: Original user message
            detected_language: Language of the response
            knowledge_context: Knowledge base documents used
            intent: Detected intent
            
        Returns:
            Dictionary with validation results:
                - is_valid: bool
                - confidence_score: float (0-1)
                - issues: List[str]
                - warnings: List[str]
                - suggestions: List[str]
        """
        issues = []
        warnings = []
        suggestions = []
        scores = {}
        
        # 1. Check for empty or too short responses
        if not response or len(response.strip()) < 3:
            issues.append("Response is empty or too short")
            return {
                'is_valid': False,
                'confidence_score': 0.0,
                'issues': issues,
                'warnings': warnings,
                'suggestions': ["Try rephrasing your question", "Ask a more specific question"]
            }
        
        # 2. Check for language mixing
        language_mixing_score = self._check_language_mixing(response, detected_language)
        scores['language_consistency'] = language_mixing_score
        
        if language_mixing_score < 0.7:
            warnings.append(f"Response may contain mixed languages (confidence: {language_mixing_score:.2f})")
        
        # 3. Check for placeholder text or error messages
        placeholder_score = self._check_for_placeholders(response)
        scores['no_placeholders'] = placeholder_score
        
        if placeholder_score < 1.0:
            issues.append("Response contains placeholder text or error messages")
        
        # 4. Check response relevance to question (for factual queries)
        if intent in ['question', 'cultural_query']:
            relevance_score = self._check_relevance(response, user_message, knowledge_context)
            scores['relevance'] = relevance_score
            
            if relevance_score < 0.5:
                warnings.append(f"Response may not be relevant to the question (confidence: {relevance_score:.2f})")
                suggestions.append("Try asking your question differently")
        
        # 5. Check for hallucination indicators (for knowledge-based responses)
        if knowledge_context and intent in ['question', 'cultural_query']:
            hallucination_score = self._check_hallucination(response, knowledge_context)
            scores['grounding'] = hallucination_score
            
            if hallucination_score < 0.6:
                warnings.append("Response may contain information not found in knowledge base")
        
        # 6. Check for uncertainty indicators
        uncertainty_score = self._check_uncertainty_indicators(response)
        scores['certainty'] = uncertainty_score
        
        if uncertainty_score < 0.7:
            warnings.append("Response contains uncertainty markers")
            suggestions.append("The answer may not be completely accurate")
        
        # 7. Check response length appropriateness
        length_score = self._check_response_length(response, intent)
        scores['length_appropriate'] = length_score
        
        if length_score < 0.7:
            warnings.append("Response length may be inappropriate for the question type")
        
        # Calculate overall confidence score (weighted average)
        weights = {
            'language_consistency': 0.2,
            'no_placeholders': 0.15,
            'relevance': 0.25,
            'grounding': 0.25,
            'certainty': 0.1,
            'length_appropriate': 0.05
        }
        
        confidence_score = sum(
            scores.get(key, 1.0) * weight 
            for key, weight in weights.items()
        )
        
        # Determine if valid based on critical issues
        is_valid = len(issues) == 0 and confidence_score >= 0.5
        
        return {
            'is_valid': is_valid,
            'confidence_score': confidence_score,
            'detailed_scores': scores,
            'issues': issues,
            'warnings': warnings,
            'suggestions': suggestions
        }
    
    def _check_language_mixing(self, response: str, expected_language: str) -> float:
        """
        Check if response contains unexpected language mixing.
        
        Returns a score from 0 (mixed) to 1 (consistent).
        """
        # Language-specific patterns
        language_indicators = {
            'ha': ['zan', 'yaya', 'kai', 'kike', 'ba', 'ne', 'ce', 'da', 'ga', 'kuma'],
            'yo': ['mo', 'ni', 'se', 'ti', 'ki', 'je', 'wa', 'ṣe', 'ẹ', 'rẹ'],
            'pcm': ['dey', 'na', 'wetin', 'wey', 'dem', 'go', 'don', 'una', 'no', 'be'],
            'en': ['the', 'is', 'are', 'was', 'were', 'have', 'has', 'will', 'would', 'could']
        }
        
        if expected_language not in language_indicators:
            return 1.0  # Can't validate unknown languages
        
        words = response.lower().split()
        if len(words) == 0:
            return 1.0
        
        expected_indicators = language_indicators[expected_language]
        other_indicators = []
        for lang, indicators in language_indicators.items():
            if lang != expected_language:
                other_indicators.extend(indicators)
        
        expected_matches = sum(1 for word in words if word in expected_indicators)
        other_matches = sum(1 for word in words if word in other_indicators)
        
        if expected_matches + other_matches == 0:
            return 0.8  # Neutral - no clear indicators
        
        consistency_ratio = expected_matches / (expected_matches + other_matches)
        return consistency_ratio
    
    def _check_for_placeholders(self, response: str) -> float:
        """
        Check for placeholder text, error messages, or system artifacts.
        
        Returns 1.0 if clean, 0.0 if placeholders found.
        """
        placeholder_patterns = [
            r'\[.*?\]',  # [placeholder], [ERROR], etc.
            r'<.*?>',    # <placeholder>, <response>, etc.
            r'LLM not configured',
            r'API.*error',
            r'failed to',
            r'unable to',
            r'error:',
            r'exception:',
            r'null',
            r'undefined',
            r'TODO',
            r'FIXME',
            r'\.\.\.',  # Excessive ellipsis
        ]
        
        for pattern in placeholder_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                return 0.0
        
        return 1.0
    
    def _check_relevance(
        self, 
        response: str, 
        question: str,
        knowledge_context: Optional[List[Dict]] = None
    ) -> float:
        """
        Check if response is relevant to the question.
        
        Returns a score from 0 (irrelevant) to 1 (highly relevant).
        """
        # Simple keyword overlap approach
        question_words = set(re.findall(r'\w+', question.lower()))
        response_words = set(re.findall(r'\w+', response.lower()))
        
        # Remove common stop words
        stop_words = {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but', 
                      'in', 'with', 'to', 'for', 'of', 'as', 'by', 'ni', 'na', 'ne', 'da'}
        question_words -= stop_words
        response_words -= stop_words
        
        if not question_words:
            return 0.8  # Can't determine
        
        overlap = len(question_words & response_words)
        relevance = overlap / len(question_words)
        
        return min(relevance * 1.5, 1.0)  # Scale up but cap at 1.0
    
    def _check_hallucination(self, response: str, knowledge_context: List[Dict]) -> float:
        """
        Check if response contains information not in knowledge base.
        
        Returns a score from 0 (likely hallucinated) to 1 (well-grounded).
        """
        if not knowledge_context:
            return 0.5  # Can't verify without context
        
        # Extract all text from knowledge context
        context_text = ' '.join([
            doc.get('content', '') + ' ' + 
            doc.get('title', '') + ' ' + 
            doc.get('text', '')
            for doc in knowledge_context
        ]).lower()
        
        # Check what percentage of response content appears in knowledge base
        response_sentences = re.split(r'[.!?]+', response)
        grounded_sentences = 0
        
        for sentence in response_sentences:
            sentence = sentence.strip().lower()
            if not sentence:
                continue
            
            # Check if key phrases from sentence appear in context
            words = re.findall(r'\w+', sentence)
            if len(words) < 3:
                continue
                
            # Look for 2-3 word phrases
            phrase_found = False
            for i in range(len(words) - 2):
                phrase = ' '.join(words[i:i+3])
                if phrase in context_text:
                    phrase_found = True
                    break
            
            if phrase_found:
                grounded_sentences += 1
        
        total_sentences = len([s for s in response_sentences if s.strip()])
        if total_sentences == 0:
            return 0.5
        
        grounding_score = grounded_sentences / total_sentences
        return grounding_score
    
    def _check_uncertainty_indicators(self, response: str) -> float:
        """
        Check for uncertainty markers in the response.
        
        Returns a score from 0 (very uncertain) to 1 (confident).
        """
        uncertainty_patterns = [
            r"i don't know",
            r"i'm not sure",
            r"might be",
            r"could be",
            r"possibly",
            r"perhaps",
            r"maybe",
            r"uncertain",
            r"not certain",
            r"not enough information",
            r"ban sani ba",  # Hausa: I don't know
            r"mi o mọ",      # Yoruba: I don't know
            r"i no know",    # Pidgin: I don't know
        ]
        
        response_lower = response.lower()
        uncertainty_count = sum(
            1 for pattern in uncertainty_patterns 
            if re.search(pattern, response_lower)
        )
        
        # More uncertainty markers = lower score
        if uncertainty_count == 0:
            return 1.0
        elif uncertainty_count == 1:
            return 0.7
        elif uncertainty_count == 2:
            return 0.4
        else:
            return 0.2
    
    def _check_response_length(self, response: str, intent: str) -> float:
        """
        Check if response length is appropriate for the intent.
        
        Returns a score from 0 (inappropriate) to 1 (appropriate).
        """
        word_count = len(response.split())
        
        # Expected ranges by intent
        expected_ranges = {
            'greeting': (5, 30),
            'casual_conversation': (10, 50),
            'translation': (5, 100),
            'question': (20, 150),
            'cultural_query': (30, 200),
            'content_generation': (50, 500),
            'general': (10, 100)
        }
        
        min_words, max_words = expected_ranges.get(intent, (10, 100))
        
        if word_count < min_words * 0.5:
            return 0.3  # Too short
        elif word_count > max_words * 2:
            return 0.5  # Too long
        elif min_words <= word_count <= max_words:
            return 1.0  # Perfect
        else:
            return 0.8  # Close enough
    
    def suggest_improvements(
        self,
        response: str,
        validation_results: Dict[str, Any],
        detected_language: str
    ) -> Optional[str]:
        """
        Suggest improvements if response quality is low.
        
        Returns:
            Improved response or None if no improvements needed
        """
        if validation_results['confidence_score'] >= 0.8:
            return None  # Response is good enough
        
        if not self.llm_client:
            return None  # Can't improve without LLM
        
        # Build improvement prompt
        issues = validation_results.get('issues', [])
        warnings = validation_results.get('warnings', [])
        
        language_map = {
            'en': 'English',
            'ha': 'Hausa',
            'pcm': 'Nigerian Pidgin',
            'yo': 'Yoruba'
        }
        language_name = language_map.get(detected_language, 'English')
        
        prompt = f"""You are a quality assurance expert for a Nigerian multilingual AI assistant.

A response was generated but has quality issues:

Original Response: "{response}"
Language: {language_name}
Confidence Score: {validation_results['confidence_score']:.2f}

Issues Found:
{chr(10).join(f"- {issue}" for issue in issues) if issues else "None"}

Warnings:
{chr(10).join(f"- {warning}" for warning in warnings) if warnings else "None"}

Task: Improve this response by:
1. Fixing any language mixing (keep it 100% {language_name})
2. Making it more natural and conversational
3. Ensuring it's factually grounded
4. Removing any placeholders or errors
5. Making it more confident if appropriate

Return ONLY the improved {language_name} response, nothing else:"""
        
        try:
            import os
            provider = os.getenv("WAZOBIA_LLM_PROVIDER", "anthropic").lower()
            
            if provider == "anthropic":
                result = self.llm_client.messages.create(
                    model=os.getenv("WAZOBIA_DEFAULT_MODEL", "claude-3-5-sonnet-20241022"),
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                return result.content[0].text.strip()
            
            elif provider in ["openai", "groq"]:
                result = self.llm_client.chat.completions.create(
                    model=os.getenv("WAZOBIA_DEFAULT_MODEL", "llama-3.3-70b-versatile"),
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000
                )
                return result.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"Error improving response: {e}")
            return None


def get_response_validator(llm_client: Any = None) -> ResponseValidator:
    """
    Factory function to get a ResponseValidator instance.
    
    Args:
        llm_client: Optional LLM client for intelligent validation
        
    Returns:
        ResponseValidator instance
    """
    return ResponseValidator(llm_client=llm_client)
