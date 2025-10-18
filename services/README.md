# 🔧 Services Layer - Multi-Agent Financial Analyst

This directory contains the core services that power the Multi-Agent Financial Analyst Tool.

## 📁 Structure

```
services/
├── __init__.py          # Package initialization
├── data_fetcher.py      # Stock data retrieval and caching
├── indicators.py        # Technical indicator calculations
├── rag_store.py         # Document search and retrieval
└── README.md           # This file
```

## 🗄️ Data Fetcher Service

**File**: `data_fetcher.py`

### Purpose
Handles all stock data retrieval, caching, and preprocessing operations.

### Key Features
- **yfinance Integration**: Real-time and historical stock data
- **Intelligent Caching**: LRU cache with configurable size
- **Error Handling**: Robust error recovery and fallback mechanisms
- **Data Validation**: Ensures data quality and completeness
- **Rate Limiting**: Prevents API abuse and quota exhaustion

### Usage
```python
from services.data_fetcher import DataFetcher

fetcher = DataFetcher(cache_size=128, timeout=15)
data = fetcher.get_stock_data("AAPL", "2023-01-01", "2024-01-01")
```

### Methods
- `get_stock_data(ticker, start_date, end_date)`: Fetch historical stock data
- `get_latest_price(ticker)`: Get current stock price
- `get_stock_info(ticker)`: Get company information
- `clear_cache()`: Clear the data cache

## 📊 Indicators Service

**File**: `indicators.py`

### Purpose
Calculates technical indicators and generates financial charts.

### Key Features
- **Technical Indicators**: RSI, MACD, Bollinger Bands, Moving Averages
- **Chart Generation**: Matplotlib and Plotly visualizations
- **Multiple Timeframes**: Support for different chart periods
- **Customizable Styling**: Professional chart appearance
- **Export Options**: Save charts in various formats

### Usage
```python
from services.indicators import compute_indicators, plot_price_with_indicators

# Calculate indicators
indicators = compute_indicators(data)

# Generate chart
chart_path = plot_price_with_indicators(data, indicators, ticker)
```

### Available Indicators
- **RSI (Relative Strength Index)**: Momentum oscillator
- **MACD (Moving Average Convergence Divergence)**: Trend following indicator
- **Bollinger Bands**: Volatility indicator
- **SMA/EMA (Simple/Exponential Moving Averages)**: Trend indicators
- **Volume Analysis**: Trading volume patterns

## 🔍 RAG Store Service

**File**: `rag_store.py`

### Purpose
Provides document search and retrieval capabilities for research queries.

### Key Features
- **Vector Search**: Semantic similarity search
- **Document Storage**: Efficient document indexing
- **Embedding Generation**: Text vectorization for search
- **Query Processing**: Natural language query understanding
- **Citation Management**: Source tracking and attribution

### Usage
```python
from services.rag_store import RAGStore

store = RAGStore(collection_name="financial_docs")
results = store.search_documents("stock market trends", k=5)
```

### Methods
- `add_documents(documents)`: Add documents to the store
- `search_documents(query, k=5)`: Search for relevant documents
- `get_document(id)`: Retrieve specific document
- `clear_store()`: Clear all stored documents

## 🔄 Service Integration

### Data Flow
```
User Query → Data Agent → Data Fetcher → Indicators → Charts
                ↓
            Research Agent → RAG Store → Documents
                ↓
            Explainer Agent → Format Response
```

### Error Handling
Each service includes comprehensive error handling:
- **DataFetcherError**: Data retrieval failures
- **IndicatorError**: Calculation errors
- **RAGStoreError**: Search and storage errors

### Performance Optimization
- **Caching**: Intelligent caching at multiple levels
- **Async Operations**: Non-blocking I/O where possible
- **Batch Processing**: Efficient bulk operations
- **Resource Management**: Proper cleanup and memory management

## 🛠️ Configuration

### Environment Variables
```env
# Data Fetcher
CACHE_SIZE=128
REQUEST_TIMEOUT=30

# RAG Store
VECTOR_STORE_PATH=./vector_store
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Chart Generation
CHART_SAVE_PATH=./charts
```

### Dependencies
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computations
- **matplotlib**: Chart generation
- **plotly**: Interactive visualizations
- **yfinance**: Stock data retrieval
- **chromadb**: Vector storage (future enhancement)

## 🚀 Deployment Considerations

### Minimal Deployment
For deployment, the services are designed to work with minimal dependencies:
- Core functionality available with basic packages
- Optional advanced features can be added incrementally
- Graceful degradation when optional dependencies are missing

### Scaling
- **Horizontal Scaling**: Services can be distributed across multiple instances
- **Database Integration**: Can be extended with persistent storage
- **Caching Layer**: Redis integration for distributed caching
- **Load Balancing**: Multiple service instances with load distribution

## 🔮 Future Enhancements

### Planned Features
- **Advanced Technical Indicators**: TA-Lib integration for 20+ indicators
- **Real-time Data**: WebSocket connections for live data feeds
- **Machine Learning**: Predictive models and pattern recognition
- **News Integration**: Real-time financial news and sentiment analysis
- **Portfolio Management**: Multi-stock analysis and optimization

### Performance Improvements
- **GPU Acceleration**: CUDA support for heavy computations
- **Distributed Processing**: Multi-core and multi-machine processing
- **Advanced Caching**: Redis and Memcached integration
- **Database Optimization**: Indexing and query optimization

## 📚 API Reference

### DataFetcher Class
```python
class DataFetcher:
    def __init__(self, cache_size=64, timeout=15):
        """Initialize data fetcher with caching and timeout settings."""
    
    def get_stock_data(self, ticker, start_date, end_date):
        """Fetch historical stock data for a ticker symbol."""
    
    def get_latest_price(self, ticker):
        """Get the latest price for a ticker symbol."""
    
    def get_stock_info(self, ticker):
        """Get company information for a ticker symbol."""
```

### Indicators Module
```python
def compute_indicators(data):
    """Calculate technical indicators for stock data."""
    
def plot_price_with_indicators(data, indicators, ticker):
    """Generate price chart with technical indicators."""
```

### RAGStore Class
```python
class RAGStore:
    def __init__(self, collection_name="documents"):
        """Initialize RAG store with collection name."""
    
    def search_documents(self, query, k=5):
        """Search for documents relevant to query."""
    
    def add_documents(self, documents):
        """Add documents to the store."""
```
