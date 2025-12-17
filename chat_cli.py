#!/usr/bin/env python3
"""
Wazobia Agent - Terminal Chat Interface
Interactive command-line chat with the agent
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app import get_wazobia_agent, get_language_detector


def print_banner():
    """Print welcome banner."""
    print("\n" + "="*60)
    print("🇳🇬  WAZOBIA MULTILINGUAL AI AGENT")
    print("="*60)
    print("Languages: Hausa | Nigerian Pidgin | Yoruba | English")
    print("="*60)
    print("\nCommands:")
    print("  /help     - Show help")
    print("  /stats    - Show statistics")
    print("  /clear    - Clear conversation history")
    print("  /detect   - Detect language of next message")
    print("  /quit     - Exit chat")
    print("\nType your message and press Enter to chat!")
    print("="*60 + "\n")


def print_help():
    """Print help information."""
    print("\n📚 HELP")
    print("="*60)
    print("How to use:")
    print("  - Just type naturally in any supported language")
    print("  - The agent will detect your language automatically")
    print("  - Try greetings: 'Sannu', 'How far', 'Báwo ni', 'Hello'")
    print("  - Ask for translations: 'Translate X to Y'")
    print("  - Ask questions: 'Tell me about Nigeria'")
    print("  - Generate content: 'Write a story in Pidgin'")
    print("\nExamples:")
    print("  User: Sannu, yaya kuke?")
    print("  User: How far, wetin dey happen?")
    print("  User: Translate 'Good morning' to Hausa")
    print("  User: Tell me about Nigerian culture")
    print("="*60 + "\n")


def print_stats(agent):
    """Print agent statistics."""
    stats = agent.get_statistics()
    print("\n📊 STATISTICS")
    print("="*60)
    print(f"Total conversations: {stats['total_conversations']}")
    print(f"Languages supported: {', '.join(stats['languages_supported'])}")
    print("\nKnowledge Base Size:")
    for lang, count in stats['knowledge_base_size'].items():
        lang_names = {'ha': 'Hausa', 'pcm': 'Pidgin', 'yo': 'Yoruba', 'all': 'Combined'}
        print(f"  {lang_names.get(lang, lang)}: {count:,} documents")
    print("="*60 + "\n")


def format_response(response_data):
    """Format agent response for display."""
    response = response_data['response']
    language = response_data['language']
    intent = response_data['intent']
    
    # Language flags
    lang_flags = {
        'ha': '🇳🇬 Hausa',
        'pcm': '🇳🇬 Pidgin',
        'yo': '🇳🇬 Yoruba',
        'en': '🇬🇧 English'
    }
    
    lang_display = lang_flags.get(language, language)
    
    return f"\n💬 Agent [{lang_display} | {intent}]:\n{response}\n"


def main():
    """Main chat loop."""
    print_banner()
    
    # Initialize agent
    print("🔄 Initializing agent...")
    try:
        agent = get_wazobia_agent()
        detector = get_language_detector()
        print("✅ Agent ready!\n")
    except Exception as e:
        print(f"❌ Error initializing agent: {e}")
        print("Make sure you're in the wazobia-agent directory")
        return
    
    detect_mode = False
    
    # Main chat loop
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.startswith('/'):
                command = user_input.lower()
                
                if command == '/quit' or command == '/exit':
                    print("\n👋 Ka sai anjima! (Goodbye!)\n")
                    break
                
                elif command == '/help':
                    print_help()
                    continue
                
                elif command == '/stats':
                    print_stats(agent)
                    continue
                
                elif command == '/clear':
                    agent.clear_history()
                    print("✅ Conversation history cleared\n")
                    continue
                
                elif command == '/detect':
                    detect_mode = True
                    print("🔍 Language detection mode ON (next message only)\n")
                    continue
                
                else:
                    print(f"❌ Unknown command: {command}")
                    print("Type /help for available commands\n")
                    continue
            
            # Language detection mode
            if detect_mode:
                detection = detector.detect_language(user_input)
                print("\n🔍 LANGUAGE DETECTION")
                print("="*60)
                print(f"Text: {user_input}")
                print(f"Detected: {detector.get_language_name(detection['language'])}")
                print(f"Confidence: {detection['confidence']:.2%}")
                print(f"All scores: {detection['scores']}")
                print(f"Mixed language: {detection['is_mixed']}")
                print("="*60 + "\n")
                detect_mode = False
                continue
            
            # Process message with agent
            print("🤔 Thinking...")
            response_data = agent.process_message(user_input)
            
            # Display response
            print(format_response(response_data))
            
        except KeyboardInterrupt:
            print("\n\n👋 Chat interrupted. Goodbye!\n")
            break
        
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            print("Type /help for assistance or /quit to exit\n")


if __name__ == "__main__":
    main()
