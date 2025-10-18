"""
FastAPI Backend for Multi-Agent Financial Analyst Tool

This module provides a REST API that orchestrates multiple agents to provide
comprehensive financial analysis and research capabilities.

Author: Multi-Agent Financial Analyst Tool
Version: 1.0.0
"""

import sys
import os
import re
import asyncio
import concurrent.futures
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

# FastAPI and related imports
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
import uvicorn

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import agents
from agents.data_agent import DataAgent, DataAgentError
from agents.research_agent import ResearchAgent, ResearchAgentError
from agents.explainer_agent import ExplainerAgent, ExplainerAgentError

# Import services for direct access if needed
from services.data_fetcher import DataFetcher
from services.rag_store import RAGStore

# Logging
from loguru import logger


# Request/Response Models
class QueryRequest(BaseModel):
    """Request model for the /query endpoint."""
    user_id: str = Field(..., description="Unique user identifier")
    query: str = Field(..., min_length=1, max_length=1000, description="User query")
    
    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()


class QueryResponse(BaseModel):
    """Response model for the /query endpoint."""
    answer_html: str = Field(..., description="HTML formatted answer")
    charts: List[str] = Field(default=[], description="List of chart URLs")
    citations: List[Dict[str, str]] = Field(default=[], description="List of citations")
    metadata: Dict[str, Any] = Field(default={}, description="Response metadata")
    processing_time: float = Field(..., description="Total processing time in seconds")
    success: bool = Field(..., description="Whether the query was successful")


class HealthResponse(BaseModel):
    """Response model for the /health endpoint."""
    status: str = Field(..., description="Health status")
    timestamp: str = Field(..., description="Current timestamp")
    version: str = Field(..., description="API version")
    uptime: float = Field(..., description="Uptime in seconds")


# Global variables for app state
app_start_time = datetime.now()
data_agent = None
research_agent = None
explainer_agent = None
executor = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    global data_agent, research_agent, explainer_agent, executor
    
    # Startup
    logger.info("Starting Multi-Agent Financial Analyst API...")
    
    try:
        # Initialize agents
        logger.info("Initializing agents...")
        data_agent = DataAgent(cache_size=128, timeout=15)
        research_agent = ResearchAgent(
            collection_name="financial_docs",
            llm_provider="fallback"  # Use fallback for demo, can be configured
        )
        explainer_agent = ExplainerAgent(
            include_emojis=True,
            output_format="html",
            include_citations=True
        )
        
        # Initialize thread pool executor for parallel processing
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        
        logger.info("API startup completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize agents: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Multi-Agent Financial Analyst API...")
    if executor:
        executor.shutdown(wait=True)


# Create FastAPI app
app = FastAPI(
    title="Multi-Agent Financial Analyst API",
    description="A comprehensive financial analysis API powered by multiple AI agents",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Utility Functions
def detect_tickers_and_keywords(query: str) -> Dict[str, Any]:
    """
    Detect ticker symbols and financial keywords in the query.
    
    Args:
        query (str): User query
        
    Returns:
        Dict[str, Any]: Detection results
    """
    try:
        # Common ticker patterns (1-5 uppercase letters, possibly with dots or hyphens)
        ticker_pattern = r'\b[A-Z]{1,5}(?:[.-][A-Z]{1,3})?\b'
        
        # Financial keywords
        financial_keywords = [
            'stock', 'stocks', 'share', 'shares', 'price', 'prices',
            'market', 'markets', 'trading', 'trade', 'invest', 'investment',
            'portfolio', 'volatility', 'trend', 'analysis', 'analyst',
            'earnings', 'revenue', 'profit', 'loss', 'dividend', 'yield',
            'bull', 'bear', 'bullish', 'bearish', 'buy', 'sell', 'hold',
            'rsi', 'macd', 'bollinger', 'moving average', 'sma', 'ema',
            'volume', 'chart', 'technical', 'fundamental', 'sector', 'industry'
        ]
        
        # Find potential tickers (uppercase words)
        potential_tickers = re.findall(ticker_pattern, query.upper())
        
        # Filter out common words that aren't tickers
        common_words = {'THE', 'AND', 'OR', 'BUT', 'FOR', 'WITH', 'FROM', 'TO', 'OF', 'IN', 'ON', 'AT', 'BY'}
        detected_tickers = [ticker for ticker in potential_tickers if ticker not in common_words]
        
        # Find financial keywords
        query_lower = query.lower()
        detected_keywords = [keyword for keyword in financial_keywords if keyword in query_lower]
        
        # Determine query type
        if detected_tickers:
            query_type = 'ticker_analysis'
        elif detected_keywords:
            query_type = 'financial_research'
        else:
            query_type = 'general'
        
        return {
            'tickers': detected_tickers,
            'keywords': detected_keywords,
            'query_type': query_type,
            'has_financial_content': len(detected_keywords) > 0 or len(detected_tickers) > 0
        }
        
    except Exception as e:
        logger.error(f"Error detecting tickers and keywords: {str(e)}")
        return {
            'tickers': [],
            'keywords': [],
            'query_type': 'general',
            'has_financial_content': False
        }


def extract_date_range_from_query(query: str) -> Dict[str, str]:
    """
    Extract date range from query if mentioned.
    
    Args:
        query (str): User query
        
    Returns:
        Dict[str, str]: Start and end dates
    """
    try:
        # Default date range (last 1 year)
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        # Look for date patterns
        date_patterns = [
            r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
            r'(\d{1,2})/(\d{1,2})/(\d{4})',  # MM/DD/YYYY
            r'(\d{1,2})-(\d{1,2})-(\d{4})',  # MM-DD-YYYY
        ]
        
        # Look for relative date mentions
        if 'last year' in query.lower() or 'past year' in query.lower():
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        elif 'last 6 months' in query.lower() or 'past 6 months' in query.lower():
            start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
        elif 'last 3 months' in query.lower() or 'past 3 months' in query.lower():
            start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        elif 'last month' in query.lower() or 'past month' in query.lower():
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        elif 'last week' in query.lower() or 'past week' in query.lower():
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        return {
            'start_date': start_date,
            'end_date': end_date
        }
        
    except Exception as e:
        logger.error(f"Error extracting date range: {str(e)}")
        return {
            'start_date': (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'),
            'end_date': datetime.now().strftime('%Y-%m-%d')
        }


async def run_data_analysis(ticker: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """Run data analysis for a ticker symbol."""
    try:
        logger.info(f"Starting data analysis for {ticker}")
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            executor,
            data_agent.analyze_ticker,
            ticker,
            start_date,
            end_date
        )
        
        logger.info(f"Data analysis completed for {ticker}")
        return result
        
    except Exception as e:
        logger.error(f"Data analysis failed for {ticker}: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'ticker': ticker
        }


async def run_research_analysis(query: str, k: int = 3) -> List[Dict[str, Any]]:
    """Run research analysis for a query."""
    try:
        logger.info(f"Starting research analysis for query: {query[:50]}...")
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            executor,
            research_agent.research_query,
            query,
            k
        )
        
        logger.info(f"Research analysis completed")
        return result
        
    except Exception as e:
        logger.error(f"Research analysis failed: {str(e)}")
        return []


async def create_explanation(analysis_result: Dict[str, Any], research_results: List[Dict[str, Any]]) -> str:
    """Create explanation from analysis and research results."""
    try:
        logger.info("Creating explanation...")
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            executor,
            explainer_agent.explain_analysis,
            analysis_result,
            research_results
        )
        
        logger.info("Explanation created successfully")
        return result
        
    except Exception as e:
        logger.error(f"Explanation creation failed: {str(e)}")
        return f"<p>Error creating explanation: {str(e)}</p>"


# API Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    uptime = (datetime.now() - app_start_time).total_seconds()
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        uptime=uptime
    )


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest, background_tasks: BackgroundTasks):
    """
    Process a financial analysis query.
    
    This endpoint orchestrates multiple agents to provide comprehensive
    financial analysis and research based on the user's query.
    """
    start_time = datetime.now()
    
    try:
        logger.info(f"Processing query from user {request.user_id}: {request.query[:50]}...")
        
        # Step 1: Analyze query
        detection_results = detect_tickers_and_keywords(request.query)
        date_range = extract_date_range_from_query(request.query)
        
        logger.info(f"Query analysis: {detection_results}")
        
        # Step 2: Initialize results
        analysis_result = None
        research_results = []
        charts = []
        citations = []
        
        # Step 3: Execute parallel analysis based on query type
        if detection_results['query_type'] == 'ticker_analysis' and detection_results['tickers']:
            # Ticker analysis - run both data analysis and research
            ticker = detection_results['tickers'][0]  # Use first detected ticker
            
            # Run parallel tasks
            data_task = run_data_analysis(ticker, date_range['start_date'], date_range['end_date'])
            research_task = run_research_analysis(request.query, k=3)
            
            # Wait for both to complete
            analysis_result, research_results = await asyncio.gather(data_task, research_task)
            
            # Extract charts from analysis result
            if analysis_result and analysis_result.get('chart_path'):
                charts.append(analysis_result['chart_path'])
                
        elif detection_results['has_financial_content']:
            # Financial research query - run research only
            research_results = await run_research_analysis(request.query, k=5)
            
        else:
            # General query - provide helpful response
            research_results = [{
                'title': 'General Query',
                'summary': 'This appears to be a general query. For financial analysis, please mention specific ticker symbols (like AAPL, MSFT) or financial terms.',
                'source': 'System',
                'score': 1.0,
                'query_relevance': 'medium'
            }]
        
        # Step 4: Create explanation
        if analysis_result and analysis_result.get('status') != 'error':
            answer_html = await create_explanation(analysis_result, research_results)
        else:
            # Create simple explanation for research-only results
            answer_html = "<h2>Research Results</h2>"
            for i, result in enumerate(research_results[:3], 1):
                answer_html += f"""
                <div style="margin-bottom: 20px; padding: 15px; border-left: 4px solid #007bff; background: #f8f9fa;">
                    <h3>{i}. {result.get('title', 'Untitled')}</h3>
                    <p>{result.get('summary', 'No summary available')}</p>
                    <small>Source: {result.get('source', 'Unknown')}</small>
                </div>
                """
        
        # Step 5: Extract citations
        for result in research_results:
            if result.get('source') and result.get('source') != 'System':
                citations.append({
                    'title': result.get('title', 'Untitled'),
                    'source': result.get('source', 'Unknown'),
                    'relevance': result.get('query_relevance', 'unknown')
                })
        
        # Step 6: Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Step 7: Prepare metadata
        metadata = {
            'query_type': detection_results['query_type'],
            'detected_tickers': detection_results['tickers'],
            'detected_keywords': detection_results['keywords'],
            'date_range': date_range,
            'analysis_status': analysis_result.get('status') if analysis_result else 'not_applicable',
            'research_count': len(research_results),
            'user_id': request.user_id
        }
        
        logger.info(f"Query processed successfully in {processing_time:.2f}s")
        
        return QueryResponse(
            answer_html=answer_html,
            charts=charts,
            citations=citations,
            metadata=metadata,
            processing_time=processing_time,
            success=True
        )
        
    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        error_msg = f"Query processing failed: {str(e)}"
        logger.error(error_msg)
        
        # Return error response
        return QueryResponse(
            answer_html=f"<div class='error'><h2>Error</h2><p>{error_msg}</p></div>",
            charts=[],
            citations=[],
            metadata={
                'error': str(e),
                'user_id': request.user_id,
                'processing_time': processing_time
            },
            processing_time=processing_time,
            success=False
        )


@app.get("/tickers/{ticker}")
async def get_ticker_info(ticker: str):
    """Get basic information about a ticker symbol."""
    try:
        if not data_agent:
            raise HTTPException(status_code=503, detail="Data agent not initialized")
        
        # Get latest price
        price_info = data_agent.get_latest_price(ticker.upper())
        
        # Get stock info
        stock_info = data_agent.get_stock_info(ticker.upper())
        
        return {
            'ticker': ticker.upper(),
            'price_info': price_info,
            'stock_info': stock_info,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting ticker info for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search")
async def search_documents(query: str, k: int = 5):
    """Search documents in the RAG store."""
    try:
        if not research_agent:
            raise HTTPException(status_code=503, detail="Research agent not initialized")
        
        # Run research query
        results = await run_research_analysis(query, k)
        
        return {
            'query': query,
            'results': results,
            'count': len(results),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'error': exc.detail,
            'status_code': exc.status_code,
            'timestamp': datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            'error': 'Internal server error',
            'status_code': 500,
            'timestamp': datetime.now().isoformat()
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("Multi-Agent Financial Analyst API is starting up...")
    
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    logger.info("API startup completed")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("Multi-Agent Financial Analyst API is shutting down...")


# Main execution
if __name__ == "__main__":
    # Configure logging
    logger.add(
        "logs/api.log",
        rotation="10 MB",
        retention="7 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}"
    )
    
    # Run the application
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Set to False in production
        log_level="info"
    )
