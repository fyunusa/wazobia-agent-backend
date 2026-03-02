"""
Fallback Handler
================
Handles cases where the agent is uncertain or cannot provide a good answer.

Author: Umar Farouk Yunusa  
Date: December 23, 2025
"""

from typing import Dict, Any, List, Optional


class FallbackHandler:
    """
    Handles fallback scenarios when the agent cannot provide a confident response.
    """
    
    def __init__(self):
        """Initialize the fallback handler."""
        self.fallback_messages = self._initialize_fallback_messages()
        self.suggestion_templates = self._initialize_suggestions()
    
    def _initialize_fallback_messages(self) -> Dict[str, Dict[str, str]]:
        """Initialize fallback messages in different languages."""
        return {
            'insufficient_knowledge': {
                'en': "I don't have enough information in my knowledge base to answer that question accurately. Could you try asking in a different way, or ask about something else?",
                'ha': "Ban sami isasshen bayani a cikin ma'ajin ilimi na don amsa wannan tambayar daidai ba. Za ka iya sake tambaya ta wata hanya, ko kuma ka tambaye ni wani abu dabam?",
                'yo': "Mi o ni alaye to peye ninu ise-imo mi lati dahun ibeere yẹn daradara. Ṣe o le tun beere ni ọna miiran, tabi beere nipa ohun miiran?",
                'pcm': "I no get enough information for my knowledge base to answer dat question well well. You fit try ask am another way, or make you ask me something else?"
            },
            'unclear_question': {
                'en': "I'm not quite sure what you're asking. Could you please rephrase your question or provide more details?",
                'ha': "Ban fahimci abin da kake tambaya sosai ba. Za ka iya sake faɗi tambayar ko kuma ka ƙara bayani?",
                'yo': "Mi ko ye ohun ti o n beere daadaa. Ṣe o le tun sọ ibeere rẹ ni ọna miiran tabi fi alaye sii kun?",
                'pcm': "I no too understand wetin you dey ask. You fit talk the question another way or add more detail?"
            },
            'language_mixing_detected': {
                'en': "I noticed your message mixes different languages. For better results, try asking in one language (Hausa, Yoruba, Pidgin, or English).",
                'ha': "Na lura cewa saƙonka ya haɗa harsunan dabam-dabam. Don samun sakamakon da ya fi kyau, gwada tambaya cikin harshe ɗaya (Hausa, Yoruba, Pidgin, ko Turanci).",
                'yo': "Mo rii pe ifiranṣẹ rẹ pọ awọn ede pupọ. Fun abajade to dara julọ, gbiyanju beere ni ede kan (Hausa, Yoruba, Pidgin, tabi English).",
                'pcm': "I see say your message mix different languages. For better result, try ask am for one language (Hausa, Yoruba, Pidgin, or English)."
            },
            'error_occurred': {
                'en': "I encountered an issue while processing your request. Please try again.",
                'ha': "Na fuskanci matsala yayin aiwatar da buƙatarka. Don Allah sake gwadawa.",
                'yo': "Mo pade iṣoro nigba ti mo n ṣe ibeere rẹ. Jọwọ gbiyanju lẹẹkansi.",
                'pcm': "I get problem when I dey try process your request. Abeg try again."
            },
            'low_confidence': {
                'en': "I'm not very confident about this answer. The information might not be accurate. You may want to verify from other sources.",
                'ha': "Ba ni da cikakkiyar tabbaci game da wannan amsa. Bayanin zai iya zama ba daidai ba. Kana iya bincika daga wasu majiyoyi.",
                'yo': "Mi ko ni igboya pupọ nipa idahun yii. Alaye le ma jẹ daradara. O le fẹ ṣayẹwo lati awọn orisun miiran.",
                'pcm': "I no too sure about this answer. The information fit no correct. You fit like check from other places."
            }
        }
    
    def _initialize_suggestions(self) -> Dict[str, List[str]]:
        """Initialize suggestion templates for different scenarios."""
        return {
            'question_not_found': {
                'en': [
                    "Try asking about Nigerian news or current events",
                    "Ask about Nigerian culture, traditions, or languages",
                    "Request a translation between Nigerian languages",
                    "Ask for help with Hausa, Yoruba, or Pidgin phrases"
                ],
                'ha': [
                    "Yi tambaya game da labarai ko al'amuran Najeriya",
                    "Tambaya game da al'adun Najeriya, al'adunmu, ko harsunanmu",
                    "Nemi fassara tsakanin harsunan Najeriya",
                    "Nemi taimako game da jimlolin Hausa, Yoruba, ko Pidgin"
                ],
                'yo': [
                    "Beere nipa awọn iroyin Naijiria tabi awọn iṣẹlẹ lọwọlọwọ",
                    "Beere nipa aṣa Naijiria, awọn aṣa, tabi awọn ede",
                    "Beere fun itumọ laarin awọn ede Naijiria",
                    "Beere fun iranlọwọ pẹlu awọn gbolohun Hausa, Yoruba, tabi Pidgin"
                ],
                'pcm': [
                    "Try ask about Nigerian news or things wey dey happen",
                    "Ask about Nigerian culture, tradition, or languages",
                    "Ask make I translate between Nigerian languages",
                    "Ask for help with Hausa, Yoruba, or Pidgin phrases"
                ]
            },
            'rephrase_suggestions': {
                'en': [
                    "Try to be more specific in your question",
                    "Break down complex questions into simpler parts",
                    "Provide more context about what you want to know",
                    "Use keywords related to your topic"
                ],
                'ha': [
                    "Yi ƙoƙari ka fi takaita a tambayarka",
                    "Raba tambayoyi masu rikitarwa zuwa sassa masu sauƙi",
                    "Bayar da ƙarin bayani game da abin da kake son sani",
                    "Yi amfani da kalmomin mahimmanci da suka shafi batun"
                ],
                'yo': [
                    "Gbiyanju lati pato diẹ sii ni ibeere rẹ",
                    "Pin awọn ibeere to nira si awọn apakan ti o rọrun",
                    "Pese alaye diẹ sii nipa ohun ti o fẹ mọ",
                    "Lo awọn koko-ọrọ ti o jọmọ koko-ọrọ rẹ"
                ],
                'pcm': [
                    "Try dey more specific for your question",
                    "Break complex questions into small small parts",
                    "Give more context about wetin you wan know",
                    "Use keywords wey relate to your topic"
                ]
            }
        }
    
    def get_fallback_response(
        self,
        scenario: str,
        language: str,
        additional_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get appropriate fallback response for a given scenario.
        
        Args:
            scenario: Type of fallback ('insufficient_knowledge', 'unclear_question', etc.)
            language: Language code for the response
            additional_info: Additional context information
            
        Returns:
            Fallback response dictionary
        """
        # Get base fallback message
        fallback_messages = self.fallback_messages.get(scenario, {})
        message = fallback_messages.get(language, fallback_messages.get('en', 'I cannot process this request.'))
        
        # Add suggestions if relevant
        suggestions = self._get_suggestions(scenario, language, additional_info)
        
        return {
            'response': message,
            'language': language,
            'intent': 'fallback',
            'metadata': {
                'fallback_scenario': scenario,
                'suggestions': suggestions,
                'is_fallback': True,
                'confidence_score': 0.3
            }
        }
    
    def _get_suggestions(
        self,
        scenario: str,
        language: str,
        additional_info: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Get contextual suggestions for the user."""
        suggestions = []
        
        # Map scenarios to suggestion types
        if scenario == 'insufficient_knowledge':
            suggestion_key = 'question_not_found'
        elif scenario == 'unclear_question':
            suggestion_key = 'rephrase_suggestions'
        else:
            suggestion_key = None
        
        if suggestion_key and suggestion_key in self.suggestion_templates:
            suggestions = self.suggestion_templates[suggestion_key].get(
                language,
                self.suggestion_templates[suggestion_key].get('en', [])
            )
        
        return suggestions
    
    def enhance_low_confidence_response(
        self,
        response: str,
        language: str,
        confidence_score: float,
        suggestions: Optional[List[str]] = None
    ) -> str:
        """
        Enhance a low-confidence response with appropriate warnings and suggestions.
        
        Args:
            response: Original response
            language: Language code
            confidence_score: Confidence score (0-1)
            suggestions: Optional list of suggestions
            
        Returns:
            Enhanced response with warnings
        """
        if confidence_score >= 0.7:
            return response  # No enhancement needed
        
        # Add confidence warning
        warning_messages = {
            'en': "\n\n⚠️ Note: I'm not very confident about this answer. Please verify from other sources.",
            'ha': "\n\n⚠️ Lura: Ban cika tabbata da wannan amsa ba. Don Allah ka bincika daga wasu majiyoyi.",
            'yo': "\n\n⚠️ Akiyesi: Mi ko ni igboya pupọ nipa idahun yii. Jọwọ ṣayẹwo lati awọn orisun miiran.",
            'pcm': "\n\n⚠️ Note: I no too sure about this answer. Abeg check from other places."
        }
        
        warning = warning_messages.get(language, warning_messages['en'])
        enhanced = response + warning
        
        # Add suggestions if provided and confidence is very low
        if suggestions and confidence_score < 0.5:
            suggestion_headers = {
                'en': "\n\nYou could also try:",
                'ha': "\n\nKuma kana iya gwadawa:",
                'yo': "\n\nO tun le gbiyanju:",
                'pcm': "\n\nYou fit also try:"
            }
            
            header = suggestion_headers.get(language, suggestion_headers['en'])
            enhanced += header
            for i, suggestion in enumerate(suggestions[:3], 1):
                enhanced += f"\n{i}. {suggestion}"
        
        return enhanced
    
    def should_use_fallback(
        self,
        validation_results: Dict[str, Any],
        response: str
    ) -> tuple[bool, str]:
        """
        Determine if a fallback response should be used instead of the generated response.
        
        Args:
            validation_results: Results from response validator
            response: Generated response
            
        Returns:
            Tuple of (should_use_fallback, scenario_type)
        """
        confidence = validation_results.get('confidence_score', 1.0)
        issues = validation_results.get('issues', [])
        
        # Use fallback if there are critical issues
        if not validation_results.get('is_valid', True):
            if 'empty' in str(issues).lower():
                return True, 'error_occurred'
            if 'placeholder' in str(issues).lower():
                return True, 'error_occurred'
        
        # Use fallback if confidence is extremely low
        if confidence < 0.3:
            return True, 'insufficient_knowledge'
        
        # Check for uncertainty indicators in response
        uncertainty_patterns = [
            "i don't know", "i'm not sure", "uncertain",
            "ban sani ba", "mi o mọ", "i no know",
            "not enough information", "ba isasshen bayani"
        ]
        
        response_lower = response.lower()
        if any(pattern in response_lower for pattern in uncertainty_patterns):
            if confidence < 0.5:
                return True, 'insufficient_knowledge'
        
        return False, ''


def get_fallback_handler() -> FallbackHandler:
    """
    Factory function to get a FallbackHandler instance.
    
    Returns:
        FallbackHandler instance
    """
    return FallbackHandler()
