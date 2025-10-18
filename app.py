"""
Streamlit Frontend for Multi-Agent Financial Analyst Tool

This module provides a beautiful chat interface that connects to the FastAPI
backend for comprehensive financial analysis and research capabilities.

Author: Multi-Agent Financial Analyst Tool
Version: 1.0.0
"""

import streamlit as st
import requests
import json
import pandas as pd
# import plotly.graph_objects as go  # Not used in current implementation
from datetime import datetime, timedelta
import time
import os
from typing import Dict, List, Any, Optional
import base64
from io import BytesIO
import uuid


# Page Configuration
st.set_page_config(
    page_title="Multi-Agent Financial Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo/multi-agent-fin-analyst',
        'Report a bug': 'https://github.com/your-repo/multi-agent-fin-analyst/issues',
        'About': "Multi-Agent Financial Analyst Tool v1.0.0"
    }
)

# Custom CSS for better styling
def load_custom_css():
    """Load custom CSS for improved styling."""
    st.markdown("""
    <style>
    /* Main app styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 3rem;
        font-weight: bold;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    /* Chat styling */
    .chat-container {
        max-height: 600px;
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        background-color: #f8f9fa;
    }
    
    .user-message {
        background-color: #007bff;
        color: white;
        padding: 1rem;
        border-radius: 15px 15px 5px 15px;
        margin: 1rem 0;
        margin-left: 20%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .ai-message {
        background-color: white;
        padding: 1rem;
        border-radius: 15px 15px 15px 5px;
        margin: 1rem 0;
        margin-right: 20%;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .message-timestamp {
        font-size: 0.8rem;
        opacity: 0.7;
        margin-top: 0.5rem;
    }
    
    /* Sidebar styling */
    .sidebar-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid #e0e0e0;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Chart container styling */
    .chart-container {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Watchlist styling */
    .watchlist-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem;
        border-bottom: 1px solid #e0e0e0;
    }
    
    .watchlist-item:last-child {
        border-bottom: none;
    }
    
    /* Loading animation */
    .loading-dots {
        display: inline-block;
    }
    
    .loading-dots::after {
        content: '...';
        animation: dots 1.5s steps(4, end) infinite;
    }
    
    @keyframes dots {
        0%, 20% { content: ''; }
        40% { content: '.'; }
        60% { content: '..'; }
        80%, 100% { content: '...'; }
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .user-message, .ai-message {
            margin-left: 5%;
            margin-right: 5%;
        }
    }
    
    /* Dark mode compatibility */
    @media (prefers-color-scheme: dark) {
        .chat-container {
            background-color: #1e1e1e;
            border-color: #404040;
        }
        
        .ai-message {
            background-color: #2d2d2d;
            border-color: #404040;
            color: #ffffff;
        }
        
        .sidebar-section {
            background-color: #2d2d2d;
            border-color: #404040;
        }
    }
    </style>
    """, unsafe_allow_html=True)


# Initialize session state
def initialize_session_state():
    """Initialize session state variables."""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'watchlist' not in st.session_state:
        st.session_state.watchlist = []
    
    if 'user_id' not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    
    if 'api_base_url' not in st.session_state:
        # Get backend URL from environment, secrets, or use default
        backend_port = os.environ.get("PORT", "8000")
        default_url = f"http://localhost:{backend_port}"
        st.session_state.api_base_url = os.environ.get("BACKEND_URL") or st.secrets.get("api", {}).get("backend_url", default_url)


# Backend API functions
def call_backend_api(endpoint: str, data: Dict = None, method: str = "GET") -> Optional[Dict]:
    """
    Call the FastAPI backend API.
    
    Args:
        endpoint (str): API endpoint
        data (Dict): Request data for POST requests
        method (str): HTTP method
        
    Returns:
        Optional[Dict]: API response or None if error
    """
    try:
        url = f"{st.session_state.api_base_url}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None


def send_query_to_backend(query: str) -> Optional[Dict]:
    """
    Send a query to the backend API.
    
    Args:
        query (str): User query
        
    Returns:
        Optional[Dict]: Backend response
    """
    data = {
        "user_id": st.session_state.user_id,
        "query": query
    }
    
    return call_backend_api("/query", data, "POST")


def get_backend_health() -> bool:
    """
    Check if the backend is healthy.
    
    Returns:
        bool: True if backend is healthy
    """
    response = call_backend_api("/health")
    return response is not None and response.get("status") == "healthy"


# UI Components
def render_header():
    """Render the main header."""
    st.markdown("""
    <div class="main-header">
        <h1>📊 Multi-Agent Financial Analyst</h1>
        <p>Powered by AI Agents • Real-time Analysis • Research Insights</p>
    </div>
    """, unsafe_allow_html=True)


def render_chat_message(message: Dict[str, Any], is_user: bool = True):
    """
    Render a chat message.
    
    Args:
        message (Dict): Message data
        is_user (bool): Whether this is a user message
    """
    if is_user:
        st.markdown(f"""
        <div class="user-message">
            <div>{message['content']}</div>
            <div class="message-timestamp">{message['timestamp']}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="ai-message">
            <div>{message['content']}</div>
            <div class="message-timestamp">{message['timestamp']}</div>
        </div>
        """, unsafe_allow_html=True)


def display_charts(chart_paths: List[str]):
    """
    Display charts from the backend.
    
    Args:
        chart_paths (List[str]): List of chart file paths
    """
    if not chart_paths:
        return
    
    for i, chart_path in enumerate(chart_paths):
        try:
            # Check if file exists
            if os.path.exists(chart_path):
                st.markdown(f"""
                <div class="chart-container">
                    <h4>📈 Technical Analysis Chart {i+1 if len(chart_paths) > 1 else ''}</h4>
                </div>
                """, unsafe_allow_html=True)
                
                # Display the image
                st.image(chart_path, use_column_width=True)
            else:
                st.warning(f"Chart not found: {chart_path}")
                
        except Exception as e:
            st.error(f"Error displaying chart {chart_path}: {str(e)}")


def display_citations(citations: List[Dict[str, str]]):
    """
    Display citations from research.
    
    Args:
        citations (List[Dict]): List of citations
    """
    if not citations:
        return
    
    with st.expander(f"📚 Research Citations ({len(citations)})", expanded=False):
        for i, citation in enumerate(citations, 1):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**{i}. {citation.get('title', 'Untitled')}**")
                st.write(f"Source: {citation.get('source', 'Unknown')}")
            
            with col2:
                relevance = citation.get('relevance', 'unknown')
                if relevance == 'high':
                    st.success("High Relevance")
                elif relevance == 'medium':
                    st.warning("Medium Relevance")
                else:
                    st.info("Low Relevance")


def render_sidebar():
    """Render the sidebar with watchlist and controls."""
    with st.sidebar:
        st.markdown("## 🎛️ Controls")
        
        # Backend status
        st.markdown("### 🔗 Backend Status")
        if get_backend_health():
            st.success("✅ Connected")
        else:
            st.error("❌ Disconnected")
            st.warning("Please check your backend URL in secrets")
        
        # Watchlist section
        st.markdown("### 📋 Watchlist")
        
        # Add to watchlist
        col1, col2 = st.columns([3, 1])
        with col1:
            new_ticker = st.text_input("Add Ticker", placeholder="e.g., AAPL", key="new_ticker")
        with col2:
            if st.button("➕", help="Add to watchlist"):
                if new_ticker and new_ticker.upper() not in [t['ticker'] for t in st.session_state.watchlist]:
                    st.session_state.watchlist.append({
                        'ticker': new_ticker.upper(),
                        'added_at': datetime.now().strftime("%Y-%m-%d %H:%M"),
                        'price': None
                    })
                    st.rerun()
        
        # Display watchlist
        if st.session_state.watchlist:
            for i, item in enumerate(st.session_state.watchlist):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**{item['ticker']}**")
                    st.caption(item['added_at'])
                
                with col2:
                    if st.button("📊", key=f"analyze_{i}", help="Analyze"):
                        query = f"Analyze {item['ticker']} stock"
                        st.session_state.pending_query = query
                        st.rerun()
                
                with col3:
                    if st.button("❌", key=f"remove_{i}", help="Remove"):
                        st.session_state.watchlist.pop(i)
                        st.rerun()
        else:
            st.info("No tickers in watchlist")
        
        # Export section
        st.markdown("### 📁 Export")
        
        if st.button("📄 Export Chat History", use_container_width=True):
            export_chat_history()
        
        if st.button("📊 Export Watchlist", use_container_width=True):
            export_watchlist()
        
        # Settings
        st.markdown("### ⚙️ Settings")
        
        # Backend URL configuration
        current_url = st.session_state.api_base_url
        new_url = st.text_input("Backend URL", value=current_url, help="Enter your FastAPI backend URL")
        
        if new_url != current_url:
            st.session_state.api_base_url = new_url
            st.rerun()


def export_chat_history():
    """Export chat history as CSV."""
    try:
        if not st.session_state.chat_history:
            st.warning("No chat history to export")
            return
        
        # Prepare data for export
        export_data = []
        for message in st.session_state.chat_history:
            export_data.append({
                'timestamp': message['timestamp'],
                'type': 'User' if message['is_user'] else 'AI',
                'content': message['content'],
                'processing_time': message.get('processing_time', ''),
                'charts_count': message.get('charts_count', 0),
                'citations_count': message.get('citations_count', 0)
            })
        
        # Create DataFrame
        df = pd.DataFrame(export_data)
        
        # Create download link
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="chat_history_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv">📥 Download CSV</a>'
        st.markdown(href, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error exporting chat history: {str(e)}")


def export_watchlist():
    """Export watchlist as CSV."""
    try:
        if not st.session_state.watchlist:
            st.warning("No watchlist to export")
            return
        
        # Create DataFrame
        df = pd.DataFrame(st.session_state.watchlist)
        
        # Create download link
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="watchlist_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv">📥 Download CSV</a>'
        st.markdown(href, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error exporting watchlist: {str(e)}")


def render_chat_interface():
    """Render the main chat interface."""
    st.markdown("## 💬 Financial Analysis Chat")
    
    # Chat container
    with st.container():
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Display chat history
        for message in st.session_state.chat_history:
            render_chat_message(message, message['is_user'])
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    st.markdown("---")
    
    # Handle pending query (from watchlist)
    if hasattr(st.session_state, 'pending_query'):
        query = st.session_state.pending_query
        delattr(st.session_state, 'pending_query')
    else:
        query = st.text_input(
            "Ask me about stocks, markets, or financial analysis...",
            placeholder="e.g., Analyze AAPL stock performance, What are the market trends?",
            key="chat_input"
        )
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        if st.button("🚀 Send Query", use_container_width=True, disabled=not query):
            if query:
                process_user_query(query)
    
    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()


def process_user_query(query: str):
    """
    Process a user query and get AI response.
    
    Args:
        query (str): User query
    """
    # Add user message to history
    user_message = {
        'content': query,
        'timestamp': datetime.now().strftime("%H:%M:%S"),
        'is_user': True
    }
    st.session_state.chat_history.append(user_message)
    
    # Show loading indicator
    with st.spinner("🤖 AI is analyzing your query..."):
        # Call backend API
        response = send_query_to_backend(query)
    
    if response:
        # Extract response data
        answer_html = response.get('answer_html', '')
        charts = response.get('charts', [])
        citations = response.get('citations', [])
        processing_time = response.get('processing_time', 0)
        metadata = response.get('metadata', {})
        
        # Create AI message
        ai_message = {
            'content': answer_html,
            'timestamp': datetime.now().strftime("%H:%M:%S"),
            'is_user': False,
            'processing_time': f"{processing_time:.2f}s",
            'charts_count': len(charts),
            'citations_count': len(citations),
            'charts': charts,
            'citations': citations,
            'metadata': metadata
        }
        
        st.session_state.chat_history.append(ai_message)
        
        # Display charts and citations
        if charts:
            display_charts(charts)
        
        if citations:
            display_citations(citations)
        
        # Show processing info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("⏱️ Processing Time", f"{processing_time:.2f}s")
        with col2:
            st.metric("📊 Charts", len(charts))
        with col3:
            st.metric("📚 Citations", len(citations))
        
    else:
        # Error message
        error_message = {
            'content': "❌ Sorry, I couldn't process your query. Please check the backend connection and try again.",
            'timestamp': datetime.now().strftime("%H:%M:%S"),
            'is_user': False
        }
        st.session_state.chat_history.append(error_message)
    
    # Rerun to update the display
    st.rerun()


def render_footer():
    """Render the footer."""
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**📊 Multi-Agent Financial Analyst**")
        st.caption("Powered by AI Agents")
    
    with col2:
        st.markdown("**🔗 Backend Status**")
        if get_backend_health():
            st.caption("✅ Connected")
        else:
            st.caption("❌ Disconnected")
    
    with col3:
        st.markdown("**📈 Session Info**")
        st.caption(f"User: {st.session_state.user_id[:8]}...")


# Main app
def main():
    """Main application function."""
    # Load custom CSS
    load_custom_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Render header
    render_header()
    
    # Render sidebar
    render_sidebar()
    
    # Render main chat interface
    render_chat_interface()
    
    # Render footer
    render_footer()
    
    # Add some example queries
    st.markdown("---")
    st.markdown("### 💡 Try These Examples:")
    
    example_queries = [
        "Analyze AAPL stock performance last 6 months",
        "What are the current market trends?",
        "Compare MSFT and GOOGL stocks",
        "What factors affect tech stock volatility?",
        "Show me Tesla stock analysis"
    ]
    
    cols = st.columns(len(example_queries))
    for i, example in enumerate(example_queries):
        with cols[i]:
            if st.button(example, key=f"example_{i}", help="Click to try this query"):
                st.session_state.pending_query = example
                st.rerun()


if __name__ == "__main__":
    main()
