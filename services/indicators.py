"""
Financial Indicators Module for Multi-Agent Financial Analyst Tool

This module provides functions to compute standard financial indicators
from OHLC price data and create visualization charts.

Author: Multi-Agent Financial Analyst Tool
Version: 1.0.0
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
import seaborn as sns
from typing import Dict, Optional, Tuple
import os
from datetime import datetime
from loguru import logger
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# Set matplotlib style for better-looking charts
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


class IndicatorError(Exception):
    """Custom exception for indicator calculation errors."""
    pass


def compute_indicators(df: pd.DataFrame) -> Dict[str, pd.Series]:
    """
    Compute standard financial indicators from OHLC price data.
    
    Args:
        df (pd.DataFrame): DataFrame with columns ['open', 'high', 'low', 'close', 'volume']
                          and 'date' as index or column
        
    Returns:
        Dict[str, pd.Series]: Dictionary containing calculated indicators
        
    Raises:
        IndicatorError: If input data is invalid or calculations fail
        
    Example:
        >>> df = get_historical_prices('AAPL', '2023-01-01', '2023-12-31')
        >>> indicators = compute_indicators(df)
    """
    try:
        # Validate input DataFrame
        _validate_price_data(df)
        
        logger.info(f"Computing indicators for {len(df)} data points")
        
        # Make a copy to avoid modifying original data
        data = df.copy()
        
        # Ensure date is the index
        if 'date' in data.columns:
            data = data.set_index('date')
        
        # Extract OHLCV data
        close = data['close']
        high = data['high']
        low = data['low']
        volume = data.get('volume', pd.Series(index=close.index))
        
        indicators = {}
        
        # Simple Moving Averages
        indicators['SMA_20'] = _compute_sma(close, 20)
        indicators['SMA_50'] = _compute_sma(close, 50)
        indicators['SMA_200'] = _compute_sma(close, 200)
        
        # Exponential Moving Averages
        indicators['EMA_12'] = _compute_ema(close, 12)
        indicators['EMA_26'] = _compute_ema(close, 26)
        indicators['EMA_50'] = _compute_ema(close, 50)
        
        # RSI (Relative Strength Index)
        indicators['RSI_14'] = _compute_rsi(close, 14)
        
        # MACD (Moving Average Convergence Divergence)
        macd_line, macd_signal, macd_histogram = _compute_macd(close)
        indicators['MACD'] = macd_line
        indicators['MACD_Signal'] = macd_signal
        indicators['MACD_Histogram'] = macd_histogram
        
        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = _compute_bollinger_bands(close, 20, 2)
        indicators['BB_Upper'] = bb_upper
        indicators['BB_Middle'] = bb_middle
        indicators['BB_Lower'] = bb_lower
        
        # Additional useful indicators
        indicators['Stochastic_K'] = _compute_stochastic(high, low, close, 14)
        indicators['Stochastic_D'] = _compute_sma(indicators['Stochastic_K'], 3)
        
        # Volume indicators
        indicators['Volume_SMA'] = _compute_sma(volume, 20)
        indicators['OBV'] = _compute_obv(close, volume)
        
        # Volatility indicators
        indicators['ATR'] = _compute_atr(high, low, close, 14)
        indicators['Volatility'] = _compute_volatility(close, 20)
        
        # Price-based indicators
        indicators['Williams_R'] = _compute_williams_r(high, low, close, 14)
        indicators['CCI'] = _compute_cci(high, low, close, 20)
        
        logger.info(f"Successfully computed {len(indicators)} indicators")
        
        return indicators
        
    except Exception as e:
        error_msg = f"Error computing indicators: {str(e)}"
        logger.error(error_msg)
        raise IndicatorError(error_msg) from e


def plot_price_with_indicators(
    df: pd.DataFrame, 
    indicators: Dict[str, pd.Series],
    ticker: str = "STOCK",
    save_path: Optional[str] = None
) -> str:
    """
    Create a comprehensive chart showing price data with key indicators.
    
    Args:
        df (pd.DataFrame): Price data with OHLCV columns
        indicators (Dict[str, pd.Series]): Calculated indicators
        ticker (str): Stock ticker symbol for chart title
        save_path (Optional[str]): Custom save path (optional)
        
    Returns:
        str: File path of the saved chart
        
    Example:
        >>> df = get_historical_prices('AAPL', '2023-01-01', '2023-12-31')
        >>> indicators = compute_indicators(df)
        >>> chart_path = plot_price_with_indicators(df, indicators, 'AAPL')
    """
    try:
        # Create charts directory if it doesn't exist
        os.makedirs("charts", exist_ok=True)
        
        # Generate filename if not provided
        if save_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = f"charts/{ticker}_{timestamp}_indicators.png"
        
        # Prepare data
        data = df.copy()
        if 'date' in data.columns:
            data = data.set_index('date')
        
        close = data['close']
        volume = data.get('volume', pd.Series(index=close.index))
        
        # Create figure with subplots
        fig = Figure(figsize=(16, 12))
        
        # Main price chart with moving averages and Bollinger Bands
        ax1 = fig.add_subplot(4, 1, 1)
        ax1.plot(close.index, close.values, label='Close Price', linewidth=2, color='#1f77b4')
        
        # Add moving averages if available
        if 'SMA_20' in indicators:
            ax1.plot(close.index, indicators['SMA_20'], label='SMA 20', alpha=0.7, color='orange')
        if 'SMA_50' in indicators:
            ax1.plot(close.index, indicators['SMA_50'], label='SMA 50', alpha=0.7, color='red')
        
        # Add Bollinger Bands if available
        if all(key in indicators for key in ['BB_Upper', 'BB_Middle', 'BB_Lower']):
            ax1.fill_between(
                close.index, 
                indicators['BB_Lower'], 
                indicators['BB_Upper'], 
                alpha=0.2, 
                color='gray', 
                label='Bollinger Bands'
            )
            ax1.plot(close.index, indicators['BB_Middle'], '--', alpha=0.5, color='gray')
        
        ax1.set_title(f'{ticker} - Price Chart with Moving Averages & Bollinger Bands', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price ($)', fontsize=12)
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)
        
        # RSI Chart
        ax2 = fig.add_subplot(4, 1, 2)
        if 'RSI_14' in indicators:
            ax2.plot(close.index, indicators['RSI_14'], label='RSI (14)', color='purple', linewidth=2)
            ax2.axhline(y=70, color='r', linestyle='--', alpha=0.7, label='Overbought (70)')
            ax2.axhline(y=30, color='g', linestyle='--', alpha=0.7, label='Oversold (30)')
            ax2.axhline(y=50, color='k', linestyle='-', alpha=0.3)
            ax2.fill_between(close.index, 30, 70, alpha=0.1, color='gray')
        
        ax2.set_title('Relative Strength Index (RSI)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('RSI', fontsize=10)
        ax2.set_ylim(0, 100)
        ax2.legend(loc='upper left')
        ax2.grid(True, alpha=0.3)
        
        # MACD Chart
        ax3 = fig.add_subplot(4, 1, 3)
        if all(key in indicators for key in ['MACD', 'MACD_Signal', 'MACD_Histogram']):
            ax3.plot(close.index, indicators['MACD'], label='MACD', color='blue', linewidth=2)
            ax3.plot(close.index, indicators['MACD_Signal'], label='Signal', color='red', linewidth=2)
            ax3.bar(close.index, indicators['MACD_Histogram'], label='Histogram', alpha=0.6, color='gray')
            ax3.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        
        ax3.set_title('MACD (Moving Average Convergence Divergence)', fontsize=12, fontweight='bold')
        ax3.set_ylabel('MACD', fontsize=10)
        ax3.legend(loc='upper left')
        ax3.grid(True, alpha=0.3)
        
        # Volume Chart
        ax4 = fig.add_subplot(4, 1, 4)
        if not volume.empty:
            ax4.bar(close.index, volume.values, alpha=0.6, color='lightblue', label='Volume')
            if 'Volume_SMA' in indicators:
                ax4.plot(close.index, indicators['Volume_SMA'], label='Volume SMA (20)', color='darkblue', linewidth=2)
        
        ax4.set_title('Volume', fontsize=12, fontweight='bold')
        ax4.set_ylabel('Volume', fontsize=10)
        ax4.set_xlabel('Date', fontsize=10)
        ax4.legend(loc='upper left')
        ax4.grid(True, alpha=0.3)
        
        # Format x-axis for all subplots
        for ax in [ax1, ax2, ax3, ax4]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        # Adjust layout and save
        fig.tight_layout(pad=2.0)
        fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close(fig)  # Close figure to free memory
        
        logger.info(f"Chart saved to: {save_path}")
        return save_path
        
    except Exception as e:
        error_msg = f"Error creating chart: {str(e)}"
        logger.error(error_msg)
        raise IndicatorError(error_msg) from e


# Indicator calculation functions
def _compute_sma(series: pd.Series, period: int) -> pd.Series:
    """Compute Simple Moving Average."""
    return series.rolling(window=period).mean()


def _compute_ema(series: pd.Series, period: int) -> pd.Series:
    """Compute Exponential Moving Average."""
    return series.ewm(span=period).mean()


def _compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Compute Relative Strength Index."""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def _compute_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Compute MACD (Moving Average Convergence Divergence)."""
    ema_fast = _compute_ema(series, fast)
    ema_slow = _compute_ema(series, slow)
    macd_line = ema_fast - ema_slow
    macd_signal = _compute_ema(macd_line, signal)
    macd_histogram = macd_line - macd_signal
    return macd_line, macd_signal, macd_histogram


def _compute_bollinger_bands(series: pd.Series, period: int = 20, std_dev: float = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Compute Bollinger Bands."""
    sma = _compute_sma(series, period)
    std = series.rolling(window=period).std()
    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)
    return upper_band, sma, lower_band


def _compute_stochastic(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Compute Stochastic Oscillator %K."""
    lowest_low = low.rolling(window=period).min()
    highest_high = high.rolling(window=period).max()
    k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
    return k_percent


def _compute_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """Compute On-Balance Volume."""
    price_change = close.diff()
    obv = (volume * np.sign(price_change)).cumsum()
    return obv


def _compute_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Compute Average True Range."""
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = true_range.rolling(window=period).mean()
    return atr


def _compute_volatility(series: pd.Series, period: int = 20) -> pd.Series:
    """Compute volatility (standard deviation of returns)."""
    returns = series.pct_change()
    volatility = returns.rolling(window=period).std() * np.sqrt(252)  # Annualized
    return volatility


def _compute_williams_r(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Compute Williams %R."""
    highest_high = high.rolling(window=period).max()
    lowest_low = low.rolling(window=period).min()
    williams_r = -100 * ((highest_high - close) / (highest_high - lowest_low))
    return williams_r


def _compute_cci(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20) -> pd.Series:
    """Compute Commodity Channel Index."""
    typical_price = (high + low + close) / 3
    sma_tp = _compute_sma(typical_price, period)
    mean_deviation = typical_price.rolling(window=period).apply(
        lambda x: np.mean(np.abs(x - x.mean()))
    )
    cci = (typical_price - sma_tp) / (0.015 * mean_deviation)
    return cci


def _validate_price_data(df: pd.DataFrame) -> None:
    """Validate input price data."""
    required_columns = ['open', 'high', 'low', 'close']
    
    if df.empty:
        raise IndicatorError("Input DataFrame is empty")
    
    if not all(col in df.columns for col in required_columns):
        missing_cols = [col for col in required_columns if col not in df.columns]
        raise IndicatorError(f"Missing required columns: {missing_cols}")
    
    # Check for valid numeric data
    for col in required_columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise IndicatorError(f"Column '{col}' must contain numeric data")
    
    # Check for reasonable price values
    if (df[required_columns] <= 0).any().any():
        raise IndicatorError("Price data contains non-positive values")


def get_indicator_summary(indicators: Dict[str, pd.Series]) -> Dict[str, Dict[str, float]]:
    """
    Get summary statistics for computed indicators.
    
    Args:
        indicators (Dict[str, pd.Series]): Calculated indicators
        
    Returns:
        Dict[str, Dict[str, float]]: Summary statistics for each indicator
    """
    summary = {}
    
    for name, series in indicators.items():
        if series is not None and not series.empty:
            summary[name] = {
                'current': float(series.iloc[-1]) if not pd.isna(series.iloc[-1]) else None,
                'mean': float(series.mean()) if not series.empty else None,
                'std': float(series.std()) if not series.empty else None,
                'min': float(series.min()) if not series.empty else None,
                'max': float(series.max()) if not series.empty else None,
                'count': int(series.count())
            }
    
    return summary


# Create charts directory if it doesn't exist
os.makedirs("charts", exist_ok=True)
