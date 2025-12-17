"""
Example Usage Scripts for Wazobia Agent
"""

# ============================================================================
# Example 1: Basic Agent Usage
# ============================================================================

def example_basic_usage():
    """Basic agent initialization and usage."""
    from app import get_wazobia_agent
    
    print("Example 1: Basic Agent Usage")
    print("=" * 50)
    
    # Initialize agent
    agent = get_wazobia_agent()
    
    # Process a Hausa greeting
    response = agent.process_message("Sannu, yaya kuke?")
    print(f"User (Hausa): Sannu, yaya kuke?")
    print(f"Agent: {response['response']}")
    print(f"Detected language: {response['language']}")
    print(f"Intent: {response['intent']}\n")


# ============================================================================
# Example 2: Translation
# ============================================================================

def example_translation():
    """Translation between languages."""
    from app import get_wazobia_agent
    
    print("Example 2: Translation")
    print("=" * 50)
    
    agent = get_wazobia_agent()
    
    # English to Hausa
    response = agent.process_message(
        "Translate 'Good morning, how did you sleep?' to Hausa"
    )
    print(f"Translation: {response['response']}\n")


# ============================================================================
# Example 3: Language Detection
# ============================================================================

def example_language_detection():
    """Demonstrate language detection."""
    from app import get_language_detector
    
    print("Example 3: Language Detection")
    print("=" * 50)
    
    detector = get_language_detector()
    
    texts = [
        "Sannu, yaya kuke?",
        "How far, wetin dey happen?",
        "Báwo ni? Ṣe dáadáa ni?",
        "Hello, how are you?"
    ]
    
    for text in texts:
        result = detector.detect_language(text)
        print(f"Text: {text}")
        print(f"Language: {result['language']} ({detector.get_language_name(result['language'])})")
        print(f"Confidence: {result['confidence']:.2f}")
        print()


# ============================================================================
# Example 4: Prompt Loading
# ============================================================================

def example_prompt_loading():
    """Using the prompt loader."""
    from app import get_prompt_loader
    
    print("Example 4: Prompt Loading")
    print("=" * 50)
    
    loader = get_prompt_loader()
    
    # Load a translation prompt
    prompt = loader.get_translation_prompt(
        source_text="Hello world",
        source_language="en",
        target_language="ha"
    )
    
    print("Generated prompt:")
    print(prompt[:500] + "...\n")


# ============================================================================
# Example 5: Question Answering with Context
# ============================================================================

def example_qa_with_context():
    """Question answering using knowledge base."""
    from app import get_wazobia_agent
    
    print("Example 5: Question Answering")
    print("=" * 50)
    
    agent = get_wazobia_agent()
    
    # Ask a question
    response = agent.process_message(
        "Tell me about Nigerian culture"
    )
    
    print(f"Question: Tell me about Nigerian culture")
    print(f"Answer: {response['response'][:200]}...")
    print(f"Sources used: {response['metadata'].get('sources', [])}\n")


# ============================================================================
# Example 6: Content Generation
# ============================================================================

def example_content_generation():
    """Generate content in Nigerian languages."""
    from app import get_wazobia_agent
    
    print("Example 6: Content Generation")
    print("=" * 50)
    
    agent = get_wazobia_agent()
    
    # Generate a story in Pidgin
    response = agent.process_message(
        "Write a short story about Lagos in Nigerian Pidgin"
    )
    
    print(f"Generated content: {response['response'][:300]}...\n")


# ============================================================================
# Example 7: Multilingual Conversation
# ============================================================================

def example_multilingual_conversation():
    """Conversation switching between languages."""
    from app import get_wazobia_agent
    
    print("Example 7: Multilingual Conversation")
    print("=" * 50)
    
    agent = get_wazobia_agent()
    
    messages = [
        "Hello!",
        "Sannu!",
        "How far?",
        "Báwo ni?"
    ]
    
    for msg in messages:
        response = agent.process_message(msg)
        print(f"User: {msg}")
        print(f"Agent ({response['language']}): {response['response']}\n")


# ============================================================================
# Example 8: API Client Usage
# ============================================================================

def example_api_client():
    """Using the REST API with Python requests."""
    import requests
    
    print("Example 8: API Client Usage")
    print("=" * 50)
    print("Note: Make sure the API server is running (python run.py)\n")
    
    base_url = "http://localhost:8000"
    
    # Chat endpoint
    response = requests.post(
        f"{base_url}/chat",
        json={"message": "Sannu, yaya kuke?", "language": "ha"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data['response']}")
        print(f"Language: {data['language']}\n")
    else:
        print(f"Error: {response.status_code}\n")
    
    # Language detection endpoint
    response = requests.post(
        f"{base_url}/detect-language",
        json={"text": "How far, wetin dey happen?"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Detected: {data['language_name']}")
        print(f"Confidence: {data['confidence']:.2f}\n")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print("\n🇳🇬 Wazobia Agent - Usage Examples\n")
    
    examples = [
        ("Basic Usage", example_basic_usage),
        ("Translation", example_translation),
        ("Language Detection", example_language_detection),
        ("Prompt Loading", example_prompt_loading),
        ("Question Answering", example_qa_with_context),
        ("Content Generation", example_content_generation),
        ("Multilingual Conversation", example_multilingual_conversation),
    ]
    
    print("Available examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")
    
    print("\nRunning all examples...\n")
    
    for name, func in examples:
        try:
            func()
            print()
        except Exception as e:
            print(f"Error in {name}: {e}\n")
    
    print("=" * 50)
    print("Examples completed!")
    print("\nNote: Some examples require:")
    print("- Knowledge base data in data/ directory")
    print("- LLM API keys configured in .env")
    print("- API server running for API client example")
