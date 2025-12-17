"""
Nigerian Pidgin Agent
====================
Specialized agent for Nigerian Pidgin processing.
"""

from typing import Optional
from .base_agent import BaseLanguageAgent


class PidginAgent(BaseLanguageAgent):
    """Nigerian Pidgin specialist agent."""
    
    def get_language_code(self) -> str:
        return 'pcm'
    
    def get_language_name(self) -> str:
        return 'Nigerian Pidgin'
    
    def _build_response_prompt(
        self, 
        message: str, 
        conversation_history: Optional[str] = None,
        context_type: str = 'general',
        knowledge_base_context: Optional[str] = None
    ) -> str:
        """Build Pidgin-specific response prompt using centralized template."""
        
        # Determine output instruction based on context type
        if context_type == 'greeting':
            output_instruction = "Give warm Nigerian Pidgin greeting (1-2 sentences)."
        elif context_type == 'casual_conversation':
            output_instruction = "Respond naturally for Nigerian Pidgin conversation."
        else:
            output_instruction = "Provide your answer in pure Nigerian Pidgin."
        
        # Use centralized prompt template
        from ..prompts import WazobiaPrompts
        
        prompt = WazobiaPrompts.PIDGIN_AGENT_RESPONSE.format(
            user_message=message,
            context_type=context_type,
            conversation_history=conversation_history or "No previous conversation",
            knowledge_base_context=knowledge_base_context or "No additional context provided",
            output_instruction=output_instruction
        )
        
        return prompt
