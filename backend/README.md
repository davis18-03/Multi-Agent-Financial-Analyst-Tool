# 🚀 Multi-Agent Financial Analyst - Backend

This directory contains the FastAPI backend for the Multi-Agent Financial Analyst Tool.

## 📁 Structure

```
backend/
├── api.py                    # Main FastAPI application
├── requirements.txt          # Full dependencies (development)
├── requirements-minimal.txt  # Minimal dependencies (deployment)
└── README.md                # This file
```

## 🛠️ Development Setup

### Local Development

1. **Install dependencies**
```bash
# For full development environment
pip install -r requirements.txt

# For minimal deployment environment
pip install -r requirements-minimal.txt
```

2. **Run the server**
```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

3. **Access API documentation**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔧 Configuration

### Environment Variables

Required environment variables:

```env
# LLM Configuration
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here
LLM_PROVIDER=openrouter
LLM_MODEL_NAME=openai/gpt-3.5-turbo

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Optional Environment Variables

```env
# Data Configuration
CACHE_SIZE=128
REQUEST_TIMEOUT=30

# Vector Store (for future enhancements)
VECTOR_STORE_PATH=./vector_store
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Chart Configuration
CHART_SAVE_PATH=./charts

# CORS Configuration
CORS_ORIGINS=http://localhost:8501
```

## 📡 API Endpoints

### Health Check
```
GET /health
```
Returns the health status of the API.

### Process Query
```
POST /query
```
Main endpoint for processing financial analysis queries.

**Request Body:**
```json
{
  "user_id": "string",
  "query": "string"
}
```

**Response:**
```json
{
  "answer_html": "string",
  "charts": ["string"],
  "citations": [{"title": "string", "source": "string"}],
  "metadata": {},
  "processing_time": 0.0,
  "success": true
}
```

### Get Ticker Info
```
GET /tickers/{ticker}
```
Get basic information about a ticker symbol.

### Search Documents
```
GET /search?query={query}&k={k}
```
Search documents in the knowledge base.

## 🏗️ Architecture

### Multi-Agent System

The backend orchestrates three specialized agents:

1. **Data Agent** (`agents/data_agent.py`)
   - Fetches stock data via yfinance
   - Calculates technical indicators
   - Generates charts

2. **Research Agent** (`agents/research_agent.py`)
   - Performs document search
   - Generates research summaries
   - Manages citations

3. **Explainer Agent** (`agents/explainer_agent.py`)
   - Creates user-friendly explanations
   - Formats responses as HTML
   - Embeds charts and citations

### Services Layer

- **Data Fetcher** (`services/data_fetcher.py`): Stock data retrieval and caching
- **Indicators** (`services/indicators.py`): Technical indicator calculations
- **RAG Store** (`services/rag_store.py`): Document search and retrieval

## 🚀 Deployment

### Render.com Deployment

The backend is configured for deployment on Render.com using:

- `render.yaml` - Deployment configuration
- `requirements-minimal.txt` - Optimized dependencies
- `runtime.txt` - Python version specification

### Build Process

```bash
pip install --upgrade pip
pip install --no-cache-dir -r backend/requirements-minimal.txt
cd backend && uvicorn api:app --host 0.0.0.0 --port $PORT
```

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure all dependencies are installed
   - Check Python path configuration

2. **API Key Issues**
   - Verify OPENROUTER_API_KEY is set correctly
   - Check API key permissions and quotas

3. **Data Fetching Errors**
   - yfinance may have rate limits
   - Check network connectivity

4. **Chart Generation Issues**
   - Ensure matplotlib backend is properly configured
   - Check file permissions for chart output directory

### Logs

The application uses structured logging with loguru. Logs are written to:
- Console output (for development)
- `logs/api.log` (for production)

## 📈 Performance

### Optimization Features

- **Caching**: LRU cache for frequently accessed data
- **Async Processing**: Non-blocking I/O operations
- **Connection Pooling**: Efficient HTTP client usage
- **Parallel Processing**: Concurrent agent execution

### Monitoring

- Health check endpoint for uptime monitoring
- Processing time metrics
- Error rate tracking
- Memory usage monitoring

## 🔮 Future Enhancements

- **Database Integration**: Persistent storage for user data
- **Advanced Caching**: Redis for distributed caching
- **Rate Limiting**: API usage controls
- **Authentication**: User management and security
- **WebSocket Support**: Real-time updates
- **Advanced Analytics**: Performance metrics and insights

## 📚 API Documentation

When the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

The API documentation is automatically generated from the FastAPI code and includes:
- Request/response schemas
- Example requests
- Interactive testing interface
- Authentication requirements
