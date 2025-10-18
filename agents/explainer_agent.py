"""
Explainer Agent Module for Multi-Agent Financial Analyst Tool

This module provides an ExplainerAgent class that transforms technical financial
analysis into user-friendly, visually appealing explanations with HTML/markdown
formatting, emojis, citations, and chart embeddings for Streamlit.

Author: Multi-Agent Financial Analyst Tool
Version: 1.0.0
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from functools import lru_cache
from loguru import logger
import traceback
import base64
import re

# Add services to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from services.data_fetcher import DataFetcher
from services.indicators import compute_indicators


class ExplainerAgentError(Exception):
    """Custom exception for Explainer Agent operations."""
    pass


class ExplainerAgent:
    """
    Explainer Agent for user-friendly financial analysis explanations.
    
    This agent transforms technical analysis results into plain-language,
    visually appealing explanations with HTML/markdown formatting for Streamlit.
    """
    
    def __init__(self, 
                 include_emojis: bool = True,
                 output_format: str = "html",
                 include_citations: bool = True,
                 chart_quality: str = "high"):
        """
        Initialize the Explainer Agent.
        
        Args:
            include_emojis (bool): Whether to include emojis in explanations
            output_format (str): Output format ('html', 'markdown')
            include_citations (bool): Whether to include source citations
            chart_quality (str): Chart quality ('high', 'medium', 'low')
        """
        self.include_emojis = include_emojis
        self.output_format = output_format.lower()
        self.include_citations = include_citations
        self.chart_quality = chart_quality
        
        # Initialize components
        self.data_fetcher = DataFetcher()
        
        self._setup_logging()
        self._initialize_emoji_maps()
        
    def _setup_logging(self) -> None:
        """Setup logging configuration for the explainer agent."""
        logger.add(
            "logs/explainer_agent.log",
            rotation="10 MB",
            retention="7 days",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}"
        )
        
    def _initialize_emoji_maps(self) -> None:
        """Initialize emoji mappings for different analysis aspects."""
        self.emoji_maps = {
            'trend': {
                'bullish': '📈',
                'bearish': '📉',
                'neutral': '➡️',
                'volatile': '📊'
            },
            'sentiment': {
                'positive': '😊',
                'negative': '😟',
                'neutral': '😐',
                'excellent': '🌟',
                'good': '👍',
                'warning': '⚠️',
                'danger': '🚨'
            },
            'indicators': {
                'rsi': '⚡',
                'macd': '📊',
                'bollinger': '🎯',
                'sma': '📏',
                'volume': '📦',
                'volatility': '🌊'
            },
            'actions': {
                'buy': '🟢',
                'sell': '🔴',
                'hold': '🟡',
                'watch': '👀',
                'research': '🔍',
                'analyze': '📋'
            },
            'general': {
                'chart': '📊',
                'data': '📈',
                'analysis': '🔬',
                'insight': '💡',
                'recommendation': '💼',
                'risk': '⚠️',
                'opportunity': '🎯',
                'summary': '📝',
                'source': '📄',
                'time': '⏰',
                'price': '💰',
                'percentage': '📊'
            }
        }
    
    def explain_analysis(self, 
                        analysis_result: Dict[str, Any],
                        research_results: Optional[List[Dict[str, Any]]] = None,
                        style: str = "professional") -> str:
        """
        Transform technical analysis into user-friendly explanation.
        
        Args:
            analysis_result (Dict[str, Any]): Analysis result from DataAgent
            research_results (Optional[List[Dict]]): Research results from ResearchAgent
            style (str): Explanation style ('professional', 'casual', 'detailed')
            
        Returns:
            str: Formatted explanation in HTML or Markdown
            
        Raises:
            ExplainerAgentError: If explanation fails
            
        Example:
            >>> explainer = ExplainerAgent()
            >>> explanation = explainer.explain_analysis(analysis_result)
        """
        try:
            logger.info(f"Creating explanation for {analysis_result.get('ticker', 'UNKNOWN')} analysis")
            
            # Validate inputs
            if not analysis_result or not isinstance(analysis_result, dict):
                raise ValueError("Analysis result must be a non-empty dictionary")
            
            # Generate explanation sections
            sections = []
            
            # Header section
            sections.append(self._create_header(analysis_result))
            
            # Executive summary
            sections.append(self._create_executive_summary(analysis_result))
            
            # Price analysis
            if analysis_result.get('data', {}).get('status') == 'success':
                sections.append(self._create_price_analysis(analysis_result['data']))
            
            # Technical indicators
            if analysis_result.get('indicators', {}).get('status') == 'success':
                sections.append(self._create_indicators_explanation(analysis_result['indicators']))
            
            # Trading signals
            if analysis_result.get('summary', {}).get('trading_signals'):
                sections.append(self._create_signals_explanation(analysis_result['summary']))
            
            # Chart section
            if analysis_result.get('chart_path'):
                sections.append(self._create_chart_section(analysis_result['chart_path']))
            
            # Research insights (if available)
            if research_results:
                sections.append(self._create_research_section(research_results))
            
            # Risk assessment
            sections.append(self._create_risk_assessment(analysis_result))
            
            # Recommendations
            sections.append(self._create_recommendations(analysis_result))
            
            # Footer with citations and metadata
            sections.append(self._create_footer(analysis_result))
            
            # Combine all sections
            explanation = self._combine_sections(sections, style)
            
            logger.info("Explanation created successfully")
            return explanation
            
        except Exception as e:
            error_msg = f"Failed to create explanation: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            raise ExplainerAgentError(error_msg) from e
    
    def _create_header(self, analysis_result: Dict[str, Any]) -> str:
        """Create header section with ticker and basic info."""
        ticker = analysis_result.get('ticker', 'UNKNOWN')
        status = analysis_result.get('status', 'unknown')
        analysis_date = analysis_result.get('analysis_date', datetime.now().isoformat())
        
        # Format analysis date
        try:
            date_obj = datetime.fromisoformat(analysis_date.replace('Z', '+00:00'))
            formatted_date = date_obj.strftime("%B %d, %Y at %I:%M %p")
        except:
            formatted_date = analysis_date
        
        # Get emojis
        chart_emoji = self._get_emoji('general', 'chart')
        time_emoji = self._get_emoji('general', 'time')
        
        if self.output_format == "html":
            return f"""
            <div class="analysis-header" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <h1 style="margin: 0; font-size: 2.5em; text-align: center;">
                    {chart_emoji} {ticker} Financial Analysis {chart_emoji}
                </h1>
                <p style="text-align: center; margin: 10px 0 0 0; font-size: 1.2em; opacity: 0.9;">
                    {time_emoji} Analysis completed on {formatted_date}
                </p>
                <div style="text-align: center; margin-top: 10px;">
                    <span class="status-badge" style="background: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 20px; font-size: 0.9em;">
                        Status: {status.replace('_', ' ').title()}
                    </span>
                </div>
            </div>
            """
        else:  # markdown
            return f"""
# {chart_emoji} {ticker} Financial Analysis {chart_emoji}

**{time_emoji} Analysis Date:** {formatted_date}  
**Status:** {status.replace('_', ' ').title()}

---
"""
    
    def _create_executive_summary(self, analysis_result: Dict[str, Any]) -> str:
        """Create executive summary section."""
        summary_data = analysis_result.get('summary', {})
        key_metrics = summary_data.get('key_metrics', {})
        trend_analysis = summary_data.get('trend_analysis', {})
        
        current_price = key_metrics.get('current_price', 0)
        price_change = key_metrics.get('price_change_pct', 0)
        overall_trend = trend_analysis.get('overall_trend', 'neutral')
        
        # Get emojis
        insight_emoji = self._get_emoji('general', 'insight')
        trend_emoji = self._get_emoji('trend', overall_trend)
        price_emoji = self._get_emoji('general', 'price')
        
        # Create trend description
        trend_descriptions = {
            'bullish': 'showing positive momentum',
            'bearish': 'showing negative momentum',
            'neutral': 'showing sideways movement'
        }
        trend_desc = trend_descriptions.get(overall_trend, 'showing mixed signals')
        
        if self.output_format == "html":
            return f"""
            <div class="executive-summary" style="background: #f8f9fa; padding: 20px; border-left: 5px solid #007bff; margin: 20px 0; border-radius: 5px;">
                <h2 style="color: #007bff; margin-top: 0;">{insight_emoji} Executive Summary</h2>
                <div style="display: flex; align-items: center; margin: 15px 0;">
                    <span style="font-size: 2em; margin-right: 15px;">{trend_emoji}</span>
                    <div>
                        <p style="margin: 0; font-size: 1.1em; font-weight: 500;">
                            <strong>{price_emoji} Current Price:</strong> ${current_price:.2f}
                        </p>
                        <p style="margin: 5px 0 0 0; color: {'#28a745' if price_change >= 0 else '#dc3545'};">
                            <strong>Change:</strong> {price_change:+.2f}%
                        </p>
                    </div>
                </div>
                <p style="margin: 15px 0; font-size: 1.1em; line-height: 1.6;">
                    The stock is currently {trend_desc} with a {overall_trend} trend pattern. 
                    {'This suggests potential upside opportunities.' if overall_trend == 'bullish' else 
                     'This suggests caution is warranted.' if overall_trend == 'bearish' else 
                     'This suggests a wait-and-see approach may be appropriate.'}
                </p>
            </div>
            """
        else:  # markdown
            return f"""
## {insight_emoji} Executive Summary

{trend_emoji} **Current Price:** ${current_price:.2f} ({price_change:+.2f}%)

The stock is currently {trend_desc} with a {overall_trend} trend pattern. 
{'This suggests potential upside opportunities.' if overall_trend == 'bullish' else 
 'This suggests caution is warranted.' if overall_trend == 'bearish' else 
 'This suggests a wait-and-see approach may be appropriate.'}

---
"""
    
    def _create_price_analysis(self, data_result: Dict[str, Any]) -> str:
        """Create price analysis section."""
        stats = data_result.get('statistics', {})
        price_range = stats.get('price_range', {})
        volume_stats = stats.get('volume_stats', {})
        returns = stats.get('returns', {})
        
        min_price = price_range.get('min', 0)
        max_price = price_range.get('max', 0)
        current_price = price_range.get('current', 0)
        avg_volume = volume_stats.get('avg_volume', 0)
        volatility = returns.get('daily_volatility', 0)
        
        # Calculate price position
        price_position = ((current_price - min_price) / (max_price - min_price)) * 100 if max_price > min_price else 50
        
        # Get emojis
        data_emoji = self._get_emoji('general', 'data')
        volatility_emoji = self._get_emoji('indicators', 'volatility')
        volume_emoji = self._get_emoji('indicators', 'volume')
        
        if self.output_format == "html":
            return f"""
            <div class="price-analysis" style="margin: 20px 0;">
                <h2 style="color: #28a745;">{data_emoji} Price Analysis</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 15px 0;">
                    <div class="metric-card" style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h4 style="margin: 0 0 10px 0; color: #666;">Price Range</h4>
                        <p style="margin: 0; font-size: 1.2em; font-weight: bold;">
                            ${min_price:.2f} - ${max_price:.2f}
                        </p>
                        <p style="margin: 5px 0 0 0; color: #666; font-size: 0.9em;">
                            Current: {price_position:.1f}% from low
                        </p>
                    </div>
                    <div class="metric-card" style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h4 style="margin: 0 0 10px 0; color: #666;">{volatility_emoji} Volatility</h4>
                        <p style="margin: 0; font-size: 1.2em; font-weight: bold; color: {'#dc3545' if volatility > 20 else '#ffc107' if volatility > 10 else '#28a745'};">
                            {volatility:.2f}%
                        </p>
                        <p style="margin: 5px 0 0 0; color: #666; font-size: 0.9em;">
                            {'High' if volatility > 20 else 'Medium' if volatility > 10 else 'Low'} risk
                        </p>
                    </div>
                    <div class="metric-card" style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h4 style="margin: 0 0 10px 0; color: #666;">{volume_emoji} Volume</h4>
                        <p style="margin: 0; font-size: 1.2em; font-weight: bold;">
                            {avg_volume:,.0f}
                        </p>
                        <p style="margin: 5px 0 0 0; color: #666; font-size: 0.9em;">
                            Average daily
                        </p>
                    </div>
                </div>
            </div>
            """
        else:  # markdown
            return f"""
## {data_emoji} Price Analysis

| Metric | Value |
|--------|-------|
| **Price Range** | ${min_price:.2f} - ${max_price:.2f} |
| **Current Position** | {price_position:.1f}% from low |
| **{volatility_emoji} Volatility** | {volatility:.2f}% ({'High' if volatility > 20 else 'Medium' if volatility > 10 else 'Low'} risk) |
| **{volume_emoji} Average Volume** | {avg_volume:,.0f} |

---
"""
    
    def _create_indicators_explanation(self, indicators_result: Dict[str, Any]) -> str:
        """Create technical indicators explanation section."""
        signals = indicators_result.get('signals', {})
        
        rsi_signal = signals.get('rsi_signal', 'unknown')
        macd_signal = signals.get('macd_signal', 'unknown')
        ma_signal = signals.get('ma_signal', 'unknown')
        volatility = signals.get('volatility', 0)
        
        # Get emojis
        analysis_emoji = self._get_emoji('general', 'analysis')
        rsi_emoji = self._get_emoji('indicators', 'rsi')
        macd_emoji = self._get_emoji('indicators', 'macd')
        sma_emoji = self._get_emoji('indicators', 'sma')
        
        # Create signal descriptions
        signal_descriptions = {
            'rsi_signal': {
                'overbought': 'The stock may be overvalued and could face selling pressure',
                'oversold': 'The stock may be undervalued and could see buying interest',
                'neutral': 'The stock is trading in a normal range'
            },
            'macd_signal': {
                'bullish': 'Momentum is building upward, suggesting potential price increases',
                'bearish': 'Momentum is weakening, suggesting potential price decreases'
            },
            'ma_signal': {
                'bullish': 'Short-term trend is stronger than long-term, indicating upward momentum',
                'bearish': 'Short-term trend is weaker than long-term, indicating downward momentum'
            }
        }
        
        if self.output_format == "html":
            return f"""
            <div class="technical-indicators" style="margin: 20px 0;">
                <h2 style="color: #6f42c1;">{analysis_emoji} Technical Indicators</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; margin: 15px 0;">
                    <div class="indicator-card" style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #007bff;">
                        <h4 style="margin: 0 0 10px 0; color: #007bff;">
                            {rsi_emoji} Relative Strength Index (RSI)
                        </h4>
                        <p style="margin: 0; font-weight: bold; color: {'#dc3545' if rsi_signal == 'overbought' else '#28a745' if rsi_signal == 'oversold' else '#6c757d'};">
                            {rsi_signal.replace('_', ' ').title()}
                        </p>
                        <p style="margin: 5px 0 0 0; color: #666; font-size: 0.9em;">
                            {signal_descriptions['rsi_signal'].get(rsi_signal, 'No clear signal available')}
                        </p>
                    </div>
                    <div class="indicator-card" style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #28a745;">
                        <h4 style="margin: 0 0 10px 0; color: #28a745;">
                            {macd_emoji} MACD (Momentum)
                        </h4>
                        <p style="margin: 0; font-weight: bold; color: {'#28a745' if macd_signal == 'bullish' else '#dc3545' if macd_signal == 'bearish' else '#6c757d'};">
                            {macd_signal.replace('_', ' ').title()}
                        </p>
                        <p style="margin: 5px 0 0 0; color: #666; font-size: 0.9em;">
                            {signal_descriptions['macd_signal'].get(macd_signal, 'No clear signal available')}
                        </p>
                    </div>
                    <div class="indicator-card" style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107;">
                        <h4 style="margin: 0 0 10px 0; color: #e0a800;">
                            {sma_emoji} Moving Averages
                        </h4>
                        <p style="margin: 0; font-weight: bold; color: {'#28a745' if ma_signal == 'bullish' else '#dc3545' if ma_signal == 'bearish' else '#6c757d'};">
                            {ma_signal.replace('_', ' ').title()}
                        </p>
                        <p style="margin: 5px 0 0 0; color: #666; font-size: 0.9em;">
                            {signal_descriptions['ma_signal'].get(ma_signal, 'No clear signal available')}
                        </p>
                    </div>
                </div>
            </div>
            """
        else:  # markdown
            return f"""
## {analysis_emoji} Technical Indicators

### {rsi_emoji} Relative Strength Index (RSI)
- **Signal:** {rsi_signal.replace('_', ' ').title()}
- **Interpretation:** {signal_descriptions['rsi_signal'].get(rsi_signal, 'No clear signal available')}

### {macd_emoji} MACD (Momentum)
- **Signal:** {macd_signal.replace('_', ' ').title()}
- **Interpretation:** {signal_descriptions['macd_signal'].get(macd_signal, 'No clear signal available')}

### {sma_emoji} Moving Averages
- **Signal:** {ma_signal.replace('_', ' ').title()}
- **Interpretation:** {signal_descriptions['ma_signal'].get(ma_signal, 'No clear signal available')}

---
"""
    
    def _create_signals_explanation(self, summary_data: Dict[str, Any]) -> str:
        """Create trading signals explanation section."""
        trading_signals = summary_data.get('trading_signals', {})
        
        # Get emojis
        recommendation_emoji = self._get_emoji('general', 'recommendation')
        watch_emoji = self._get_emoji('actions', 'watch')
        
        # Create signal summary
        bullish_signals = 0
        bearish_signals = 0
        neutral_signals = 0
        
        for signal, value in trading_signals.items():
            if isinstance(value, str):
                if 'bullish' in value.lower():
                    bullish_signals += 1
                elif 'bearish' in value.lower():
                    bearish_signals += 1
                else:
                    neutral_signals += 1
        
        # Determine overall signal
        if bullish_signals > bearish_signals:
            overall_signal = 'bullish'
            signal_emoji = self._get_emoji('actions', 'buy')
            signal_color = '#28a745'
        elif bearish_signals > bullish_signals:
            overall_signal = 'bearish'
            signal_emoji = self._get_emoji('actions', 'sell')
            signal_color = '#dc3545'
        else:
            overall_signal = 'neutral'
            signal_emoji = self._get_emoji('actions', 'hold')
            signal_color = '#ffc107'
        
        if self.output_format == "html":
            return f"""
            <div class="trading-signals" style="margin: 20px 0;">
                <h2 style="color: {signal_color};">{recommendation_emoji} Trading Signals</h2>
                <div style="background: {signal_color}20; padding: 20px; border-radius: 8px; border: 2px solid {signal_color};">
                    <div style="text-align: center;">
                        <span style="font-size: 3em;">{signal_emoji}</span>
                        <h3 style="margin: 10px 0; color: {signal_color};">
                            Overall Signal: {overall_signal.replace('_', ' ').title()}
                        </h3>
                        <p style="margin: 0; color: #666;">
                            Based on {len(trading_signals)} technical indicators
                        </p>
                    </div>
                </div>
                <div style="margin-top: 15px; text-align: center;">
                    <span style="color: #28a745; margin-right: 20px;">{self._get_emoji('actions', 'buy')} Bullish: {bullish_signals}</span>
                    <span style="color: #dc3545; margin-right: 20px;">{self._get_emoji('actions', 'sell')} Bearish: {bearish_signals}</span>
                    <span style="color: #6c757d;">{self._get_emoji('actions', 'hold')} Neutral: {neutral_signals}</span>
                </div>
            </div>
            """
        else:  # markdown
            return f"""
## {recommendation_emoji} Trading Signals

### {signal_emoji} Overall Signal: {overall_signal.replace('_', ' ').title()}

Based on {len(trading_signals)} technical indicators:
- {self._get_emoji('actions', 'buy')} **Bullish signals:** {bullish_signals}
- {self._get_emoji('actions', 'sell')} **Bearish signals:** {bearish_signals}
- {self._get_emoji('actions', 'hold')} **Neutral signals:** {neutral_signals}

---
"""
    
    def _create_chart_section(self, chart_path: str) -> str:
        """Create chart embedding section."""
        chart_emoji = self._get_emoji('general', 'chart')
        
        if self.output_format == "html":
            return f"""
            <div class="chart-section" style="margin: 20px 0;">
                <h2 style="color: #17a2b8;">{chart_emoji} Technical Analysis Chart</h2>
                <div style="text-align: center; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <img src="{chart_path}" alt="Technical Analysis Chart" style="max-width: 100%; height: auto; border-radius: 5px;">
                    <p style="margin: 10px 0 0 0; color: #666; font-size: 0.9em;">
                        Interactive chart showing price movement and technical indicators
                    </p>
                </div>
            </div>
            """
        else:  # markdown
            return f"""
## {chart_emoji} Technical Analysis Chart

![Technical Analysis Chart]({chart_path})

*Interactive chart showing price movement and technical indicators*

---
"""
    
    def _create_research_section(self, research_results: List[Dict[str, Any]]) -> str:
        """Create research insights section."""
        research_emoji = self._get_emoji('actions', 'research')
        source_emoji = self._get_emoji('general', 'source')
        
        if self.output_format == "html":
            html = f"""
            <div class="research-insights" style="margin: 20px 0;">
                <h2 style="color: #fd7e14;">{research_emoji} Research Insights</h2>
                <div style="background: #fff3cd; padding: 20px; border-radius: 8px; border-left: 4px solid #ffc107;">
            """
            
            for i, result in enumerate(research_results[:3], 1):  # Limit to top 3
                title = result.get('title', 'Untitled')
                summary = result.get('summary', 'No summary available')
                source = result.get('source', 'Unknown source')
                relevance = result.get('query_relevance', 'unknown')
                
                relevance_colors = {
                    'high': '#28a745',
                    'medium': '#ffc107',
                    'low': '#6c757d'
                }
                relevance_color = relevance_colors.get(relevance, '#6c757d')
                
                html += f"""
                    <div style="margin-bottom: 20px; padding: 15px; background: white; border-radius: 5px;">
                        <h4 style="margin: 0 0 10px 0; color: #333;">
                            {i}. {title}
                        </h4>
                        <p style="margin: 0 0 10px 0; line-height: 1.6;">
                            {summary}
                        </p>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="color: #666; font-size: 0.9em;">
                                {source_emoji} {source}
                            </span>
                            <span style="background: {relevance_color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em;">
                                {relevance} relevance
                            </span>
                        </div>
                    </div>
                """
            
            html += """
                </div>
            </div>
            """
            return html
        else:  # markdown
            markdown = f"""
## {research_emoji} Research Insights

"""
            for i, result in enumerate(research_results[:3], 1):
                title = result.get('title', 'Untitled')
                summary = result.get('summary', 'No summary available')
                source = result.get('source', 'Unknown source')
                relevance = result.get('query_relevance', 'unknown')
                
                markdown += f"""
### {i}. {title}

{summary}

{source_emoji} **Source:** {source} | **Relevance:** {relevance}

"""
            
            markdown += "---\n"
            return markdown
    
    def _create_risk_assessment(self, analysis_result: Dict[str, Any]) -> str:
        """Create risk assessment section."""
        summary_data = analysis_result.get('summary', {})
        volatility_assessment = summary_data.get('volatility_assessment', {})
        
        volatility_level = volatility_assessment.get('level', 'unknown')
        volatility_trend = volatility_assessment.get('trend', 'unknown')
        
        # Get emojis
        risk_emoji = self._get_emoji('general', 'risk')
        warning_emoji = self._get_emoji('sentiment', 'warning')
        
        # Risk level descriptions
        risk_descriptions = {
            'low': 'The stock shows relatively stable price movements with lower volatility',
            'medium': 'The stock exhibits moderate price fluctuations requiring careful monitoring',
            'high': 'The stock is highly volatile and poses significant risk for investors'
        }
        
        risk_color = {
            'low': '#28a745',
            'medium': '#ffc107',
            'high': '#dc3545'
        }.get(volatility_level, '#6c757d')
        
        if self.output_format == "html":
            return f"""
            <div class="risk-assessment" style="margin: 20px 0;">
                <h2 style="color: {risk_color};">{risk_emoji} Risk Assessment</h2>
                <div style="background: {risk_color}20; padding: 20px; border-radius: 8px; border-left: 4px solid {risk_color};">
                    <h4 style="margin: 0 0 10px 0; color: {risk_color};">
                        {warning_emoji} Volatility Level: {volatility_level.title()}
                    </h4>
                    <p style="margin: 0 0 10px 0; line-height: 1.6;">
                        {risk_descriptions.get(volatility_level, 'Risk level assessment unavailable')}
                    </p>
                    <p style="margin: 0; color: #666; font-size: 0.9em;">
                        <strong>Trend:</strong> {volatility_trend.replace('_', ' ').title()}
                    </p>
                </div>
            </div>
            """
        else:  # markdown
            return f"""
## {risk_emoji} Risk Assessment

### {warning_emoji} Volatility Level: {volatility_level.title()}

{risk_descriptions.get(volatility_level, 'Risk level assessment unavailable')}

**Trend:** {volatility_trend.replace('_', ' ').title()}

---
"""
    
    def _create_recommendations(self, analysis_result: Dict[str, Any]) -> str:
        """Create recommendations section."""
        summary_data = analysis_result.get('summary', {})
        trend_analysis = summary_data.get('trend_analysis', {})
        trading_signals = summary_data.get('trading_signals', {})
        
        overall_trend = trend_analysis.get('overall_trend', 'neutral')
        
        # Get emojis
        recommendation_emoji = self._get_emoji('general', 'recommendation')
        opportunity_emoji = self._get_emoji('general', 'opportunity')
        
        # Create recommendations based on analysis
        recommendations = []
        
        if overall_trend == 'bullish':
            recommendations.append({
                'action': 'Consider buying on dips',
                'reason': 'Strong upward momentum suggests potential for continued gains',
                'emoji': self._get_emoji('actions', 'buy')
            })
        elif overall_trend == 'bearish':
            recommendations.append({
                'action': 'Consider reducing position or setting stop-loss',
                'reason': 'Downward momentum suggests potential for further declines',
                'emoji': self._get_emoji('actions', 'sell')
            })
        else:
            recommendations.append({
                'action': 'Monitor closely and wait for clearer signals',
                'reason': 'Mixed signals suggest uncertainty in near-term direction',
                'emoji': self._get_emoji('actions', 'watch')
            })
        
        # Add general recommendations
        recommendations.extend([
            {
                'action': 'Diversify your portfolio',
                'reason': 'Never put all your eggs in one basket',
                'emoji': self._get_emoji('actions', 'research')
            },
            {
                'action': 'Set clear entry and exit strategies',
                'reason': 'Having a plan helps manage emotions and risk',
                'emoji': self._get_emoji('general', 'analysis')
            }
        ])
        
        if self.output_format == "html":
            html = f"""
            <div class="recommendations" style="margin: 20px 0;">
                <h2 style="color: #007bff;">{recommendation_emoji} Investment Recommendations</h2>
                <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; border-left: 4px solid #2196f3;">
            """
            
            for rec in recommendations:
                html += f"""
                    <div style="margin-bottom: 15px; padding: 15px; background: white; border-radius: 5px;">
                        <div style="display: flex; align-items: center;">
                            <span style="font-size: 1.5em; margin-right: 15px;">{rec['emoji']}</span>
                            <div>
                                <h5 style="margin: 0 0 5px 0; color: #333;">{rec['action']}</h5>
                                <p style="margin: 0; color: #666; font-size: 0.9em;">{rec['reason']}</p>
                            </div>
                        </div>
                    </div>
                """
            
            html += """
                </div>
                <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin-top: 15px; border-left: 4px solid #ffc107;">
                    <p style="margin: 0; color: #856404; font-size: 0.9em;">
                        <strong>⚠️ Disclaimer:</strong> This analysis is for educational purposes only and should not be considered as financial advice. 
                        Always do your own research and consult with a financial advisor before making investment decisions.
                    </p>
                </div>
            </div>
            """
            return html
        else:  # markdown
            markdown = f"""
## {recommendation_emoji} Investment Recommendations

"""
            for rec in recommendations:
                markdown += f"""
### {rec['emoji']} {rec['action']}

{rec['reason']}

"""
            
            markdown += """
### ⚠️ Disclaimer

This analysis is for educational purposes only and should not be considered as financial advice. 
Always do your own research and consult with a financial advisor before making investment decisions.

---
"""
            return markdown
    
    def _create_footer(self, analysis_result: Dict[str, Any]) -> str:
        """Create footer with citations and metadata."""
        ticker = analysis_result.get('ticker', 'UNKNOWN')
        processing_time = analysis_result.get('processing_time', 0)
        analysis_date = analysis_result.get('analysis_date', datetime.now().isoformat())
        
        # Get emojis
        summary_emoji = self._get_emoji('general', 'summary')
        source_emoji = self._get_emoji('general', 'source')
        
        if self.output_format == "html":
            return f"""
            <div class="analysis-footer" style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-top: 30px; border-top: 2px solid #dee2e6;">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                    <div>
                        <h5 style="margin: 0 0 10px 0; color: #495057;">{summary_emoji} Analysis Details</h5>
                        <p style="margin: 0; color: #6c757d; font-size: 0.9em;">
                            <strong>Ticker:</strong> {ticker}<br>
                            <strong>Processing Time:</strong> {processing_time:.2f}s<br>
                            <strong>Analysis Date:</strong> {analysis_date}
                        </p>
                    </div>
                    <div>
                        <h5 style="margin: 0 0 10px 0; color: #495057;">{source_emoji} Data Sources</h5>
                        <p style="margin: 0; color: #6c757d; font-size: 0.9em;">
                            • Yahoo Finance API<br>
                            • Technical Analysis Library<br>
                            • Multi-Agent Financial Analyst
                        </p>
                    </div>
                </div>
                <hr style="margin: 20px 0; border: none; border-top: 1px solid #dee2e6;">
                <p style="text-align: center; margin: 0; color: #6c757d; font-size: 0.8em;">
                    Generated by Multi-Agent Financial Analyst Tool | 
                    <a href="#" style="color: #007bff;">Terms of Use</a> | 
                    <a href="#" style="color: #007bff;">Privacy Policy</a>
                </p>
            </div>
            """
        else:  # markdown
            return f"""
---

## {summary_emoji} Analysis Details

- **Ticker:** {ticker}
- **Processing Time:** {processing_time:.2f}s
- **Analysis Date:** {analysis_date}

## {source_emoji} Data Sources

- Yahoo Finance API
- Technical Analysis Library
- Multi-Agent Financial Analyst

---

*Generated by Multi-Agent Financial Analyst Tool*
"""
    
    def _combine_sections(self, sections: List[str], style: str) -> str:
        """Combine all sections into final explanation."""
        if self.output_format == "html":
            # Add CSS styles for better presentation
            css_styles = """
            <style>
                .analysis-container {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }
                .metric-card:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
                    transition: all 0.3s ease;
                }
                .indicator-card:hover {
                    transform: translateY(-2px);
                    transition: all 0.3s ease;
                }
                @media (max-width: 768px) {
                    .analysis-header h1 {
                        font-size: 2em !important;
                    }
                    .executive-summary {
                        padding: 15px !important;
                    }
                }
            </style>
            """
            
            return f"""
            <div class="analysis-container">
                {css_styles}
                {''.join(sections)}
            </div>
            """
        else:  # markdown
            return '\n\n'.join(sections)
    
    def _get_emoji(self, category: str, key: str) -> str:
        """Get emoji for given category and key."""
        if not self.include_emojis:
            return ""
        
        return self.emoji_maps.get(category, {}).get(key, "")


# Convenience functions for direct usage
def explain_analysis(analysis_result: Dict[str, Any],
                    research_results: Optional[List[Dict[str, Any]]] = None,
                    output_format: str = "html",
                    include_emojis: bool = True) -> str:
    """
    Convenience function to explain analysis results.
    
    Args:
        analysis_result (Dict[str, Any]): Analysis result from DataAgent
        research_results (Optional[List[Dict]]): Research results from ResearchAgent
        output_format (str): Output format ('html', 'markdown')
        include_emojis (bool): Whether to include emojis
        
    Returns:
        str: Formatted explanation
    """
    explainer = ExplainerAgent(
        include_emojis=include_emojis,
        output_format=output_format
    )
    return explainer.explain_analysis(analysis_result, research_results)


# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)
