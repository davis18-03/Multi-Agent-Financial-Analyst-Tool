# 📊 Multi-Agent Financial Analyst Tool

A sophisticated AI-powered financial analysis platform that combines multiple specialized agents to provide comprehensive stock analysis, market research, and investment insights. Built with FastAPI and Streamlit, this tool leverages advanced AI agents for data processing, research, and explanation generation.

## 🎯 Project Purpose

This tool provides:
- **Real-time Stock Analysis**: Technical indicators, price charts, and trend analysis
- **AI-Powered Research**: Document retrieval and summarization from financial databases
- **Intelligent Explanations**: User-friendly analysis with visual charts and citations
- **Multi-Agent Architecture**: Specialized agents working together for comprehensive insights
- **Modern Web Interface**: Beautiful Streamlit frontend with real-time chat capabilities

## 🏗️ Architecture

### System Overview
```
┌─────────────────────────────────────────────────────────────────┐
│                    Multi-Agent Financial Analyst                │
├─────────────────────────────────────────────────────────────────┤
│  Frontend (Streamlit)           │  Backend (FastAPI)            │
│  ┌─────────────────────────────┐ │  ┌─────────────────────────────┐ │
│  │ • Chat Interface            │ │  │ • Query Orchestration       │ │
│  │ • Watchlist Management      │ │  │ • Agent Coordination        │ │
│  │ • Chart Visualization       │ │  │ • Response Processing       │ │
│  │ • Export Functions          │ │  │ • Error Handling            │ │
│  └─────────────────────────────┘ │  └─────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                           Agent Layer                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Data Agent  │  │Research Agent│  │Explainer Agent│             │
│  │ • yfinance  │  │ • RAG Store  │  │ • HTML Gen   │              │
│  │ • Technical │  │ • LLM Query  │  │ • Charts     │              │
│  │ • Charts    │  │ • Citations  │  │ • Citations  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
├─────────────────────────────────────────────────────────────────┤
│                         Service Layer                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │Data Fetcher │  │Indicators   │  │RAG Store    │              │
│  │ • API Calls │  │ • TA-Lib    │  │ • ChromaDB  │              │
│  │ • Caching   │  │ • Pandas-TA │  │ • Embeddings│              │
│  │ • Error Hdl │  │ • Plotting  │  │ • Search    │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

### Agent Responsibilities

#### 🔍 Data Agent
- **Purpose**: Fetches and processes financial data
- **Responsibilities**:
  - Stock data retrieval via yfinance
  - Technical indicator calculations (RSI, MACD, Bollinger Bands)
  - Chart generation and visualization
  - Price trend analysis
  - Data caching and optimization

#### 📚 Research Agent
- **Purpose**: Provides research and document analysis
- **Responsibilities**:
  - RAG (Retrieval-Augmented Generation) queries
  - Document search and retrieval
  - LLM-powered summarization
  - Citation management
  - Knowledge base integration

#### 💡 Explainer Agent
- **Purpose**: Creates user-friendly explanations
- **Responsibilities**:
  - Technical analysis translation
  - HTML/markdown formatting
  - Chart embedding
  - Citation formatting
  - User experience optimization

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git
- 4GB+ RAM (for GPU operations) [[memory:3819947]]

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-username/multi-agent-fin-analyst.git
cd multi-agent-fin-analyst
```

2. **Create virtual environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables** [[memory:3819944]]
```bash
cp env.example .env
# Edit .env with your API keys and configuration
```

5. **Check system requirements**
```bash
python run_app.py check
```

### Running the Application

#### Option 1: Using the Application Runner (Recommended)
```bash
# Start backend only
python run_app.py backend

# Start frontend only (in another terminal)
python run_app.py frontend

# Check system status
python run_app.py status
```

#### Option 2: Manual Commands

**Backend (FastAPI)**
```bash
uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000
```

**Frontend (Streamlit)**
```bash
streamlit run app.py --server.port 8501 --server.headless true
```

#### Access URLs
- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🛠️ Configuration

### Environment Variables (.env)

Key configuration options in your `.env` file:

```env
# LLM Configuration
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your-api-key-here

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO

# Vector Store
VECTOR_STORE_PATH=./vector_store
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Backend URL
BACKEND_URL=http://localhost:8000
```

### GPU Configuration
The project is configured to use GPU for computations when available. Ensure your system has:
- CUDA-compatible GPU (for advanced ML operations)
- Proper CUDA drivers installed
- GPU memory available for model operations

## 📱 Demo Usage Examples

### 1. Stock Analysis
```
User: "Analyze AAPL stock performance over the last 6 months"

Response: 
- Technical indicators (RSI, MACD, Bollinger Bands)
- Price charts with trend analysis
- Performance metrics and statistics
- Research citations from financial sources
```

### 2. Market Research
```
User: "What are the current trends in the tech sector?"

Response:
- Market trend analysis
- Sector performance comparison
- Research insights from financial databases
- Relevant news and analysis citations
```

### 3. Comparative Analysis
```
User: "Compare MSFT and GOOGL stocks"

Response:
- Side-by-side performance comparison
- Technical indicator comparison charts
- Financial metrics analysis
- Investment recommendation insights
```

### 4. Technical Analysis
```
User: "Show me Tesla's RSI and MACD indicators"

Response:
- Interactive charts with technical indicators
- Buy/sell signal analysis
- Historical indicator performance
- Trading recommendations
```

## 🚀 Deployment Options

### Free-Tier Deployment Links

#### Render (Recommended for Free Tier)
- **Frontend**: [Deploy to Render](https://render.com/deploy)
- **Backend**: [Deploy to Render](https://render.com/deploy)
- **Database**: Render PostgreSQL (Free tier available)

#### Railway
- **Full Stack**: [Deploy to Railway](https://railway.app/template)
- **Database**: Railway PostgreSQL (Free tier available)

#### Heroku
- **Frontend**: [Deploy to Heroku](https://dashboard.heroku.com/new-app)
- **Backend**: [Deploy to Heroku](https://dashboard.heroku.com/new-app)

#### Vercel (Frontend Only)
- **Streamlit**: [Deploy to Vercel](https://vercel.com/new)

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build individual containers
docker build -t multi-agent-fin-analyst .
docker run -p 8000:8000 -p 8501:8501 multi-agent-fin-analyst
```

## 📊 Features

### Core Capabilities
- ✅ **Real-time Stock Data**: Live price feeds and historical data
- ✅ **Technical Analysis**: 20+ technical indicators
- ✅ **AI-Powered Research**: Intelligent document search and summarization
- ✅ **Interactive Charts**: Beautiful visualizations with Plotly
- ✅ **Chat Interface**: Natural language query processing
- ✅ **Watchlist Management**: Track multiple stocks
- ✅ **Export Functions**: Download analysis reports
- ✅ **Responsive Design**: Works on desktop and mobile

### Advanced Features
- ✅ **Multi-Agent Architecture**: Specialized AI agents for different tasks
- ✅ **RAG Integration**: Retrieval-augmented generation for research
- ✅ **Caching System**: Optimized performance with intelligent caching
- ✅ **Error Handling**: Robust error recovery and user feedback
- ✅ **API Documentation**: Auto-generated OpenAPI/Swagger docs
- ✅ **Logging**: Comprehensive logging and monitoring

## 🛠️ Development

### Project Structure
```
multi-agent-fin-analyst/
├── agents/                 # AI Agent modules
│   ├── data_agent.py      # Stock data and technical analysis
│   ├── research_agent.py  # Document research and RAG
│   └── explainer_agent.py # User-friendly explanations
├── backend/               # FastAPI backend
│   └── api.py            # Main API endpoints
├── services/             # Core services
│   ├── data_fetcher.py   # Data retrieval and caching
│   ├── indicators.py     # Technical indicator calculations
│   └── rag_store.py      # Vector store and search
├── app.py                # Streamlit frontend
├── run_app.py           # Application runner script
├── requirements.txt      # Python dependencies
├── docker-compose.yml    # Docker configuration
└── README.md            # This file
```

### Adding New Features

1. **New Technical Indicators**: Add to `services/indicators.py`
2. **New Data Sources**: Extend `services/data_fetcher.py`
3. **New Agent Capabilities**: Modify respective agent files
4. **Frontend Components**: Update `app.py` with new Streamlit components

### Testing
```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=agents --cov=services tests/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check this README and inline code comments
- **Issues**: [GitHub Issues](https://github.com/your-username/multi-agent-fin-analyst/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/multi-agent-fin-analyst/discussions)

## 🙏 Acknowledgments

- **yfinance**: For providing free stock data
- **FastAPI**: For the excellent web framework
- **Streamlit**: For the beautiful frontend framework
- **LangChain**: For LLM integration capabilities
- **ChromaDB**: For vector storage and search
- **TA-Lib**: For technical analysis indicators

---

**Made with ❤️ for the financial analysis community**

*This tool is for educational and research purposes. Always consult with financial professionals before making investment decisions.*