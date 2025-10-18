"""
Agents package for Multi-Agent Financial Analyst Tool.

This package contains specialized agent classes that handle different
aspects of financial analysis and data processing.
"""

from .data_agent import (
    DataAgent,
    DataAgentError
)

from .research_agent import (
    ResearchAgent,
    ResearchAgentError,
    research_financial_query
)

from .explainer_agent import (
    ExplainerAgent,
    ExplainerAgentError,
    explain_analysis
)

__all__ = [
    'DataAgent',
    'DataAgentError',
    'ResearchAgent',
    'ResearchAgentError',
    'research_financial_query',
    'ExplainerAgent',
    'ExplainerAgentError',
    'explain_analysis'
]

__version__ = "1.0.0"
