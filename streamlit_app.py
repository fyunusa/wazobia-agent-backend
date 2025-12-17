"""
Wazobia Agent - Streamlit Web UI
Interactive web interface for the multilingual agent
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app import get_wazobia_agent, get_language_detector


# Page configuration
st.set_page_config(
    page_title="Wazobia AI Agent",
    page_icon="🇳🇬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #008751;
        text-align: center;
        padding: 1rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        color: #1a1a1a !important;
    }
    .chat-message strong {
        color: #1a1a1a !important;
    }
    .chat-message p {
        color: #2d2d2d !important;
        margin-top: 0.5rem;
        font-size: 1rem;
        line-height: 1.6;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .agent-message {
        background-color: #f1f8e9;
        border-left: 4px solid #4caf50;
    }
    .language-badge {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-size: 0.8rem;
        font-weight: bold;
        margin-right: 0.5rem;
    }
    .badge-hausa { background-color: #ff9800; color: white; }
    .badge-pidgin { background-color: #9c27b0; color: white; }
    .badge-yoruba { background-color: #3f51b5; color: white; }
    .badge-english { background-color: #607d8b; color: white; }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'detector' not in st.session_state:
    st.session_state.detector = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'initialized' not in st.session_state:
    st.session_state.initialized = False


def initialize_agent():
    """Initialize the agent."""
    if not st.session_state.initialized:
        try:
            with st.spinner("🔄 Initializing Wazobia Agent..."):
                st.session_state.agent = get_wazobia_agent()
                st.session_state.detector = get_language_detector()
                st.session_state.initialized = True
            return True
        except Exception as e:
            st.error(f"❌ Error initializing agent: {e}")
            return False
    return True


def get_language_badge(lang_code):
    """Get HTML badge for language."""
    badges = {
        'ha': '<span class="language-badge badge-hausa">🇳🇬 Hausa</span>',
        'pcm': '<span class="language-badge badge-pidgin">🇳🇬 Pidgin</span>',
        'yo': '<span class="language-badge badge-yoruba">🇳🇬 Yoruba</span>',
        'en': '<span class="language-badge badge-english">🇬🇧 English</span>',
    }
    return badges.get(lang_code, f'<span class="language-badge">{lang_code}</span>')


def display_chat_message(role, content, language=None, intent=None):
    """Display a chat message."""
    css_class = "user-message" if role == "user" else "agent-message"
    icon = "👤" if role == "user" else "🤖"
    
    message_html = f'<div class="chat-message {css_class}">'
    message_html += f'<strong>{icon} {role.capitalize()}</strong>'
    
    if language:
        message_html += f' {get_language_badge(language)}'
    
    if intent:
        message_html += f' <span style="color: #666; font-size: 0.8rem;">({intent})</span>'
    
    message_html += f'<p style="margin-top: 0.5rem;">{content}</p>'
    message_html += '</div>'
    
    st.markdown(message_html, unsafe_allow_html=True)


def main():
    """Main application."""
    
    # Header
    st.markdown('<h1 class="main-header">🇳🇬 Wazobia Multilingual AI Agent</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Initialize agent
    if not initialize_agent():
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Language selector
        st.subheader("Supported Languages")
        st.info("""
        🇳🇬 **Hausa** - Sannu  
        🇳🇬 **Nigerian Pidgin** - How far  
        🇳🇬 **Yoruba** - Báwo ni  
        🇬🇧 **English** - Hello
        """)
        
        st.markdown("---")
        
        # Statistics
        if st.button("📊 Show Statistics"):
            stats = st.session_state.agent.get_statistics()
            st.subheader("Agent Statistics")
            st.metric("Total Conversations", stats['total_conversations'])
            
            st.write("**Knowledge Base:**")
            for lang, count in stats['knowledge_base_size'].items():
                lang_names = {'ha': 'Hausa', 'pcm': 'Pidgin', 'yo': 'Yoruba', 'all': 'Combined'}
                st.write(f"- {lang_names.get(lang, lang)}: {count:,}")
        
        st.markdown("---")
        
        # Clear history
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.session_state.agent.clear_history()
            st.success("Chat history cleared!")
            st.rerun()
        
        st.markdown("---")
        
        # Examples
        st.subheader("💡 Example Prompts")
        examples = [
            "Sannu, yaya kuke?",
            "How far, wetin dey?",
            "Báwo ni?",
            "Translate 'Good morning' to Hausa",
            "Tell me about Nigerian culture",
            "Write a story in Pidgin"
        ]
        
        for example in examples:
            if st.button(example, key=f"ex_{example}"):
                st.session_state.example_input = example
        
        st.markdown("---")
        
        # About
        with st.expander("ℹ️ About"):
            st.write("""
            **Wazobia Agent** is a multilingual AI assistant for Nigerian languages.
            
            **Features:**
            - Translation
            - Question Answering
            - Content Generation
            - Cultural Understanding
            
            Built with ❤️ for Nigerian languages.
            """)
    
    # Main chat area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("💬 Chat")
        
        # Display chat history
        if st.session_state.messages:
            for msg in st.session_state.messages:
                display_chat_message(
                    msg['role'],
                    msg['content'],
                    msg.get('language'),
                    msg.get('intent')
                )
        else:
            st.info("👋 Start a conversation in any supported language!")
    
    with col2:
        st.subheader("🔍 Tools")
        
        # Language detection
        with st.expander("Language Detector"):
            detect_text = st.text_area("Enter text to detect language:", height=100)
            if st.button("Detect Language"):
                if detect_text:
                    detection = st.session_state.detector.detect_language(detect_text)
                    
                    st.success(f"**Detected:** {st.session_state.detector.get_language_name(detection['language'])}")
                    st.info(f"**Confidence:** {detection['confidence']:.2%}")
                    
                    st.write("**All Scores:**")
                    for lang, score in detection['scores'].items():
                        st.progress(score, text=f"{lang}: {score:.2%}")
                    
                    if detection['is_mixed']:
                        st.warning("⚠️ Mixed language detected")
        
        # Quick actions
        with st.expander("Quick Actions"):
            if st.button("📝 Translate"):
                st.session_state.example_input = "Translate 'Hello' to Hausa"
                st.rerun()
            
            if st.button("❓ Ask Question"):
                st.session_state.example_input = "Tell me about Nigeria"
                st.rerun()
            
            if st.button("✍️ Generate Content"):
                st.session_state.example_input = "Write a short story in Pidgin"
                st.rerun()
    
    # Chat input (must be outside columns)
    user_input = st.chat_input("Type your message here...")
    
    # Handle example input from sidebar
    if 'example_input' in st.session_state:
        user_input = st.session_state.example_input
        del st.session_state.example_input
    
    if user_input:
        # Add user message
        st.session_state.messages.append({
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now().isoformat()
        })
        
        # Get agent response
        with st.spinner("🤔 Thinking..."):
            try:
                response_data = st.session_state.agent.process_message(user_input)
                
                # Add agent message
                st.session_state.messages.append({
                    'role': 'agent',
                    'content': response_data['response'],
                    'language': response_data['language'],
                    'intent': response_data['intent'],
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                st.error(f"❌ Error: {e}")
        
        st.rerun()


if __name__ == "__main__":
    main()
