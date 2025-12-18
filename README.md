# Wazobia Multilingual AI Agent 🇳🇬

A powerful multilingual AI agent for Nigerian languages supporting **Hausa**, **Nigerian Pidgin**, and **Yoruba**. Built with modern Python and designed for natural language processing, translation, and cultural understanding of Nigerian languages.

## 🌟 Features

### Core Capabilities
- **🗣️ Multilingual Support**: Seamlessly handle Hausa, Nigerian Pidgin, Yoruba, and English
- **🔄 Translation**: Accurate translation between Nigerian languages and English
- **🤖 Intelligent Conversations**: Context-aware chat with cultural understanding
- **📚 Knowledge Base**: RAG-powered responses using Nigerian language datasets
- **🎨 Content Generation**: Create articles, stories, and more in Nigerian languages
- **🔍 Language Detection**: Automatically identify the language being used
- **💬 Cultural Context**: Understanding of Nigerian proverbs, idioms, and cultural references

### Technical Features
- **XML-Tagged Prompts**: Well-structured, maintainable prompt system
- **Prompt Loader Service**: Centralized prompt management with dynamic loading
- **RESTful API**: FastAPI-based endpoints for easy integration
- **Modular Architecture**: Clean separation of concerns
- **RAG Support**: Retrieval-Augmented Generation for accurate responses
- **Type Safety**: Full Pydantic models and type hints

## 📁 Project Structure

```
wazobia-agent/
├── app/
│   ├── __init__.py              # Package initialization
│   ├── agent.py                 # Core agent logic with RAG
│   ├── api.py                   # FastAPI REST endpoints
│   ├── config.py                # Configuration management
│   ├── language_detector.py    # Language detection service
│   ├── prompt_loader.py        # Prompt loading and formatting
│   └── prompts.py              # XML-tagged prompt templates
├── data/
│   ├── bbc_hausa_scraped.json
│   ├── bbc_pidgin_scraped.json
│   ├── bbc_yoruba_scraped.json
│   └── combined_wazobia_dataset.json
├── tests/                       # Unit and integration tests
├── .env.example                 # Environment variables template
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or navigate to the wazobia-agent directory
cd wazobia-agent

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
# For example, if using OpenAI:
# WAZOBIA_OPENAI_API_KEY=sk-your-key-here
```

### 3. Run the API Server

```bash
# Start the server
python -m uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```

Visit http://localhost:8000/docs for interactive API documentation.

## 💻 Usage Examples

### Using the API

#### 1. Chat/Conversation
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Sannu, yaya kuke?",
    "language": "ha"
  }'
```

#### 2. Translation
```bash
curl -X POST "http://localhost:8000/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, how are you?",
    "source_language": "en",
    "target_language": "ha"
  }'
```

#### 3. Language Detection
```bash
curl -X POST "http://localhost:8000/detect-language" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "How far, wetin dey happen?"
  }'
```

#### 4. Content Generation
```bash
curl -X POST "http://localhost:8000/generate-content" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Nigerian independence",
    "content_type": "article",
    "language": "pcm"
  }'
```

### Using the Python API

```python
from app import get_wazobia_agent

# Initialize agent
agent = get_wazobia_agent()

# Process a message
response = agent.process_message("Sannu, yaya kuke?")
print(response['response'])

# Translation
result = agent.process_message(
    "Translate 'Good morning' to Yoruba"
)
print(result['response'])

# Get statistics
stats = agent.get_statistics()
print(f"Knowledge base size: {stats['knowledge_base_size']}")
```

## 🎯 Prompt System

The agent uses a sophisticated XML-tagged prompt system for maintainability and clarity:

### Example Prompt Structure
```python
<TRANSLATION_INSTRUCTION>
    <TASK>
        Translate the following text from {source_language} to {target_language}.
    </TASK>
    
    <SOURCE_TEXT>
        {source_text}
    </SOURCE_TEXT>
    
    <REQUIREMENTS>
        <REQUIREMENT>Preserve cultural context</REQUIREMENT>
        <REQUIREMENT>Use natural language</REQUIREMENT>
    </REQUIREMENTS>
</TRANSLATION_INSTRUCTION>
```

### Available Prompt Categories
- `SYSTEM_CORE` - Base system instructions
- `TRANSLATION_TASK` - Translation operations
- `QUESTION_ANSWERING` - Q&A with RAG
- `CONTENT_GENERATION` - Content creation
- `CULTURAL_EXPLANATION` - Cultural context
- `PROVERB_EXPLANATION` - Proverbs and idioms
- `LANGUAGE_TEACHING` - Language lessons
- `CASUAL_CONVERSATION` - Chat interactions
- `GREETING_RESPONSE` - Greetings
- And more...

## 🔧 Configuration

Configuration is managed through environment variables (prefixed with `WAZOBIA_`):

```bash
# LLM Settings
WAZOBIA_LLM_PROVIDER=openai
WAZOBIA_DEFAULT_MODEL=gpt-4
WAZOBIA_TEMPERATURE=0.7

# Agent Settings
WAZOBIA_MAX_CONVERSATION_HISTORY=10
WAZOBIA_RETRIEVAL_TOP_K=5

# API Settings
WAZOBIA_API_HOST=0.0.0.0
WAZOBIA_API_PORT=8000
```

See [`.env.example`](.env.example) for all options.

## 🌍 Supported Languages

| Language | Code | Native Name | Status |
|----------|------|-------------|--------|
| Hausa | `ha` | Hausa | ✅ Active |
| Nigerian Pidgin | `pcm` | Naija Pidgin | ✅ Active |
| Yoruba | `yo` | Yorùbá | ✅ Active |
| English | `en` | English | ✅ Active |

## 📚 Knowledge Base

The agent leverages a rich knowledge base of Nigerian language content:

- **BBC Hausa**: News and articles in Hausa
- **BBC Pidgin**: Nigerian Pidgin content
- **BBC Yoruba**: Yoruba language materials
- **Combined Dataset**: ~24,000+ documents

The RAG system retrieves relevant context from these sources to provide accurate, culturally-appropriate responses.

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_agent.py
```

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/chat` | POST | Process chat messages |
| `/translate` | POST | Translate text |
| `/detect-language` | POST | Detect language |
| `/generate-content` | POST | Generate content |
| `/stats` | GET | Agent statistics |
| `/languages` | GET | Supported languages |
| `/clear-history` | POST | Clear conversation history |

Full API documentation: http://localhost:8000/docs

## 🏗️ Architecture

### Component Overview

```
┌─────────────────────────────────────────┐
│           FastAPI REST API              │
├─────────────────────────────────────────┤
│          WazobiaAgent (Core)            │
│  ┌──────────────────────────────────┐   │
│  │  Language Detector               │   │
│  │  Prompt Loader                   │   │
│  │  RAG Retrieval                   │   │
│  │  Intent Detection                │   │
│  └──────────────────────────────────┘   │
├─────────────────────────────────────────┤
│         Knowledge Base (Data)           │
│  - Hausa, Pidgin, Yoruba datasets       │
└─────────────────────────────────────────┘
```

### Key Design Patterns

1. **Singleton Pattern**: Agent, detector, and loader instances
2. **Factory Pattern**: Prompt creation and formatting
3. **Strategy Pattern**: Different handlers for different intents
4. **Repository Pattern**: Knowledge base access

## 🎨 Advanced Features

### Custom Prompt Loading
```python
from app import get_prompt_loader

loader = get_prompt_loader()

# Load and format a prompt
prompt = loader.load_prompt(
    'TRANSLATION_TASK',
    source_language='English',
    target_language='Hausa',
    source_text='Hello world'
)
```

### Language Detection
```python
from app import get_language_detector

detector = get_language_detector()

result = detector.detect_language("Sannu, yaya kuke?")
# {'language': 'ha', 'confidence': 0.85, ...}
```

### Extending the Agent

Add new capabilities by:
1. Adding prompts to `prompts.py`
2. Implementing handlers in `agent.py`
3. Creating API endpoints in `api.py`

## 📖 Documentation

### Prompt Format Guidelines

All prompts use XML-like tags for structure:

```xml
<INSTRUCTION_TYPE>
    <TASK>What to do</TASK>
    <REQUIREMENTS>
        <REQUIREMENT>Specific requirement</REQUIREMENT>
    </REQUIREMENTS>
    <OUTPUT_FORMAT>Expected output format</OUTPUT_FORMAT>
</INSTRUCTION_TYPE>
```

### Adding New Languages

1. Add language keywords to `language_detector.py`
2. Update `LANGUAGE_CONFIG` in `config.py`
3. Add language-specific prompts to `prompts.py`
4. Add training data to `data/` directory

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- [ ] Add more Nigerian languages (Igbo, Fulani, etc.)
- [ ] Enhanced embedding-based retrieval
- [ ] Voice input/output support
- [ ] Fine-tuned models for Nigerian languages
- [ ] Mobile app integration
- [ ] Real-time translation

## 📄 License

MIT License - see LICENSE file for details

## 👥 Author

**Umar Farouk Yunusa**  
Department of Science Education  
Northwest University, Kano

## 🙏 Acknowledgments

- BBC for Nigerian language content
- Nigerian linguistic research community
- Open source NLP tools and libraries

## 📞 Support

For questions or issues:
- Create an issue in the repository
- Contact: [Your contact information]

## 🗺️ Roadmap

### Phase 1 (Current) ✅
- [x] Core multilingual agent
- [x] Language detection
- [x] Translation capabilities
- [x] REST API
- [x] Knowledge base integration

### Phase 2 (Next)
- [ ] Advanced embeddings with vector DB
- [ ] Fine-tuned models
- [ ] Web UI
- [ ] Enhanced cultural context

### Phase 3 (Future)
- [ ] Mobile applications
- [ ] Voice support
- [ ] Real-time collaboration
- [ ] Educational modules

---

**Wazobia** means "Come" in the three major Nigerian languages (Wa=Yoruba, Zo=Hausa, Bia=Igbo), symbolizing unity in diversity. 🇳🇬
