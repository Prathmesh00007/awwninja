# Check DEMO VIDEO in the repo itself. It is named as demo.mp4

# AwwNews-AI-Powered Audio Briefs from News & Reddit

Intelligent news aggregation meets conversational AI. AwwNews autonomously collects current headlines and community perspectives from Reddit, synthesizing them into immersive audio briefings delivered through advanced text-to-speech technology.

## Visual Overview
[](https://prathmesh00007.github.io/awwninja/)


## Key Capabilities

- **Multi-Source News Aggregation**: Access premium news content with paywall bypassing through advanced proxy infrastructure
- **Real-Time Social Intelligence**: Extract authentic community perspectives and discussions directly from Reddit's live platform data
- **Natural Audio Generation**: Convert synthesized news briefs into natural-sounding speech using AI text-to-speech engines
- **Intelligent Web Scraping**: Leverage sophisticated proxy and browser automation technologies for reliable data collection

## System Requirements

| Component | Specification |
|-----------|---------------|
| Python | 3.12+ |
| Proxy Service | Bright Data account ([brightdata.com](https://brightdata.com)) |
| TTS Engine | MURF API ([murf.ai](https://murf.ai/api/docs/introduction/overview)) OR ElevenLabs ([elevenlabs.io](https://elevenlabs.io)) |
| LLM Provider | Google Gemini ([aistudio.google.com](https://aistudio.google.com/apikey)) |

## Installation & Configuration

### Step 1: Clone Repository
```bash
git clone https://github.com/prathmesh00007/awwninja.git
cd awwninja
```

### Step 2: Install Dependencies
```bash
pipenv install
pipenv shell
```

### Step 3: Environment Variables Setup

Copy the template configuration:
```bash
cp .env.example .env
```

Add the following credentials to your `.env` file:

**Web Scraping (Bright Data)**:
```
BRIGHTDATA_MCP_KEY=your_mcp_api_key
WEB_UNLOCKER_ZONE=your_zone_name
BROWSER_AUTH=your_browser_auth_token
API_TOKEN=your_bright_data_token
```

**Language Model**:
```
GEMINI_API_KEY=your_gemini_api_key
```

**Text-to-Speech (Choose One)**:
```
MURF_API_KEY=your_murf_api_key
MURF_WORKSPACE_ID=your_murf_workspace_name
```
OR
```
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

**Configuration Notes**:
- `BRIGHTDATA_MCP_KEY`: Mobile Collector Proxy credentials for web scraping functionality
- `WEB_UNLOCKER_ZONE`: Zone identifier configured within your Bright Data account for paywall bypassing
- `BROWSER_AUTH`: Authentication credentials for browser-based automated operations
- `API_TOKEN`: Alternative/backup Bright Data authentication token
- `GEMINI_API_KEY`: Google's generative AI model for content summarization
- `MURF_API_KEY` & `MURF_WORKSPACE_ID`: MURF platform credentials for audio synthesis (recommended)
- `ELEVENLABS_API_KEY`: ElevenLabs alternative for text-to-speech conversion
- **Important**: Select either Gemini for LLM processing and either MURF or ElevenLabs for audio generation

### Step 4: Bright Data Configuration

Configure your web scraping proxy infrastructure:
1. Access Bright Data Control Panel: https://brightdata.com/cp/zones
2. Create a new MCP zone for web scraping
3. Enable browser authentication for JavaScript-heavy sites
4. Copy your credentials to the `.env` file

## Running the Application

**Terminal 1 - Backend Service**:
```bash
pipenv run python backend.py
```

**Terminal 2 - Web Interface**:
```bash
pipenv run streamlit run frontend.py
```

## Project Architecture

```
├── frontend.py           # Streamlit web interface
├── backend.py            # Core API and data processing engine
├── news_scraper.py       # News content acquisition module
├── reddit_scraper.py     # Reddit discussion collection
├── models.py             # Pydantic data models
├── utils.py              # Shared utility functions
├── test_murf.py          # MURF API integration testing
├── Pipfile               # Python dependency specification
├── requirements.txt      # Alternative dependency manifest
├── .env.example          # Template environment configuration
└── audio/                # Generated audio file storage
```

## Implementation Notes

- Initial data collection requires 15-20 seconds for optimal results
- Reddit data extraction employs real browser emulation through proxy infrastructure
- Sensitive credentials in `.env` must not be committed to version control
- Audio files are generated and stored in the `audio/` directory 

