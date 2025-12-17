"""
Prompt Loader Service
====================
Service to load, parse, and format XML-tagged prompts for the Wazobia Agent.

Author: Firdausi Yakubu
Date: December 15, 2025
"""

import re
from typing import Dict, Any, Optional, List
from .prompts import WazobiaPrompts


class PromptLoader:
    """
    Service class for loading and formatting prompts with variable substitution.
    Handles XML-tagged prompt templates and dynamic parameter injection.
    """
    
    def __init__(self):
        self.prompts = WazobiaPrompts()
    
    def load_prompt(self, prompt_name: str, **kwargs) -> str:
        """
        Load a prompt by name and substitute variables.
        
        Args:
            prompt_name: Name of the prompt constant (e.g., 'TRANSLATION_TASK')
            **kwargs: Variables to substitute in the prompt template
        
        Returns:
            Formatted prompt string with variables substituted
        
        Example:
            loader = PromptLoader()
            prompt = loader.load_prompt(
                'TRANSLATION_TASK',
                source_language='English',
                target_language='Hausa',
                source_text='Hello, how are you?'
            )
        """
        # Get the prompt template
        prompt_template = self.prompts.get_prompt_by_name(prompt_name)
        
        if not prompt_template:
            raise ValueError(f"Prompt '{prompt_name}' not found")
        
        # Substitute variables
        try:
            formatted_prompt = prompt_template.format(**kwargs)
            return formatted_prompt
        except KeyError as e:
            raise ValueError(f"Missing required variable in prompt: {e}")
    
    def extract_xml_tag(self, text: str, tag_name: str) -> Optional[str]:
        """
        Extract content from an XML-like tag in the text.
        
        Args:
            text: The text containing XML tags
            tag_name: Name of the tag to extract
        
        Returns:
            Content within the tag, or None if not found
        
        Example:
            content = loader.extract_xml_tag(response, 'TRANSLATION')
        """
        pattern = f"<{tag_name}>(.*?)</{tag_name}>"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        return None
    
    def extract_all_tags(self, text: str) -> Dict[str, str]:
        """
        Extract all XML-like tags from the text.
        
        Args:
            text: The text containing XML tags
        
        Returns:
            Dictionary mapping tag names to their content
        
        Example:
            tags = loader.extract_all_tags(response)
            # {'ROLE': '...', 'CAPABILITIES': '...', ...}
        """
        pattern = r"<(\w+)>(.*?)</\1>"
        matches = re.finditer(pattern, text, re.DOTALL | re.IGNORECASE)
        
        result = {}
        for match in matches:
            tag_name = match.group(1)
            content = match.group(2).strip()
            result[tag_name] = content
        
        return result
    
    def parse_list_items(self, xml_content: str, item_tag: str) -> List[str]:
        """
        Parse list items from XML content.
        
        Args:
            xml_content: XML content containing list items
            item_tag: Tag name for list items (e.g., 'CAPABILITY', 'REQUIREMENT')
        
        Returns:
            List of item contents
        
        Example:
            capabilities = loader.parse_list_items(capabilities_section, 'CAPABILITY')
        """
        pattern = f"<{item_tag}>(.*?)</{item_tag}>"
        matches = re.finditer(pattern, xml_content, re.DOTALL | re.IGNORECASE)
        
        return [match.group(1).strip() for match in matches]
    
    def build_context_prompt(
        self,
        base_prompt: str,
        context_chunks: List[str],
        max_context_length: int = 4000
    ) -> str:
        """
        Build a prompt with context from knowledge base, respecting token limits.
        
        Args:
            base_prompt: The base prompt template
            context_chunks: List of context strings from knowledge base
            max_context_length: Maximum characters for context section
        
        Returns:
            Complete prompt with context injected
        """
        # Join context chunks
        context = "\n\n---\n\n".join(context_chunks)
        
        # Truncate if too long
        if len(context) > max_context_length:
            context = context[:max_context_length] + "\n\n[Context truncated...]"
        
        # Inject into prompt
        return base_prompt.replace("{context}", context)
    
    def format_multilingual_response(
        self,
        english: str,
        hausa: str = "",
        pidgin: str = "",
        yoruba: str = ""
    ) -> str:
        """
        Format a multilingual response with clear language sections.
        
        Args:
            english: Response in English
            hausa: Response in Hausa (optional)
            pidgin: Response in Nigerian Pidgin (optional)
            yoruba: Response in Yoruba (optional)
        
        Returns:
            Formatted multilingual response
        """
        response_parts = []
        
        if english:
            response_parts.append(f"🇬🇧 **English:**\n{english}")
        
        if hausa:
            response_parts.append(f"🇳🇬 **Hausa:**\n{hausa}")
        
        if pidgin:
            response_parts.append(f"🇳🇬 **Nigerian Pidgin:**\n{pidgin}")
        
        if yoruba:
            response_parts.append(f"🇳🇬 **Yoruba:**\n{yoruba}")
        
        return "\n\n".join(response_parts)
    
    def get_system_prompt(self, additional_context: str = "") -> str:
        """
        Get the core system prompt with optional additional context.
        
        Args:
            additional_context: Additional context to append to system prompt
        
        Returns:
            Complete system prompt
        """
        base_system = self.prompts.SYSTEM_CORE
        
        if additional_context:
            base_system += f"\n\n<ADDITIONAL_CONTEXT>\n{additional_context}\n</ADDITIONAL_CONTEXT>"
        
        return base_system
    
    def validate_prompt_parameters(
        self,
        prompt_template: str,
        provided_params: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """
        Validate that all required parameters are provided for a prompt.
        
        Args:
            prompt_template: The prompt template string
            provided_params: Dictionary of provided parameters
        
        Returns:
            Dictionary with 'missing' and 'extra' parameter lists
        """
        # Extract required parameters from template
        required_params = set(re.findall(r'\{(\w+)\}', prompt_template))
        provided_keys = set(provided_params.keys())
        
        missing = list(required_params - provided_keys)
        extra = list(provided_keys - required_params)
        
        return {
            'missing': missing,
            'extra': extra,
            'valid': len(missing) == 0
        }
    
    def get_greeting_prompt(self, language: str, user_greeting: str) -> str:
        """
        Get a culturally appropriate greeting prompt.
        
        Args:
            language: Target language code (ha, pcm, yo, en)
            user_greeting: The user's greeting message
        
        Returns:
            Formatted greeting prompt
        """
        return self.load_prompt(
            'GREETING_RESPONSE',
            language=self._get_language_name(language),
            user_greeting=user_greeting
        )
    
    def get_translation_prompt(
        self,
        source_text: str,
        source_language: str,
        target_language: str
    ) -> str:
        """
        Get a translation prompt.
        
        Args:
            source_text: Text to translate
            source_language: Source language code
            target_language: Target language code
        
        Returns:
            Formatted translation prompt
        """
        return self.load_prompt(
            'TRANSLATION_TASK',
            source_text=source_text,
            source_language=self._get_language_name(source_language),
            target_language=self._get_language_name(target_language)
        )
    
    def get_qa_prompt(
        self,
        question: str,
        context: str,
        language: str
    ) -> str:
        """
        Get a question answering prompt with context.
        
        Args:
            question: User's question
            context: Retrieved context from knowledge base
            language: Target language for response
        
        Returns:
            Formatted QA prompt
        """
        return self.load_prompt(
            'QUESTION_ANSWERING',
            question=question,
            context=context,
            language=self._get_language_name(language)
        )
    
    def get_content_generation_prompt(
        self,
        topic: str,
        content_type: str,
        target_language: str,
        additional_context: str = ""
    ) -> str:
        """
        Get a content generation prompt.
        
        Args:
            topic: Topic for content generation
            content_type: Type of content (article, story, dialogue, etc.)
            target_language: Language for generated content
            additional_context: Additional context or requirements
        
        Returns:
            Formatted content generation prompt
        """
        return self.load_prompt(
            'CONTENT_GENERATION',
            topic=topic,
            content_type=content_type,
            target_language=self._get_language_name(target_language),
            additional_context=additional_context
        )
    
    def _get_language_name(self, language_code: str) -> str:
        """
        Convert language code to full language name.
        
        Args:
            language_code: Language code (ha, pcm, yo, en)
        
        Returns:
            Full language name
        """
        language_map = {
            'ha': 'Hausa',
            'pcm': 'Nigerian Pidgin',
            'yo': 'Yoruba',
            'en': 'English'
        }
        return language_map.get(language_code.lower(), language_code)
    
    def get_error_prompt(self, error_type: str, language: str = 'en') -> str:
        """
        Get an error handling prompt.
        
        Args:
            error_type: Type of error ('language_not_detected', 'context_not_found', etc.)
            language: Language for error message
        
        Returns:
            Error prompt/message
        """
        error_prompts = {
            'language_not_detected': self.prompts.LANGUAGE_NOT_DETECTED,
            'context_not_found': self.prompts.CONTEXT_NOT_FOUND
        }
        
        prompt = error_prompts.get(error_type, "")
        
        if '{language}' in prompt:
            prompt = prompt.replace('{language}', self._get_language_name(language))
        
        return prompt


# Singleton instance
_prompt_loader_instance = None


def get_prompt_loader() -> PromptLoader:
    """
    Get the singleton PromptLoader instance.
    
    Returns:
        PromptLoader instance
    """
    global _prompt_loader_instance
    
    if _prompt_loader_instance is None:
        _prompt_loader_instance = PromptLoader()
    
    return _prompt_loader_instance
