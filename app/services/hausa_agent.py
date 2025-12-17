"""
Hausa Language Agent
===================
Specialized agent for Hausa language processing.
"""

from typing import Optional
from .base_agent import BaseLanguageAgent


class HausaAgent(BaseLanguageAgent):
    """Hausa language specialist agent."""
    
    def get_language_code(self) -> str:
        return 'ha'
    
    def get_language_name(self) -> str:
        return 'Hausa'
    
    def _build_response_prompt(
        self, 
        message: str, 
        conversation_history: Optional[str] = None,
        context_type: str = 'general',
        knowledge_base_context: Optional[str] = None
    ) -> str:
        """Build Hausa-specific response prompt using centralized template."""
        
        # Determine output instruction based on context type
        if context_type == 'greeting':
            output_instruction = "Provide a warm Hausa greeting (1-2 sentences)."
        elif context_type == 'casual_conversation':
            output_instruction = "Respond naturally in conversational Hausa."
        else:
            output_instruction = "Provide your answer in pure Hausa."
        
        # Use centralized prompt template
        from ..prompts import WazobiaPrompts
        
        prompt = WazobiaPrompts.HAUSA_AGENT_RESPONSE.format(
            user_message=message,
            context_type=context_type,
            conversation_history=conversation_history or "No previous conversation",
            knowledge_base_context=knowledge_base_context or "No additional context provided",
            output_instruction=output_instruction
        )
        
        return prompt
    
    def detect_language_mixing(self, text: str) -> bool:
        """Detect if text contains language mixing."""
        # Common English words
        english_indicators = [
            'the', 'is', 'are', 'was', 'have', 'help', 'need', 'want',
            'listening', 'worry', 'plan', 'here', 'there'
        ]
        
        # Yoruba/Pidgin indicators
        other_lang_indicators = ['dey', 'wetin', 'mo', 'ni', 'se', 'bawo']
        
        text_lower = text.lower()
        
        has_english = any(f' {word} ' in f' {text_lower} ' for word in english_indicators)
        has_other = any(word in text_lower for word in other_lang_indicators)
        
        return has_english or has_other
