"""
Yoruba Language Agent
====================
Specialized agent for Yoruba language processing.
"""

from typing import Optional
from .base_agent import BaseLanguageAgent


class YorubaAgent(BaseLanguageAgent):
    """Yoruba language specialist agent."""
    
    def get_language_code(self) -> str:
        return 'yo'
    
    def get_language_name(self) -> str:
        return 'Yoruba'
    
    def _build_response_prompt(
        self, 
        message: str, 
        conversation_history: Optional[str] = None,
        context_type: str = 'general',
        knowledge_base_context: Optional[str] = None
    ) -> str:
        """Build Yoruba-specific response prompt using centralized template."""
        
        # Determine output instruction based on context type
        if context_type == 'greeting':
            output_instruction = "Provide a warm Yoruba greeting (1-2 sentences)."
        elif context_type == 'casual_conversation':
            output_instruction = "Respond naturally in conversational Yoruba."
        else:
            output_instruction = "Provide your answer in pure Yoruba."
        
        # Use centralized prompt template
        from ..prompts import WazobiaPrompts
        
        prompt = WazobiaPrompts.YORUBA_AGENT_RESPONSE.format(
            user_message=message,
            context_type=context_type,
            conversation_history=conversation_history or "No previous conversation",
            knowledge_base_context=knowledge_base_context or "No additional context provided",
            output_instruction=output_instruction
        )
        
        return prompt
    
    def detect_language_mixing(self, text: str) -> bool:
        """
        Detect if text contains language mixing.
        
        Args:
            text: Text to check
            
        Returns:
            True if language mixing detected
        """
        # Common English words that shouldn't appear in pure Yoruba
        english_indicators = [
            'the', 'is', 'are', 'was', 'were', 'have', 'has', 'had',
            'will', 'would', 'should', 'could', 'can', 'may', 'might',
            'do', 'does', 'did', 'make', 'get', 'need', 'want',
            'listening', 'worry', 'plan', 'help', 'here', 'there'
        ]
        
        # Pidgin indicators
        pidgin_indicators = ['dey', 'wetin', 'wey', 'na', 'fit', 'sabi']
        
        text_lower = text.lower()
        
        # Check for English
        has_english = any(f' {word} ' in f' {text_lower} ' for word in english_indicators)
        
        # Check for Pidgin
        has_pidgin = any(word in text_lower for word in pidgin_indicators)
        
        return has_english or has_pidgin
    
    def clean_response(self, response: str) -> str:
        """
        Clean and validate a Yoruba response.
        
        Args:
            response: Response to clean
            
        Returns:
            Cleaned response
        """
        # If language mixing detected, regenerate
        if self.detect_language_mixing(response):
            prompt = f"""This response contains language mixing: "{response}"

Rewrite it in PURE Yoruba only. No English. No Pidgin. Only Yoruba.

Pure Yoruba response:"""
            return self._call_llm(prompt)
        
        return response
