"""
English Language Agent
=====================
Specialized agent for English language processing.
"""

from typing import Optional
from .base_agent import BaseLanguageAgent


class EnglishAgent(BaseLanguageAgent):
    """English language specialist agent."""
    
    def get_language_code(self) -> str:
        return 'en'
    
    def get_language_name(self) -> str:
        return 'English'
    
    def _build_response_prompt(
        self, 
        message: str, 
        conversation_history: Optional[str] = None,
        context_type: str = 'general',
        knowledge_base_context: Optional[str] = None
    ) -> str:
        """Build English-specific response prompt using centralized template."""
        
        # Determine output instruction based on context type
        if context_type == 'greeting':
            output_instruction = "Provide a warm greeting (1-2 sentences)."
        elif context_type == 'casual_conversation':
            output_instruction = "Respond naturally and conversationally."
        else:
            output_instruction = "Provide your answer in English."
        
        # Use centralized prompt template
        from ..prompts import WazobiaPrompts
        
        prompt = WazobiaPrompts.ENGLISH_AGENT_RESPONSE.format(
            user_message=message,
            context_type=context_type,
            conversation_history=conversation_history or "No previous conversation",
            knowledge_base_context=knowledge_base_context or "No additional context provided",
            output_instruction=output_instruction
        )
        
        return prompt
