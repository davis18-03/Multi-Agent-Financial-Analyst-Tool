"""
Data Agent Module for Multi-Agent Financial Analyst Tool

This module provides a DataAgent class that orchestrates data fetching,
technical indicator calculations, and chart generation for financial analysis.

Author: Multi-Agent Financial Analyst Tool
Version: 1.0.0
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pandas as pd
from functools import lru_cache
from loguru import logger
import traceback

# Add services to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from services.data_fetcher import DataFetcher, DataFetchError
from services.indicators import compute_indicators, plot_price_with_indicators, IndicatorError
from services.rag_store import RAGStore


class DataAgentError(Exception):
    """Custom exception for Data Agent operations."""
    pass


class DataAgent:
    """
    Data Agent for financial data analysis and visualization.
    
    This agent orchestrates the retrieval of stock data, calculation of technical
    indicators, and generation of charts for comprehensive financial analysis.
    """
    
    def __init__(self, 
                 cache_size: int = 64,
                 timeout: int = 15,
                 enable_charts: bool = True):
        """
        Initialize the Data Agent.
        
        Args:
            cache_size (int): Maximum number of cached results
            timeout (int): Request timeout in seconds
            enable_charts (bool): Whether to generate charts
        """
        self.cache_size = cache_size
        self.timeout = timeout
        self.enable_charts = enable_charts
        
        # Initialize components
        self.data_fetcher = DataFetcher(cache_size=cache_size, timeout=timeout)
        self.rag_store = None
        
        self._setup_logging()
        
    def _setup_logging(self) -> None:
        """Setup logging configuration for the data agent."""
        logger.add(
            "logs/data_agent.log",
            rotation="10 MB",
            retention="7 days",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}"
        )
        
    def analyze_ticker(self, 
                      ticker: str, 
                      start_date: str, 
                      end_date: str,
                      include_chart: bool = True,
                      include_rag: bool = False) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of a ticker symbol.
        
        Args:
            ticker (str): Stock ticker symbol (e.g., 'AAPL', 'MSFT')
            start_date (str): Start date in 'YYYY-MM-DD' format
            end_date (str): End date in 'YYYY-MM-DD' format
            include_chart (bool): Whether to generate chart
            include_rag (bool): Whether to include RAG-enhanced analysis
            
        Returns:
            Dict[str, Any]: Comprehensive analysis results
            
        Raises:
            DataAgentError: If analysis fails
            
        Example:
            >>> agent = DataAgent()
            >>> results = agent.analyze_ticker('AAPL', '2023-01-01', '2023-12-31')
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Starting analysis for {ticker} from {start_date} to {end_date}")
            
            # Validate inputs
            self._validate_analysis_inputs(ticker, start_date, end_date)
            
            # Initialize result structure
            analysis_result = {
                'ticker': ticker.upper(),
                'analysis_date': datetime.now().isoformat(),
                'date_range': {
                    'start': start_date,
                    'end': end_date
                },
                'status': 'success',
                'processing_time': None,
                'data': {},
                'indicators': {},
                'summary': {},
                'chart_path': None,
                'errors': []
            }
            
            # Step 1: Fetch price data
            try:
                logger.info(f"Fetching price data for {ticker}")
                price_data = self._fetch_price_data(ticker, start_date, end_date)
                analysis_result['data'] = price_data
                
                if price_data['status'] != 'success':
                    analysis_result['errors'].append(price_data.get('error', 'Unknown data fetch error'))
                    
            except Exception as e:
                error_msg = f"Failed to fetch price data: {str(e)}"
                logger.error(error_msg)
                analysis_result['errors'].append(error_msg)
                analysis_result['data'] = {'status': 'error', 'error': error_msg}
            
            # Step 2: Calculate technical indicators
            try:
                if analysis_result['data'].get('status') == 'success':
                    logger.info(f"Calculating indicators for {ticker}")
                    indicators_data = self._calculate_indicators(analysis_result['data']['dataframe'])
                    analysis_result['indicators'] = indicators_data
                    
                    if indicators_data['status'] != 'success':
                        analysis_result['errors'].append(indicators_data.get('error', 'Unknown indicator error'))
                        
            except Exception as e:
                error_msg = f"Failed to calculate indicators: {str(e)}"
                logger.error(error_msg)
                analysis_result['errors'].append(error_msg)
                analysis_result['indicators'] = {'status': 'error', 'error': error_msg}
            
            # Step 3: Generate chart
            if include_chart and self.enable_charts:
                try:
                    if (analysis_result['data'].get('status') == 'success' and 
                        analysis_result['indicators'].get('status') == 'success'):
                        
                        logger.info(f"Generating chart for {ticker}")
                        chart_path = self._generate_chart(
                            analysis_result['data']['dataframe'],
                            analysis_result['indicators']['indicators'],
                            ticker
                        )
                        analysis_result['chart_path'] = chart_path
                        
                except Exception as e:
                    error_msg = f"Failed to generate chart: {str(e)}"
                    logger.error(error_msg)
                    analysis_result['errors'].append(error_msg)
            
            # Step 4: Generate summary
            try:
                logger.info(f"Generating analysis summary for {ticker}")
                summary = self._generate_analysis_summary(
                    analysis_result['data'],
                    analysis_result['indicators']
                )
                analysis_result['summary'] = summary
                
            except Exception as e:
                error_msg = f"Failed to generate summary: {str(e)}"
                logger.error(error_msg)
                analysis_result['errors'].append(error_msg)
                analysis_result['summary'] = {'status': 'error', 'error': error_msg}
            
            # Step 5: RAG-enhanced analysis (optional)
            if include_rag:
                try:
                    rag_analysis = self._get_rag_analysis(ticker, analysis_result['summary'])
                    analysis_result['rag_insights'] = rag_analysis
                    
                except Exception as e:
                    error_msg = f"Failed to get RAG analysis: {str(e)}"
                    logger.error(error_msg)
                    analysis_result['errors'].append(error_msg)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            analysis_result['processing_time'] = processing_time
            
            # Set overall status
            if analysis_result['errors']:
                analysis_result['status'] = 'partial_success'
                logger.warning(f"Analysis completed with {len(analysis_result['errors'])} errors")
            else:
                analysis_result['status'] = 'success'
                logger.info(f"Analysis completed successfully in {processing_time:.2f}s")
            
            return analysis_result
            
        except Exception as e:
            error_msg = f"Critical error in analysis: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            raise DataAgentError(error_msg) from e
    
    @lru_cache(maxsize=64)
    def get_latest_price(self, ticker: str) -> Dict[str, Any]:
        """
        Get the latest price for a ticker with caching.
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            Dict[str, Any]: Latest price information
        """
        try:
            logger.info(f"Getting latest price for {ticker}")
            
            price = self.data_fetcher.get_latest_price(ticker)
            
            result = {
                'ticker': ticker.upper(),
                'price': price,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
            logger.info(f"Latest price for {ticker}: ${price:.2f}")
            return result
            
        except Exception as e:
            error_msg = f"Failed to get latest price for {ticker}: {str(e)}"
            logger.error(error_msg)
            return {
                'ticker': ticker.upper(),
                'price': None,
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'error': error_msg
            }
    
    def get_stock_info(self, ticker: str) -> Dict[str, Any]:
        """
        Get comprehensive stock information.
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            Dict[str, Any]: Stock information
        """
        try:
            logger.info(f"Getting stock info for {ticker}")
            
            info = self.data_fetcher.get_stock_info(ticker)
            
            result = {
                'ticker': ticker.upper(),
                'info': info,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
            return result
            
        except Exception as e:
            error_msg = f"Failed to get stock info for {ticker}: {str(e)}"
            logger.error(error_msg)
            return {
                'ticker': ticker.upper(),
                'info': None,
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'error': error_msg
            }
    
    def _fetch_price_data(self, ticker: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Fetch and validate price data."""
        try:
            # Fetch historical data
            df = self.data_fetcher.get_historical_prices(ticker, start_date, end_date)
            
            if df.empty:
                return {
                    'status': 'error',
                    'error': f'No data available for {ticker} in the specified date range',
                    'dataframe': None
                }
            
            # Get latest price for context
            latest_price = self.data_fetcher.get_latest_price(ticker)
            
            # Calculate basic statistics
            price_stats = {
                'data_points': len(df),
                'date_range_days': (df['date'].max() - df['date'].min()).days,
                'price_range': {
                    'min': float(df['close'].min()),
                    'max': float(df['close'].max()),
                    'current': float(df['close'].iloc[-1]),
                    'latest_market': latest_price
                },
                'volume_stats': {
                    'avg_volume': float(df['volume'].mean()),
                    'max_volume': float(df['volume'].max()),
                    'min_volume': float(df['volume'].min())
                },
                'returns': {
                    'total_return': float((df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100),
                    'daily_volatility': float(df['Daily_Return'].std() * 100)
                }
            }
            
            return {
                'status': 'success',
                'dataframe': df,
                'statistics': price_stats
            }
            
        except DataFetchError as e:
            return {
                'status': 'error',
                'error': str(e),
                'dataframe': None
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': f'Unexpected error fetching data: {str(e)}',
                'dataframe': None
            }
    
    def _calculate_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate technical indicators."""
        try:
            # Compute all indicators
            indicators = compute_indicators(df)
            
            # Get indicator summary
            from services.indicators import get_indicator_summary
            summary = get_indicator_summary(indicators)
            
            # Extract key signals
            signals = self._extract_trading_signals(indicators)
            
            return {
                'status': 'success',
                'indicators': indicators,
                'summary': summary,
                'signals': signals
            }
            
        except IndicatorError as e:
            return {
                'status': 'error',
                'error': str(e),
                'indicators': None
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': f'Unexpected error calculating indicators: {str(e)}',
                'indicators': None
            }
    
    def _generate_chart(self, df: pd.DataFrame, indicators: Dict, ticker: str) -> str:
        """Generate chart with indicators."""
        try:
            chart_path = plot_price_with_indicators(df, indicators, ticker)
            logger.info(f"Chart generated: {chart_path}")
            return chart_path
            
        except Exception as e:
            logger.error(f"Chart generation failed: {str(e)}")
            raise
    
    def _generate_analysis_summary(self, data_result: Dict, indicators_result: Dict) -> Dict[str, Any]:
        """Generate comprehensive analysis summary."""
        try:
            summary = {
                'timestamp': datetime.now().isoformat(),
                'data_quality': 'good' if data_result.get('status') == 'success' else 'poor',
                'indicators_available': indicators_result.get('status') == 'success',
                'key_metrics': {},
                'trend_analysis': {},
                'volatility_assessment': {},
                'trading_signals': {}
            }
            
            # Extract key metrics if data is available
            if data_result.get('status') == 'success':
                stats = data_result.get('statistics', {})
                price_range = stats.get('price_range', {})
                returns = stats.get('returns', {})
                
                summary['key_metrics'] = {
                    'current_price': price_range.get('current'),
                    'price_change_pct': returns.get('total_return'),
                    'volatility': returns.get('daily_volatility'),
                    'data_points': stats.get('data_points'),
                    'trading_days': stats.get('date_range_days')
                }
                
                # Trend analysis
                current_price = price_range.get('current', 0)
                min_price = price_range.get('min', 0)
                max_price = price_range.get('max', 0)
                
                if current_price > (min_price + max_price) / 2:
                    trend = 'bullish'
                elif current_price < (min_price + max_price) / 2:
                    trend = 'bearish'
                else:
                    trend = 'neutral'
                
                summary['trend_analysis'] = {
                    'overall_trend': trend,
                    'price_position': f"{((current_price - min_price) / (max_price - min_price) * 100):.1f}% from low",
                    'range_position': f"{((current_price - min_price) / (max_price - min_price) * 100):.1f}% of range"
                }
            
            # Extract trading signals if indicators are available
            if indicators_result.get('status') == 'success':
                signals = indicators_result.get('signals', {})
                summary['trading_signals'] = signals
                
                # Volatility assessment
                summary['volatility_assessment'] = {
                    'level': self._assess_volatility_level(signals.get('volatility', 0)),
                    'trend': signals.get('volatility_trend', 'unknown')
                }
            
            return summary
            
        except Exception as e:
            logger.error(f"Summary generation failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _extract_trading_signals(self, indicators: Dict) -> Dict[str, Any]:
        """Extract key trading signals from indicators."""
        try:
            signals = {}
            
            # RSI signals
            if 'RSI_14' in indicators:
                rsi = indicators['RSI_14'].iloc[-1] if not indicators['RSI_14'].empty else None
                if rsi is not None:
                    if rsi > 70:
                        signals['rsi_signal'] = 'overbought'
                    elif rsi < 30:
                        signals['rsi_signal'] = 'oversold'
                    else:
                        signals['rsi_signal'] = 'neutral'
                    signals['rsi_value'] = float(rsi)
            
            # MACD signals
            if all(key in indicators for key in ['MACD', 'MACD_Signal']):
                macd = indicators['MACD'].iloc[-1] if not indicators['MACD'].empty else None
                macd_signal = indicators['MACD_Signal'].iloc[-1] if not indicators['MACD_Signal'].empty else None
                
                if macd is not None and macd_signal is not None:
                    if macd > macd_signal:
                        signals['macd_signal'] = 'bullish'
                    else:
                        signals['macd_signal'] = 'bearish'
                    signals['macd_value'] = float(macd - macd_signal)
            
            # Moving average signals
            if all(key in indicators for key in ['SMA_20', 'SMA_50']):
                sma_20 = indicators['SMA_20'].iloc[-1] if not indicators['SMA_20'].empty else None
                sma_50 = indicators['SMA_50'].iloc[-1] if not indicators['SMA_50'].empty else None
                
                if sma_20 is not None and sma_50 is not None:
                    if sma_20 > sma_50:
                        signals['ma_signal'] = 'bullish'
                    else:
                        signals['ma_signal'] = 'bearish'
            
            # Bollinger Bands signals
            if all(key in indicators for key in ['BB_Upper', 'BB_Lower']):
                bb_upper = indicators['BB_Upper'].iloc[-1] if not indicators['BB_Upper'].empty else None
                bb_lower = indicators['BB_Lower'].iloc[-1] if not indicators['BB_Lower'].empty else None
                
                # This would need current price to determine position
                signals['bb_available'] = bb_upper is not None and bb_lower is not None
            
            # Volatility
            if 'Volatility' in indicators:
                volatility = indicators['Volatility'].iloc[-1] if not indicators['Volatility'].empty else None
                if volatility is not None:
                    signals['volatility'] = float(volatility)
                    signals['volatility_trend'] = self._assess_volatility_trend(indicators['Volatility'])
            
            return signals
            
        except Exception as e:
            logger.error(f"Signal extraction failed: {str(e)}")
            return {}
    
    def _assess_volatility_level(self, volatility: float) -> str:
        """Assess volatility level."""
        if volatility < 0.15:
            return 'low'
        elif volatility < 0.30:
            return 'medium'
        else:
            return 'high'
    
    def _assess_volatility_trend(self, volatility_series: pd.Series) -> str:
        """Assess volatility trend."""
        if len(volatility_series) < 5:
            return 'insufficient_data'
        
        recent = volatility_series.tail(5).mean()
        previous = volatility_series.tail(10).head(5).mean()
        
        if recent > previous * 1.1:
            return 'increasing'
        elif recent < previous * 0.9:
            return 'decreasing'
        else:
            return 'stable'
    
    def _get_rag_analysis(self, ticker: str, summary: Dict) -> Dict[str, Any]:
        """Get RAG-enhanced analysis (placeholder for future implementation)."""
        try:
            if not self.rag_store:
                self.rag_store = RAGStore()
                self.rag_store.initialize_vector_store()
            
            # This would query relevant financial documents
            query = f"Analysis of {ticker} stock performance and market trends"
            # docs = self.rag_store.retrieve_docs(query, k=3)
            
            return {
                'status': 'placeholder',
                'message': 'RAG analysis not yet implemented',
                'enhanced_insights': []
            }
            
        except Exception as e:
            logger.error(f"RAG analysis failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _validate_analysis_inputs(self, ticker: str, start_date: str, end_date: str) -> None:
        """Validate analysis inputs."""
        if not ticker or not isinstance(ticker, str):
            raise ValueError("Ticker must be a non-empty string")
        
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            if start_dt >= end_dt:
                raise ValueError("Start date must be before end date")
            
            # Check if date range is reasonable (not more than 10 years)
            if (end_dt - start_dt).days > 365 * 10:
                raise ValueError("Date range cannot exceed 10 years")
                
        except ValueError as e:
            if "time data" in str(e):
                raise ValueError("Dates must be in 'YYYY-MM-DD' format") from e
            raise


# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)
