"""
Base Language Agent
===================
Abstract base class for all language-specific agents.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import os


class BaseLanguageAgent(ABC):
    """Base class for language-specific agents."""
    
    def __init__(self, llm_client: Any = None):
        """
        Initialize the language agent.
        
        Args:
            llm_client: LLM client (Groq, OpenAI, Anthropic, etc.)
        """
        self.llm_client = llm_client
        self.language_code = self.get_language_code()
        self.language_name = self.get_language_name()
    
    @abstractmethod
    def get_language_code(self) -> str:
        """Return the language code (e.g., 'yo', 'ha', 'pcm', 'en')."""
        pass
    
    @abstractmethod
    def get_language_name(self) -> str:
        """Return the full language name."""
        pass
    
    def respond_to_message(
        self, 
        message: str, 
        conversation_history: Optional[str] = None,
        context_type: str = 'general',
        knowledge_base_context: Optional[str] = None
    ) -> str:
        """
        Generate a response to a user message in this language.
        
        Args:
            message: User's message in this language
            conversation_history: Optional conversation history
            context_type: Type of conversation ('greeting', 'casual_conversation', 'question', etc.)
            knowledge_base_context: Optional context from knowledge base
            
        Returns:
            Response in the same language
        """
        prompt = self._build_response_prompt(message, conversation_history, context_type, knowledge_base_context)
        return self._call_llm(prompt)
    
    def translate_to(self, text: str, target_language: str, target_agent: 'BaseLanguageAgent' = None) -> str:
        """
        Translate text from this language to another.
        
        Args:
            text: Text in this language
            target_language: Target language code
            target_agent: The target language agent for verification
            
        Returns:
            Translated text
        """
        # First translation
        translation = self._translate_internal(text, target_language)
        
        # Verification by target agent if available
        if target_agent:
            translation = target_agent.verify_translation(
                original_text=text,
                translated_text=translation,
                source_language=self.language_name
            )
        
        return translation
    
    def verify_translation(self, original_text: str, translated_text: str, source_language: str) -> str:
        """
        Verify and improve a translation into this language.
        
        Args:
            original_text: Original text in source language
            translated_text: Translated text in this language
            source_language: Source language name
            
        Returns:
            Verified/corrected translation
        """
        prompt = f"""You are a {self.language_name} language expert reviewing a translation.

Original text ({source_language}): "{original_text}"
Translation to {self.language_name}: "{translated_text}"

Task: Review the translation for accuracy and naturalness.
- If the translation is correct and natural, return it as-is
- If there are errors or it sounds unnatural, provide a corrected version
- Ensure the meaning is preserved
- Use proper {self.language_name} grammar and expressions

IMPORTANT: Return ONLY the final {self.language_name} translation, nothing else.

Verified translation in {self.language_name}:"""
        
        return self._call_llm(prompt)
    
    def review_response(self, response: str, original_message: str) -> str:
        """
        Review a response for accuracy and appropriateness.
        
        Args:
            response: Generated response
            original_message: Original user message
            
        Returns:
            Reviewed/corrected response
        """
        prompt = f"""You are a {self.language_name} language expert reviewing a response.

User's message: "{original_message}"
Generated response: "{response}"

Task: Review the response and ensure:
1. It's entirely in {self.language_name} (no language mixing)
2. Grammar and spelling are correct
3. It answers the user's message appropriately
4. It sounds natural and conversational
5. Cultural context is appropriate

CRITICAL RULES:
- Do NOT mix languages (e.g., no Yoruba-English-Pidgin mix)
- Stay 100% in {self.language_name}
- If the response has language mixing, rewrite it properly

Return ONLY the final {self.language_name} response:"""
        
        return self._call_llm(prompt)
    
    def _translate_internal(self, text: str, target_language: str) -> str:
        """Internal translation method."""
        target_lang_map = {
            'en': 'English',
            'ha': 'Hausa',
            'yo': 'Yoruba',
            'pcm': 'Nigerian Pidgin'
        }
        target_name = target_lang_map.get(target_language, target_language)
        
        prompt = f"""You are an expert translator from {self.language_name} to {target_name}.

Translate this text from {self.language_name} to {target_name}:
"{text}"

CRITICAL RULES:
- Translate accurately, preserving the exact meaning
- Use natural {target_name} expressions
- Keep the same tone (casual, formal, etc.)
- Do NOT add extra information or explanations
- Return ONLY the translation, nothing else

Translation in {target_name}:"""
        
        return self._call_llm(prompt)
    
    @abstractmethod
    def _build_response_prompt(
        self, 
        message: str, 
        conversation_history: Optional[str] = None,
        context_type: str = 'general',
        knowledge_base_context: Optional[str] = None
    ) -> str:
        """Build language-specific response prompt."""
        pass
    
    def _call_llm(self, prompt: str) -> str:
        """Call the LLM with the given prompt."""
        if not self.llm_client:
            return "[LLM not configured]"
        
        try:
            provider = os.getenv("WAZOBIA_LLM_PROVIDER", "anthropic").lower()
            
            if provider == "anthropic":
                response = self.llm_client.messages.create(
                    model=os.getenv("WAZOBIA_DEFAULT_MODEL", "claude-3-5-sonnet-20241022"),
                    max_tokens=int(os.getenv("WAZOBIA_MAX_TOKENS", "2000")),
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            
            elif provider in ["openai", "groq"]:
                response = self.llm_client.chat.completions.create(
                    model=os.getenv("WAZOBIA_DEFAULT_MODEL", "llama-3.3-70b-versatile"),
                    messages=[{"role": "user", "content": prompt}],
                    temperature=float(os.getenv("WAZOBIA_TEMPERATURE", "0.7")),
                    max_tokens=int(os.getenv("WAZOBIA_MAX_TOKENS", "2000"))
                )
                return response.choices[0].message.content
            
        except Exception as e:
            return f"Error calling LLM: {str(e)}"
