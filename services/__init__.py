"""
Services package for Multi-Agent Financial Analyst Tool.

This package contains utility modules for data fetching, processing,
and analysis operations.
"""

from .data_fetcher import (
    DataFetcher,
    DataFetchError,
    get_historical_prices,
    get_latest_price,
    clear_cache
)

from .indicators import (
    IndicatorError,
    compute_indicators,
    plot_price_with_indicators,
    get_indicator_summary
)

from .rag_store import (
    RAGStore,
    RAGStoreError,
    DocumentResult,
    initialize_vector_store,
    ingest_documents,
    retrieve_docs
)

__all__ = [
    # Data Fetcher
    'DataFetcher',
    'DataFetchError', 
    'get_historical_prices',
    'get_latest_price',
    'clear_cache',
    # Indicators
    'IndicatorError',
    'compute_indicators',
    'plot_price_with_indicators',
    'get_indicator_summary',
    # RAG Store
    'RAGStore',
    'RAGStoreError',
    'DocumentResult',
    'initialize_vector_store',
    'ingest_documents',
    'retrieve_docs'
]

__version__ = "1.0.0"
