"""
Wazobia Multilingual AI Agent
=============================
Core agent implementation with RAG capabilities for Nigerian languages.

Author: Umar Yunusa
Date: December 15, 2025
"""

import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

from .language_detector import get_language_detector
from .prompt_loader import get_prompt_loader
from .services import YorubaAgent, HausaAgent, PidginAgent, EnglishAgent


class WazobiaAgent:
    """
    Multilingual AI Agent for Nigerian languages (Hausa, Pidgin, Yoruba).
    Provides translation, Q&A, content generation, and cultural assistance.
    """
    
    def __init__(
        self,
        knowledge_base_path: Optional[str] = None,
        llm_client: Optional[Any] = None,
        embedding_model: Optional[Any] = None
    ):
        """
        Initialize the Wazobia Agent.
        
        Args:
            knowledge_base_path: Path to the knowledge base data directory
            llm_client: LLM client (OpenAI, Anthropic, etc.)
            embedding_model: Embedding model for RAG
        """
        self.language_detector = get_language_detector()
        self.prompt_loader = get_prompt_loader()
        self.llm_client = llm_client
        self.embedding_model = embedding_model
        
        # Set knowledge base path
        if knowledge_base_path is None:
            # Default to data directory in wazobia-agent
            current_dir = Path(__file__).parent.parent
            knowledge_base_path = current_dir / "data"
        
        self.knowledge_base_path = Path(knowledge_base_path)
        
        # Load knowledge base
        self.knowledge_base = self._load_knowledge_base()
        
        # Initialize specialized language agents
        self.agents = {
            'yo': YorubaAgent(llm_client=llm_client),
            'ha': HausaAgent(llm_client=llm_client),
            'pcm': PidginAgent(llm_client=llm_client),
            'en': EnglishAgent(llm_client=llm_client)
        }
        
        # Conversation history
        self.conversation_history: List[Dict[str, str]] = []
    
    def _load_knowledge_base(self) -> Dict[str, List[Dict]]:
        """
        Load all knowledge base files.
        
        Returns:
            Dictionary mapping language codes to document lists
        """
        kb = {
            'ha': [],  # Hausa
            'pcm': [], # Pidgin
            'yo': [],  # Yoruba
            'all': []  # Combined
        }
        
        # Load individual language files
        files_to_load = [
            ('bbc_hausa_scraped.json', 'ha'),
            ('bbc_pidgin_scraped.json', 'pcm'),
            ('bbc_yoruba_scraped.json', 'yo'),
            ('combined_wazobia_dataset.json', 'all')
        ]
        
        for filename, lang_code in files_to_load:
            file_path = self.knowledge_base_path / filename
            
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # Handle both list and dict formats
                        if isinstance(data, list):
                            kb[lang_code] = data
                        elif isinstance(data, dict):
                            kb[lang_code] = [data]
                        
                        print(f"✓ Loaded {len(kb[lang_code])} documents from {filename}")
                except Exception as e:
                    print(f"✗ Error loading {filename}: {e}")
            else:
                print(f"⚠ File not found: {filename}")
        
        return kb
    
    def process_message(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and generate a response.
        
        Args:
            message: User's input message
            context: Optional context (user preferences, session data, etc.)
        
        Returns:
            Response dictionary containing:
                - response: Generated response text
                - language: Detected/used language
                - intent: Detected intent
                - metadata: Additional metadata
        """
        # Detect language
        detection = self.language_detector.detect_language(message)
        detected_lang = detection['language']
        
        # Check for preferred languages in context
        preferred_languages = context.get('preferred_languages', []) if context else []
        
        # If preferred languages specified, use them to inform the agent
        if preferred_languages:
            if detected_lang not in preferred_languages:
                # User's input language should be detected, but response can be in preferred language
                # Pass this info to handlers
                if not context:
                    context = {}
                context['mixed_mode'] = True
                context['response_languages'] = preferred_languages
        
        # Determine intent
        intent = self._detect_intent(message, detected_lang)
        
        # Route to appropriate handler
        if intent == 'greeting':
            response = self._handle_greeting(message, detected_lang, context)
        elif intent == 'casual_conversation':
            response = self._handle_casual_conversation(message, detected_lang, context)
        elif intent == 'translation':
            response = self._handle_translation(message, detected_lang, context)
        elif intent == 'question':
            response = self._handle_question(message, detected_lang, context)
        elif intent == 'cultural_query':
            response = self._handle_cultural_query(message, detected_lang, context)
        elif intent == 'content_generation':
            response = self._handle_content_generation(message, detected_lang, context)
        else:
            response = self._handle_general(message, detected_lang, context)
        
        # Add to conversation history
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'user': message,
            'agent': response['response'],
            'language': detected_lang,
            'intent': intent
        })
        
        return response
    
    def _detect_intent(self, message: str, language: str) -> str:
        """
        Detect user's intent from the message.
        
        Args:
            message: User message
            language: Detected language
        
        Returns:
            Intent string
        """
        message_lower = message.lower()
        
        # Initial greeting patterns
        greeting_patterns = [
            'hello', 'hi', 'sannu', 'how far', 'bawo ni', 'pẹlẹ', 'e ku',
            'good morning', 'good afternoon', 'good evening',
            'e kaaro', 'e kasan', 'e ku irole'
        ]
        if any(pattern in message_lower for pattern in greeting_patterns):
            return 'greeting'
        
        # Casual conversation patterns (asking about wellbeing, family, etc.)
        casual_patterns = [
            "how are you", "how's you", "how're you", "how you dey",
            "how are u", "how r u", "you good", "you dey",
            "how's the family", "how is family", "how's your family",
            "how are things", "how's everything", "what's up", "wassup",
            "you alright", "u alright", "hope you good", "hope say",
            "i mean", "i'm saying", "you feel me", "you understand",
            "what about you", "and you", "wetin you talk",
            "se daada ni", "ṣe dara ni", "bawo lo wa", "kana lafiya"
        ]
        if any(pattern in message_lower for pattern in casual_patterns):
            return 'casual_conversation'
        
        # Translation patterns
        translation_patterns = [
            'translate', 'convert', 'fassara', 'turn to', 'say in',
            'how do you say', 'mean in', 'in english', 'in hausa',
            'in yoruba', 'in pidgin'
        ]
        if any(pattern in message_lower for pattern in translation_patterns):
            return 'translation'
        
        # Factual question patterns (requires knowledge base)
        factual_patterns = [
            'tell me about', 'explain', 'describe', 'who is', 'who was',
            'what happened', 'when did', 'where is', 'history of',
            'information about', 'facts about', 'details about',
            'what is', 'what are', 'define', 'meaning of'
        ]
        if any(pattern in message_lower for pattern in factual_patterns):
            return 'question'
        
        # Simple question words - be more selective
        question_words = ['why', 'when', 'where', 'who', 'which',
                          'menene', 'yaushe', 'wane', 'wetin']
        # Check if it's a short casual question or contains casual patterns
        word_count = len(message.split())
        has_casual = any(p in message_lower for p in ['you', 'your', 'u', 'ur', 'dey', 'are'])
        
        if any(word in message_lower for word in question_words):
            # If short and casual words, treat as conversation
            if word_count <= 6 and has_casual:
                return 'casual_conversation'
            # Otherwise treat as factual question
            else:
                return 'question'
        
        # Cultural query patterns
        cultural_keywords = ['proverb', 'idiom', 'culture', 'tradition', 'festival',
                             'karin magana', 'al\'ada', 'àṣà', 'owe']
        if any(keyword in message_lower for keyword in cultural_keywords):
            return 'cultural_query'
        
        # Content generation patterns
        generation_keywords = ['write', 'generate', 'create', 'compose', 'rubuta']
        if any(keyword in message_lower for keyword in generation_keywords):
            return 'content_generation'
        
        return 'casual_conversation'
    
    def _get_agent_for_language(self, language: str):
        """
        Get the specialized agent for the given language.
        
        Args:
            language: Language code (yo, ha, pcm, en)
            
        Returns:
            Specialized language agent instance
        """
        # Map language codes to agents
        agent = self.agents.get(language)
        
        # Default to English agent if language not supported
        if agent is None:
            agent = self.agents['en']
            
        return agent
    
    def _handle_greeting(self, message: str, language: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle greeting messages using specialized agents."""
        # Check for preferred languages in mixed mode
        if context and context.get('mixed_mode') and context.get('response_languages'):
            # Use first preferred language for response
            response_lang = context['response_languages'][0]
        else:
            response_lang = language
            
        # Get the specialized agent for response language
        agent = self._get_agent_for_language(response_lang)
        
        # Use the agent to generate a culturally appropriate greeting
        response_text = agent.respond_to_message(
            message=message,
            conversation_history="",
            context_type='greeting'
        )
        
        # Review the response for quality
        reviewed_response = agent.review_response(response_text, message)
        
        return {
            'response': reviewed_response,
            'language': response_lang,
            'intent': 'greeting',
            'metadata': {
                'detection_confidence': 0.9,
                'agent': agent.__class__.__name__,
                'input_language': language
            }
        }
    
    def _handle_casual_conversation(self, message: str, language: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle casual conversation without knowledge base retrieval."""
        # Check for preferred languages in mixed mode
        if context and context.get('mixed_mode') and context.get('response_languages'):
            # Use first preferred language for response
            response_lang = context['response_languages'][0]
        else:
            response_lang = language
            
        # Get the specialized agent for response language
        agent = self._get_agent_for_language(response_lang)
        
        # Get conversation history for context
        history_context = self._get_conversation_context()
        
        # Use the specialized agent to respond
        response_text = agent.respond_to_message(
            message=message,
            conversation_history=history_context,
            context_type='casual_conversation'
        )
        
        # Review the response for language mixing/quality issues
        reviewed_response = agent.review_response(response_text, message)
        
        return {
            'response': reviewed_response,
            'language': response_lang,
            'intent': 'casual_conversation',
            'metadata': {
                'conversational': True,
                'agent': agent.__class__.__name__,
                'input_language': language
            }
        }
    
    def _handle_translation(
        self,
        message: str,
        language: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Handle translation requests using specialized agents."""
        # Check if explicit translation parameters provided in context
        if context and 'text_to_translate' in context:
            source_lang = context.get('source_language', language)
            target_lang = context.get('target_language', 'en')
            text_to_translate = context['text_to_translate']
        else:
            # Parse translation request from message
            source_lang, target_lang, text_to_translate = self._parse_translation_request(
                message, language
            )
        
        if not text_to_translate:
            return {
                'response': 'Please specify the text you want to translate.',
                'language': language,
                'intent': 'translation',
                'metadata': {'error': 'missing_text'}
            }
        
        # Get the source and target language agents
        source_agent = self._get_agent_for_language(source_lang)
        target_agent = self._get_agent_for_language(target_lang)
        
        # Use agent-to-agent translation with verification
        translated_text = source_agent.translate_to(
            text=text_to_translate,
            target_language=target_lang,
            target_agent=target_agent
        )
        
        return {
            'response': translated_text,
            'language': target_lang,
            'intent': 'translation',
            'metadata': {
                'source_language': source_lang,
                'target_language': target_lang,
                'original_text': text_to_translate,
                'source_agent': source_agent.__class__.__name__,
                'target_agent': target_agent.__class__.__name__
            }
        }
    
    def _handle_question(
        self,
        message: str,
        language: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Handle question answering with RAG."""
        # Check for preferred languages in mixed mode
        if context and context.get('mixed_mode') and context.get('response_languages'):
            # Use first preferred language for response
            response_lang = context['response_languages'][0]
        else:
            response_lang = language
            
        # Retrieve relevant context from knowledge base
        relevant_docs = self._retrieve_relevant_docs(message, response_lang)
        
        # Build context string
        context_str = self._build_context_string(relevant_docs)
        
        # Map language for explicit instruction
        language_map = {
            'en': 'English',
            'ha': 'Hausa',
            'pcm': 'Nigerian Pidgin',
            'yo': 'Yoruba'
        }
        response_language = language_map.get(response_lang, 'English')
        
        # Build conversational QA prompt with strict grounding
        prompt = f"""You are a knowledgeable Nigerian multilingual AI assistant that ONLY provides information from verified sources.

The user asked (in {response_language}): "{message}"

Knowledge base information:
{context_str}

CRITICAL INSTRUCTIONS:
- ONLY use information from the knowledge base above to answer
- Do NOT make up, assume, or infer information not explicitly stated in the knowledge base
- Answer in {response_language} (the same language they used)
- Be conversational and natural in tone, but STRICTLY factual in content
- If the knowledge base doesn't contain enough information to answer the question, say: "I don't have enough information in my knowledge base to answer that question accurately" (in {response_language})
- Keep it concise but accurate (2-4 sentences)
- Cite what you know from the knowledge base, don't speculate beyond it

Your answer in {response_language} (using ONLY knowledge base information):"""
        
        # Generate answer
        if self.llm_client:
            answer = self._call_llm(prompt)
        else:
            answer = f"Based on the available information: {context_str[:200]}..."
        
        return {
            'response': answer,
            'language': response_lang,
            'intent': 'question',
            'metadata': {
                'input_language': language,
                'sources': [doc.get('title', 'Unknown') for doc in relevant_docs[:3]],
                'num_sources': len(relevant_docs)
            }
        }
    
    def _handle_cultural_query(
        self,
        message: str,
        language: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Handle cultural and proverb queries."""
        # Check for preferred languages in mixed mode
        if context and context.get('mixed_mode') and context.get('response_languages'):
            # Use first preferred language for response
            response_lang = context['response_languages'][0]
        else:
            response_lang = language
            
        # Retrieve relevant cultural information from knowledge base
        relevant_docs = self._retrieve_relevant_docs(message, response_lang, top_k=3)
        context_str = self._build_context_string(relevant_docs)
        
        # Map language
        language_map = {
            'en': 'English',
            'ha': 'Hausa',
            'pcm': 'Nigerian Pidgin',
            'yo': 'Yoruba'
        }
        response_language = language_map.get(response_lang, 'English')
        
        # Build grounded cultural explanation prompt
        prompt = f"""You are a Nigerian cultural expert assistant.

The user asked about Nigerian culture (in {response_language}): "{message}"

Knowledge base information:
{context_str}

CRITICAL INSTRUCTIONS:
- ONLY provide cultural information from the knowledge base above
- Do NOT invent proverbs, traditions, or cultural facts
- Answer in {response_language}
- If the knowledge base doesn't have information about this topic, say: "I don't have information about that in my knowledge base" (in {response_language})
- Be conversational but factually accurate
- Keep it concise (2-4 sentences)

Your answer in {response_language} (using ONLY knowledge base information):"""
        
        # Generate response
        if self.llm_client:
            response_text = self._call_llm(prompt)
        else:
            response_text = f"Cultural explanation for: {message} [LLM not configured]"
        
        return {
            'response': response_text,
            'language': response_lang,
            'intent': 'cultural_query',
            'metadata': {
                'has_context': len(relevant_docs) > 0,
                'num_sources': len(relevant_docs),
                'input_language': language
            }
        }
    
    def _handle_content_generation(
        self,
        message: str,
        language: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Handle content generation requests."""
        # Parse generation request
        topic, content_type = self._parse_generation_request(message)
        
        # Get content generation prompt
        prompt = self.prompt_loader.get_content_generation_prompt(
            topic, content_type, language, ""
        )
        
        # Generate content
        if self.llm_client:
            generated_content = self._call_llm(prompt)
        else:
            generated_content = f"[Generated {content_type} about {topic} in {language}]"
        
        return {
            'response': generated_content,
            'language': language,
            'intent': 'content_generation',
            'metadata': {
                'topic': topic,
                'content_type': content_type
            }
        }
    
    def _handle_general(
        self,
        message: str,
        language: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Handle general conversation."""
        # Get conversation history context
        history_context = self._get_conversation_context()
        
        # Get conversation prompt
        prompt = self.prompt_loader.load_prompt(
            'CASUAL_CONVERSATION',
            language=self.language_detector.get_language_name(language),
            user_message=message,
            conversation_history=history_context
        )
        
        # Generate response
        if self.llm_client:
            response_text = self._call_llm(prompt)
        else:
            response_text = f"I understand you said: {message}. (LLM not configured for full responses)"
        
        return {
            'response': response_text,
            'language': language,
            'intent': 'general',
            'metadata': {}
        }
    
    def _retrieve_relevant_docs(
        self,
        query: str,
        language: str,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Retrieve relevant documents from knowledge base.
        
        Args:
            query: Search query
            language: Target language
            top_k: Number of documents to retrieve
        
        Returns:
            List of relevant documents
        """
        # Get documents for the language
        if language in self.knowledge_base and self.knowledge_base[language]:
            docs = self.knowledge_base[language]
        else:
            docs = self.knowledge_base.get('all', [])
        
        if not docs:
            return []
        
        # Simple keyword-based retrieval (can be enhanced with embeddings)
        query_words = set(query.lower().split())
        
        scored_docs = []
        for doc in docs:
            text = doc.get('text', '')
            title = doc.get('title', '')
            
            # Calculate simple relevance score
            doc_words = set((text + ' ' + title).lower().split())
            overlap = len(query_words & doc_words)
            
            if overlap > 0:
                scored_docs.append((overlap, doc))
        
        # Sort by score and return top k
        scored_docs.sort(reverse=True, key=lambda x: x[0])
        return [doc for _, doc in scored_docs[:top_k]]
    
    def _build_context_string(self, docs: List[Dict]) -> str:
        """Build context string from retrieved documents."""
        if not docs:
            return "No relevant information found in knowledge base."
        
        context_parts = []
        for i, doc in enumerate(docs, 1):
            title = doc.get('title', 'Untitled')
            text = doc.get('text', '')
            source = doc.get('source', 'unknown')
            
            # Truncate long texts
            if len(text) > 500:
                text = text[:500] + "..."
            
            context_parts.append(f"[Source {i}: {title} ({source})]\n{text}")
        
        return "\n\n".join(context_parts)
    
    def _parse_translation_request(
        self,
        message: str,
        detected_lang: str
    ) -> tuple[str, str, str]:
        """
        Parse a translation request to extract languages and text.
        
        Returns:
            (source_lang, target_lang, text_to_translate)
        """
        # Simple pattern matching (can be enhanced)
        # Look for patterns like "translate X to Y" or "say X in Y"
        
        import re
        
        # Pattern: "translate <text> from/to <lang>"
        patterns = [
            r'translate\s+(.+?)\s+(?:from|to)\s+(\w+)',
            r'say\s+(.+?)\s+in\s+(\w+)',
            r'convert\s+(.+?)\s+to\s+(\w+)',
            r'fassara\s+(.+?)\s+zuwa\s+(\w+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message.lower())
            if match:
                text = match.group(1).strip()
                target_lang = self._normalize_language_name(match.group(2))
                source_lang = detected_lang
                return source_lang, target_lang, text
        
        # If no clear pattern, assume the whole message after "translate" is the text
        if 'translate' in message.lower():
            text = message.lower().replace('translate', '').strip()
            return detected_lang, 'en', text
        
        return detected_lang, 'en', message
    
    def _parse_generation_request(self, message: str) -> tuple[str, str]:
        """
        Parse content generation request.
        
        Returns:
            (topic, content_type)
        """
        message_lower = message.lower()
        
        # Detect content type
        if 'story' in message_lower or 'tale' in message_lower:
            content_type = 'story'
        elif 'article' in message_lower or 'essay' in message_lower:
            content_type = 'article'
        elif 'poem' in message_lower:
            content_type = 'poem'
        elif 'dialogue' in message_lower or 'conversation' in message_lower:
            content_type = 'dialogue'
        else:
            content_type = 'text'
        
        # Extract topic (simple approach)
        import re
        about_match = re.search(r'about\s+(.+)', message, re.IGNORECASE)
        if about_match:
            topic = about_match.group(1).strip()
        else:
            # Use the whole message as topic
            topic = message
        
        return topic, content_type
    
    def _normalize_language_name(self, lang: str) -> str:
        """Normalize language name to code."""
        lang_map = {
            'hausa': 'ha',
            'pidgin': 'pcm',
            'yoruba': 'yo',
            'english': 'en',
            'igbo': 'ig'
        }
        return lang_map.get(lang.lower(), lang)
    
    def _get_conversation_context(self, max_turns: int = 5) -> str:
        """Get recent conversation history as context."""
        if not self.conversation_history:
            return "No previous conversation."
        
        recent = self.conversation_history[-max_turns:]
        context_parts = []
        
        for turn in recent:
            context_parts.append(f"User: {turn['user']}\nAgent: {turn['agent']}")
        
        return "\n\n".join(context_parts)
    
    def _call_llm(self, prompt: str) -> str:
        """
        Call the LLM with the given prompt.
        Supports OpenAI, Groq, and Anthropic APIs.
        
        Args:
            prompt: Formatted prompt
        
        Returns:
            LLM response
        """
        if not self.llm_client:
            return "[LLM not configured]"
        
        try:
            provider = os.getenv("WAZOBIA_LLM_PROVIDER", "anthropic").lower()
            model = os.getenv("WAZOBIA_DEFAULT_MODEL")
            temperature = float(os.getenv("WAZOBIA_TEMPERATURE", "0.7"))
            max_tokens = int(os.getenv("WAZOBIA_MAX_TOKENS", "2000"))
            
            if provider == "anthropic":
                # Anthropic Claude API
                response = self.llm_client.messages.create(
                    model=model or "claude-3-5-sonnet-20241022",
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            
            elif provider in ["openai", "groq"]:
                # OpenAI/Groq compatible API (both use same interface)
                default_model = "gpt-4o" if provider == "openai" else "llama-3.1-70b-versatile"
                response = self.llm_client.chat.completions.create(
                    model=model or default_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            
            else:
                return f"[Unsupported LLM provider: {provider}]"
                
        except Exception as e:
            return f"Error calling LLM ({os.getenv('WAZOBIA_LLM_PROVIDER', 'unknown')}): {str(e)}"
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics."""
        return {
            'total_conversations': len(self.conversation_history),
            'knowledge_base_size': {
                lang: len(docs) for lang, docs in self.knowledge_base.items()
            },
            'languages_supported': ['Hausa', 'Nigerian Pidgin', 'Yoruba', 'English']
        }
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []


# Singleton instance
_agent_instance = None


def get_wazobia_agent(**kwargs) -> WazobiaAgent:
    """
    Get the singleton WazobiaAgent instance.
    Automatically initializes the appropriate LLM client based on WAZOBIA_LLM_PROVIDER.
    
    Args:
        **kwargs: Arguments to pass to WazobiaAgent constructor
    
    Returns:
        WazobiaAgent instance
    """
    global _agent_instance
    
    if _agent_instance is None:
        # Initialize LLM client if not provided
        if 'llm_client' not in kwargs:
            try:
                from dotenv import load_dotenv
                from pathlib import Path
                
                # Ensure .env is loaded
                env_path = Path(__file__).parent.parent / ".env"
                load_dotenv(dotenv_path=env_path)
                
                llm_provider = os.getenv("WAZOBIA_LLM_PROVIDER", "anthropic").lower()
                
                if llm_provider == "anthropic":
                    from anthropic import Anthropic
                    api_key = os.getenv("WAZOBIA_ANTHROPIC_API_KEY")
                    if api_key:
                        api_key = api_key.strip('"').strip("'")
                    
                    if api_key and api_key not in ["your-anthropic-key-here", ""]:
                        print(f"✅ Anthropic (Claude) initialized with key: {api_key[:10]}...")
                        kwargs['llm_client'] = Anthropic(api_key=api_key)
                    else:
                        print("⚠️ WAZOBIA_ANTHROPIC_API_KEY not found or invalid in .env file")
                
                elif llm_provider == "groq":
                    from groq import Groq
                    api_key = os.getenv("WAZOBIA_GROQ_API_KEY")
                    if api_key:
                        api_key = api_key.strip('"').strip("'")
                    
                    if api_key and api_key not in ["your-groq-api-key-here", ""]:
                        print(f"✅ Groq (Llama) initialized with key: {api_key[:10]}...")
                        kwargs['llm_client'] = Groq(api_key=api_key)
                    else:
                        print("⚠️ WAZOBIA_GROQ_API_KEY not found or invalid in .env file")
                
                elif llm_provider == "openai":
                    from openai import OpenAI
                    api_key = os.getenv("WAZOBIA_OPENAI_API_KEY")
                    if api_key:
                        api_key = api_key.strip('"').strip("'")
                    
                    if api_key and api_key not in ["your-openai-key-here", "", "sk-..."]:
                        print(f"✅ OpenAI (GPT) initialized with key: {api_key[:10]}...")
                        kwargs['llm_client'] = OpenAI(api_key=api_key)
                    else:
                        print("⚠️ WAZOBIA_OPENAI_API_KEY not found or invalid in .env file")
                
                else:
                    print(f"⚠️ Unsupported LLM provider: {llm_provider}")
                    print(f"   Supported providers: anthropic, groq, openai")
                
            except ImportError as e:
                print(f"❌ Required package not installed: {e}")
                print(f"   Run: pip install anthropic (or groq/openai)")
            except Exception as e:
                print(f"❌ Could not initialize LLM client: {e}")
        
        _agent_instance = WazobiaAgent(**kwargs)
    
    return _agent_instance
