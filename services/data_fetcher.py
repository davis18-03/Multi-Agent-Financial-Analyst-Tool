"""
Data Fetcher Module for Multi-Agent Financial Analyst Tool

This module provides functions to fetch stock data using the yfinance API.
Includes caching, error handling, and comprehensive logging for reliable
data retrieval operations.

Author: Multi-Agent Financial Analyst Tool
Version: 1.0.0
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Optional, Union
import logging
from loguru import logger
import time


class DataFetchError(Exception):
    """Custom exception for data fetching errors."""
    pass


class DataFetcher:
    """
    A class to handle stock data fetching with caching and error handling.
    
    This class provides methods to fetch historical and current stock prices
    using the yfinance API with built-in caching, error handling, and logging.
    """
    
    def __init__(self, cache_size: int = 128, timeout: int = 10):
        """
        Initialize the DataFetcher.
        
        Args:
            cache_size (int): Maximum number of cached results (default: 128)
            timeout (int): Request timeout in seconds (default: 10)
        """
        self.cache_size = cache_size
        self.timeout = timeout
        self._setup_logging()
        
    def _setup_logging(self) -> None:
        """Setup logging configuration for the data fetcher."""
        logger.add(
            "logs/data_fetcher.log",
            rotation="10 MB",
            retention="7 days",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}"
        )
        
    @lru_cache(maxsize=128)
    def get_historical_prices(
        self, 
        ticker: str, 
        start: str, 
        end: str,
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Fetch historical stock prices for a given ticker and date range.
        
        Args:
            ticker (str): Stock ticker symbol (e.g., 'AAPL', 'MSFT')
            start (str): Start date in 'YYYY-MM-DD' format
            end (str): End date in 'YYYY-MM-DD' format
            interval (str): Data interval ('1d', '1h', '5m', etc.)
            
        Returns:
            pd.DataFrame: Clean DataFrame with OHLCV data and additional columns
            
        Raises:
            DataFetchError: If data fetching fails
            ValueError: If input parameters are invalid
            
        Example:
            >>> fetcher = DataFetcher()
            >>> df = fetcher.get_historical_prices('AAPL', '2023-01-01', '2023-12-31')
        """
        start_time = time.time()
        
        try:
            # Validate inputs
            self._validate_ticker(ticker)
            self._validate_date_range(start, end)
            
            logger.info(f"Fetching historical data for {ticker} from {start} to {end}")
            
            # Create ticker object
            stock = yf.Ticker(ticker.upper())
            
            # Fetch historical data
            hist_data = stock.history(
                start=start,
                end=end,
                interval=interval,
                timeout=self.timeout
            )
            
            if hist_data.empty:
                raise DataFetchError(f"No data found for ticker {ticker} in the specified date range")
            
            # Clean and enhance the data
            cleaned_data = self._clean_historical_data(hist_data, ticker)
            
            fetch_time = time.time() - start_time
            logger.info(f"Successfully fetched {len(cleaned_data)} records for {ticker} in {fetch_time:.2f}s")
            
            return cleaned_data
            
        except yf.exceptions.YFinanceException as e:
            error_msg = f"YFinance error fetching data for {ticker}: {str(e)}"
            logger.error(error_msg)
            raise DataFetchError(error_msg) from e
            
        except Exception as e:
            error_msg = f"Unexpected error fetching historical data for {ticker}: {str(e)}"
            logger.error(error_msg)
            raise DataFetchError(error_msg) from e
    
    @lru_cache(maxsize=64)
    def get_latest_price(self, ticker: str) -> float:
        """
        Fetch the latest stock price for a given ticker.
        
        Args:
            ticker (str): Stock ticker symbol (e.g., 'AAPL', 'MSFT')
            
        Returns:
            float: Latest closing price
            
        Raises:
            DataFetchError: If data fetching fails
            ValueError: If ticker is invalid
            
        Example:
            >>> fetcher = DataFetcher()
            >>> price = fetcher.get_latest_price('AAPL')
        """
        start_time = time.time()
        
        try:
            # Validate ticker
            self._validate_ticker(ticker)
            
            logger.info(f"Fetching latest price for {ticker}")
            
            # Create ticker object
            stock = yf.Ticker(ticker.upper())
            
            # Get latest info
            info = stock.info
            
            if 'regularMarketPrice' in info and info['regularMarketPrice'] is not None:
                price = float(info['regularMarketPrice'])
            elif 'currentPrice' in info and info['currentPrice'] is not None:
                price = float(info['currentPrice'])
            elif 'previousClose' in info and info['previousClose'] is not None:
                price = float(info['previousClose'])
            else:
                # Fallback: get last close from recent history
                hist_data = stock.history(period="1d", timeout=self.timeout)
                if hist_data.empty:
                    raise DataFetchError(f"No current price data available for {ticker}")
                price = float(hist_data['Close'].iloc[-1])
            
            fetch_time = time.time() - start_time
            logger.info(f"Latest price for {ticker}: ${price:.2f} (fetched in {fetch_time:.2f}s)")
            
            return price
            
        except yf.exceptions.YFinanceException as e:
            error_msg = f"YFinance error fetching latest price for {ticker}: {str(e)}"
            logger.error(error_msg)
            raise DataFetchError(error_msg) from e
            
        except Exception as e:
            error_msg = f"Unexpected error fetching latest price for {ticker}: {str(e)}"
            logger.error(error_msg)
            raise DataFetchError(error_msg) from e
    
    def get_stock_info(self, ticker: str) -> dict:
        """
        Fetch comprehensive stock information.
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            dict: Stock information including name, sector, market cap, etc.
        """
        try:
            self._validate_ticker(ticker)
            
            logger.info(f"Fetching stock info for {ticker}")
            
            stock = yf.Ticker(ticker.upper())
            info = stock.info
            
            # Extract key information
            relevant_info = {
                'symbol': ticker.upper(),
                'name': info.get('longName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'dividend_yield': info.get('dividendYield', 'N/A'),
                '52_week_high': info.get('fiftyTwoWeekHigh', 'N/A'),
                '52_week_low': info.get('fiftyTwoWeekLow', 'N/A'),
                'avg_volume': info.get('averageVolume', 'N/A'),
                'currency': info.get('currency', 'USD')
            }
            
            logger.info(f"Successfully fetched info for {ticker}")
            return relevant_info
            
        except Exception as e:
            error_msg = f"Error fetching stock info for {ticker}: {str(e)}"
            logger.error(error_msg)
            raise DataFetchError(error_msg) from e
    
    def _validate_ticker(self, ticker: str) -> None:
        """Validate ticker symbol format."""
        if not ticker or not isinstance(ticker, str):
            raise ValueError("Ticker must be a non-empty string")
        
        if not ticker.replace('.', '').replace('-', '').isalnum():
            raise ValueError(f"Invalid ticker format: {ticker}")
    
    def _validate_date_range(self, start: str, end: str) -> None:
        """Validate date range format and logic."""
        try:
            start_date = datetime.strptime(start, '%Y-%m-%d')
            end_date = datetime.strptime(end, '%Y-%m-%d')
            
            if start_date >= end_date:
                raise ValueError("Start date must be before end date")
            
            # Check if dates are too far in the past or future
            today = datetime.now()
            if start_date > today:
                raise ValueError("Start date cannot be in the future")
            
            # Warn if date range is very large
            if (end_date - start_date).days > 365 * 5:
                logger.warning(f"Large date range requested: {(end_date - start_date).days} days")
                
        except ValueError as e:
            if "time data" in str(e):
                raise ValueError("Dates must be in 'YYYY-MM-DD' format") from e
            raise
    
    def _clean_historical_data(self, data: pd.DataFrame, ticker: str) -> pd.DataFrame:
        """
        Clean and enhance historical data DataFrame.
        
        Args:
            data (pd.DataFrame): Raw historical data from yfinance
            ticker (str): Stock ticker symbol
            
        Returns:
            pd.DataFrame: Cleaned and enhanced DataFrame
        """
        try:
            # Create a copy to avoid modifying original
            cleaned_data = data.copy()
            
            # Remove any rows with all NaN values
            cleaned_data = cleaned_data.dropna(how='all')
            
            # Forward fill missing values (but not volume)
            numeric_cols = ['Open', 'High', 'Low', 'Close']
            for col in numeric_cols:
                if col in cleaned_data.columns:
                    cleaned_data[col] = cleaned_data[col].fillna(method='ffill')
            
            # Add additional calculated columns
            cleaned_data['Ticker'] = ticker.upper()
            cleaned_data['Daily_Return'] = cleaned_data['Close'].pct_change()
            cleaned_data['Price_Change'] = cleaned_data['Close'].diff()
            cleaned_data['Price_Change_Pct'] = cleaned_data['Price_Change'] / cleaned_data['Close'].shift(1) * 100
            
            # Add moving averages
            cleaned_data['SMA_20'] = cleaned_data['Close'].rolling(window=20).mean()
            cleaned_data['SMA_50'] = cleaned_data['Close'].rolling(window=50).mean()
            
            # Add volatility measure
            cleaned_data['Volatility'] = cleaned_data['Daily_Return'].rolling(window=20).std() * np.sqrt(252)
            
            # Reset index to make Date a column
            cleaned_data = cleaned_data.reset_index()
            
            # Rename columns for consistency
            cleaned_data = cleaned_data.rename(columns={
                'Date': 'date',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            # Ensure proper data types
            cleaned_data['date'] = pd.to_datetime(cleaned_data['date'])
            
            # Round numeric columns
            numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'Daily_Return', 
                          'Price_Change', 'Price_Change_Pct', 'SMA_20', 'SMA_50', 'Volatility']
            for col in numeric_cols:
                if col in cleaned_data.columns:
                    cleaned_data[col] = cleaned_data[col].round(4)
            
            logger.info(f"Cleaned data for {ticker}: {len(cleaned_data)} rows, {len(cleaned_data.columns)} columns")
            
            return cleaned_data
            
        except Exception as e:
            logger.error(f"Error cleaning data for {ticker}: {str(e)}")
            # Return original data if cleaning fails
            return data.reset_index()


# Convenience functions for direct usage
@lru_cache(maxsize=128)
def get_historical_prices(ticker: str, start: str, end: str, interval: str = "1d") -> pd.DataFrame:
    """
    Convenience function to fetch historical stock prices.
    
    Args:
        ticker (str): Stock ticker symbol
        start (str): Start date in 'YYYY-MM-DD' format
        end (str): End date in 'YYYY-MM-DD' format
        interval (str): Data interval ('1d', '1h', '5m', etc.)
        
    Returns:
        pd.DataFrame: Historical stock data
        
    Example:
        >>> df = get_historical_prices('AAPL', '2023-01-01', '2023-12-31')
    """
    fetcher = DataFetcher()
    return fetcher.get_historical_prices(ticker, start, end, interval)


@lru_cache(maxsize=64)
def get_latest_price(ticker: str) -> float:
    """
    Convenience function to fetch the latest stock price.
    
    Args:
        ticker (str): Stock ticker symbol
        
    Returns:
        float: Latest stock price
        
    Example:
        >>> price = get_latest_price('AAPL')
    """
    fetcher = DataFetcher()
    return fetcher.get_latest_price(ticker)


def clear_cache() -> None:
    """Clear all cached data."""
    get_historical_prices.cache_clear()
    get_latest_price.cache_clear()
    logger.info("Data fetcher cache cleared")


# Create logs directory if it doesn't exist
import os
os.makedirs("logs", exist_ok=True)
