"""
Research Agent Module for Multi-Agent Financial Analyst Tool

This module provides a ResearchAgent class that uses RAG store for document
retrieval and LLM-powered summarization for financial research queries.

Author: Multi-Agent Financial Analyst Tool
Version: 1.0.0
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from functools import lru_cache
from loguru import logger
import traceback

# Add services to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from services.rag_store import RAGStore, RAGStoreError, DocumentResult

# LLM Integration - Support multiple backends
try:
    from langchain.llms import OpenAI
    from langchain.schema import PromptTemplate
    from langchain.chains import LLMChain
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class ResearchAgentError(Exception):
    """Custom exception for Research Agent operations."""
    pass


class ResearchAgent:
    """
    Research Agent for financial document analysis and summarization.
    
    This agent uses RAG store for document retrieval and LLM-powered
    summarization to provide concise financial research insights.
    """
    
    def __init__(self, 
                 collection_name: str = "financial_docs",
                 llm_provider: str = "openai",
                 model_name: str = "openai/gpt-3.5-turbo",  # Default to OpenRouter format
                 max_tokens: int = 200,
                 temperature: float = 0.3):
        """
        Initialize the Research Agent.
        
        Args:
            collection_name (str): Name of the ChromaDB collection
            llm_provider (str): LLM provider ('openai', 'huggingface', 'langchain')
            model_name (str): Model name for the LLM
            max_tokens (int): Maximum tokens for summarization
            temperature (float): Temperature for LLM generation
        """
        self.collection_name = collection_name
        self.llm_provider = llm_provider.lower()
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # Initialize components
        self.rag_store = None
        self.llm = None
        self.summarizer = None
        
        self._setup_logging()
        self._initialize_components()
        
    def _setup_logging(self) -> None:
        """Setup logging configuration for the research agent."""
        logger.add(
            "logs/research_agent.log",
            rotation="10 MB",
            retention="7 days",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}"
        )
        
    def _initialize_components(self) -> None:
        """Initialize RAG store and LLM components."""
        try:
            # Initialize RAG store
            logger.info("Initializing RAG store...")
            self.rag_store = RAGStore(collection_name=self.collection_name)
            self.rag_store.initialize_vector_store()
            
            # Initialize LLM based on provider
            self._initialize_llm()
            
            logger.info(f"ResearchAgent initialized with {self.llm_provider} LLM")
            
        except Exception as e:
            error_msg = f"Failed to initialize ResearchAgent components: {str(e)}"
            logger.error(error_msg)
            raise ResearchAgentError(error_msg) from e
    
    def _initialize_llm(self) -> None:
        """Initialize LLM based on provider."""
        try:
            if self.llm_provider == "openai":
                self._initialize_openai()
            elif self.llm_provider == "huggingface":
                self._initialize_huggingface()
            elif self.llm_provider == "langchain":
                self._initialize_langchain()
            else:
                # Fallback to simple text summarization
                logger.warning(f"Unknown LLM provider: {self.llm_provider}, using fallback")
                self.llm_provider = "fallback"
                self._initialize_fallback()
                
        except Exception as e:
            logger.warning(f"Failed to initialize {self.llm_provider} LLM: {str(e)}")
            logger.info("Falling back to simple text summarization")
            self.llm_provider = "fallback"
            self._initialize_fallback()
    
    def _initialize_openai(self) -> None:
        """Initialize OpenAI LLM (supports both OpenAI and OpenRouter)."""
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not available")
        
        # Check for OpenRouter API key first (preferred for cost-effectiveness)
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Either OPENROUTER_API_KEY or OPENAI_API_KEY must be set")
        
        # Determine base URL based on API key
        if api_key.startswith("sk-or-v1-"):
            # OpenRouter API key
            base_url = "https://openrouter.ai/api/v1"
            logger.info("Using OpenRouter API")
        else:
            # OpenAI API key
            base_url = None
            logger.info("Using OpenAI API")
        
        self.llm = openai.OpenAI(
            api_key=api_key,
            base_url=base_url,
            model=self.model_name
        )
        logger.info(f"LLM initialized with model: {self.model_name}")
    
    def _initialize_huggingface(self) -> None:
        """Initialize Hugging Face transformers."""
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("Transformers package not available")
        
        # Use a smaller, faster model for summarization
        model_name = "facebook/bart-large-cnn" if self.model_name == "default" else self.model_name
        
        try:
            self.summarizer = pipeline(
                "summarization",
                model=model_name,
                tokenizer=model_name,
                max_length=self.max_tokens,
                min_length=50,
                do_sample=False
            )
            logger.info(f"Hugging Face summarizer initialized with model: {model_name}")
        except Exception as e:
            logger.warning(f"Failed to load {model_name}, using default model")
            self.summarizer = pipeline("summarization")
    
    def _initialize_langchain(self) -> None:
        """Initialize LangChain LLM."""
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain package not available")
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable required for LangChain")
        
        self.llm = OpenAI(
            model_name=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            openai_api_key=api_key
        )
        logger.info(f"LangChain LLM initialized with model: {self.model_name}")
    
    def _initialize_fallback(self) -> None:
        """Initialize fallback summarization (simple text extraction)."""
        self.summarizer = None
        logger.info("Using fallback text summarization")
    
    def research_query(self, 
                      query: str, 
                      k: int = 3,
                      include_context: bool = True) -> List[Dict[str, Any]]:
        """
        Research a financial query and return summarized results.
        
        Args:
            query (str): Financial research query
            k (int): Number of documents to retrieve and summarize
            include_context (bool): Whether to include additional context
            
        Returns:
            List[Dict[str, Any]]: List of research results with title, summary, source
            
        Raises:
            ResearchAgentError: If research fails
            
        Example:
            >>> agent = ResearchAgent()
            >>> results = agent.research_query("What are the key factors affecting tech stock volatility?")
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Starting research query: '{query}' (k={k})")
            
            # Validate inputs
            if not query or not isinstance(query, str):
                raise ValueError("Query must be a non-empty string")
            
            if k <= 0 or k > 10:
                raise ValueError("k must be between 1 and 10")
            
            # Step 1: Retrieve relevant documents
            logger.info("Retrieving relevant documents...")
            documents = self._retrieve_documents(query, k)
            
            if not documents:
                logger.warning("No documents found for query")
                return []
            
            # Step 2: Summarize each document
            logger.info(f"Summarizing {len(documents)} documents...")
            research_results = []
            
            for i, doc in enumerate(documents):
                try:
                    summary = self._summarize_document(doc, query, include_context)
                    
                    result = {
                        'title': doc.title,
                        'summary': summary,
                        'source': doc.source_path,
                        'score': doc.score,
                        'metadata': doc.metadata,
                        'query_relevance': self._assess_relevance(doc, query)
                    }
                    
                    research_results.append(result)
                    logger.info(f"Summarized document {i+1}/{len(documents)}: {doc.title}")
                    
                except Exception as e:
                    logger.error(f"Failed to summarize document {doc.title}: {str(e)}")
                    # Add document without summary
                    result = {
                        'title': doc.title,
                        'summary': f"Summary unavailable: {str(e)}",
                        'source': doc.source_path,
                        'score': doc.score,
                        'metadata': doc.metadata,
                        'query_relevance': 'unknown'
                    }
                    research_results.append(result)
            
            # Step 3: Sort by relevance and score
            research_results.sort(key=lambda x: (x['score'], x['query_relevance']), reverse=True)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Research completed in {processing_time:.2f}s, {len(research_results)} results")
            
            return research_results
            
        except Exception as e:
            error_msg = f"Research query failed: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            raise ResearchAgentError(error_msg) from e
    
    def _retrieve_documents(self, query: str, k: int) -> List[DocumentResult]:
        """Retrieve relevant documents from RAG store."""
        try:
            if not self.rag_store:
                raise ResearchAgentError("RAG store not initialized")
            
            documents = self.rag_store.retrieve_docs(query, k=k)
            
            if not documents:
                logger.warning(f"No documents found for query: '{query}'")
                return []
            
            logger.info(f"Retrieved {len(documents)} documents for query")
            return documents
            
        except RAGStoreError as e:
            logger.error(f"RAG store retrieval failed: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error retrieving documents: {str(e)}")
            return []
    
    def _summarize_document(self, 
                           doc: DocumentResult, 
                           query: str, 
                           include_context: bool) -> str:
        """Summarize a document using the configured LLM."""
        try:
            # Prepare text for summarization
            full_text = doc.text_excerpt
            if include_context and doc.metadata:
                context_info = f"Source: {doc.metadata.get('file_name', 'Unknown')}\n"
                full_text = context_info + full_text
            
            # Summarize based on LLM provider
            if self.llm_provider == "openai":
                return self._summarize_with_openai(full_text, query)
            elif self.llm_provider == "huggingface":
                return self._summarize_with_huggingface(full_text)
            elif self.llm_provider == "langchain":
                return self._summarize_with_langchain(full_text, query)
            else:
                return self._summarize_fallback(full_text)
                
        except Exception as e:
            logger.error(f"Summarization failed for {doc.title}: {str(e)}")
            return f"Summarization failed: {str(e)}"
    
    def _summarize_with_openai(self, text: str, query: str) -> str:
        """Summarize using OpenAI API."""
        try:
            prompt = self._create_summarization_prompt(text, query)
            
            response = self.llm.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a financial research assistant. Provide concise, accurate summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            logger.error(f"OpenAI summarization failed: {str(e)}")
            return self._summarize_fallback(text)
    
    def _summarize_with_huggingface(self, text: str) -> str:
        """Summarize using Hugging Face transformers."""
        try:
            if not self.summarizer:
                return self._summarize_fallback(text)
            
            # Truncate text if too long for the model
            max_input_length = 1024
            if len(text) > max_input_length:
                text = text[:max_input_length] + "..."
            
            summary = self.summarizer(text, max_length=self.max_tokens, min_length=50, do_sample=False)
            return summary[0]['summary_text'].strip()
            
        except Exception as e:
            logger.error(f"Hugging Face summarization failed: {str(e)}")
            return self._summarize_fallback(text)
    
    def _summarize_with_langchain(self, text: str, query: str) -> str:
        """Summarize using LangChain."""
        try:
            prompt_template = PromptTemplate(
                input_variables=["text", "query"],
                template="""
                Based on the following financial document excerpt and research query, provide a concise summary:
                
                Query: {query}
                
                Document Excerpt:
                {text}
                
                Summary (max {max_tokens} words):
                """
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt_template)
            
            result = chain.run(
                text=text,
                query=query,
                max_tokens=self.max_tokens
            )
            
            return result.strip()
            
        except Exception as e:
            logger.error(f"LangChain summarization failed: {str(e)}")
            return self._summarize_fallback(text)
    
    def _summarize_fallback(self, text: str) -> str:
        """Fallback summarization using simple text extraction."""
        try:
            # Simple extractive summarization
            sentences = text.split('. ')
            if len(sentences) <= 3:
                return text
            
            # Take first few sentences and last sentence
            summary_sentences = sentences[:2] + [sentences[-1]]
            summary = '. '.join(summary_sentences)
            
            # Ensure it ends with a period
            if not summary.endswith('.'):
                summary += '.'
            
            return summary
            
        except Exception as e:
            logger.error(f"Fallback summarization failed: {str(e)}")
            return text[:200] + "..." if len(text) > 200 else text
    
    def _create_summarization_prompt(self, text: str, query: str) -> str:
        """Create a prompt for summarization."""
        return f"""
        Please provide a concise summary of the following financial document excerpt that directly addresses the research query.
        
        Research Query: {query}
        
        Document Excerpt:
        {text}
        
        Requirements:
        - Focus on information relevant to the query
        - Keep summary under {self.max_tokens} words
        - Use clear, professional language
        - Highlight key financial insights or data points
        
        Summary:
        """
    
    def _assess_relevance(self, doc: DocumentResult, query: str) -> str:
        """Assess how relevant a document is to the query."""
        try:
            score = doc.score
            
            if score >= 0.8:
                return 'high'
            elif score >= 0.6:
                return 'medium'
            elif score >= 0.4:
                return 'low'
            else:
                return 'very_low'
                
        except Exception:
            return 'unknown'
    
    @lru_cache(maxsize=32)
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the document collection."""
        try:
            if not self.rag_store:
                return {'error': 'RAG store not initialized'}
            
            stats = self.rag_store.get_collection_stats()
            stats['llm_provider'] = self.llm_provider
            stats['model_name'] = self.model_name
            stats['timestamp'] = datetime.now().isoformat()
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {str(e)}")
            return {'error': str(e)}
    
    def ingest_documents(self, folder_path: str) -> Dict[str, int]:
        """
        Ingest documents into the RAG store.
        
        Args:
            folder_path (str): Path to folder containing documents
            
        Returns:
            Dict[str, int]: Ingestion statistics
        """
        try:
            if not self.rag_store:
                raise ResearchAgentError("RAG store not initialized")
            
            logger.info(f"Ingesting documents from: {folder_path}")
            results = self.rag_store.ingest_documents(folder_path)
            
            logger.info(f"Document ingestion completed: {results}")
            return results
            
        except Exception as e:
            error_msg = f"Document ingestion failed: {str(e)}"
            logger.error(error_msg)
            raise ResearchAgentError(error_msg) from e
    
    def clear_collection(self) -> bool:
        """Clear the document collection."""
        try:
            if not self.rag_store:
                raise ResearchAgentError("RAG store not initialized")
            
            success = self.rag_store.clear_collection()
            logger.info("Document collection cleared")
            return success
            
        except Exception as e:
            error_msg = f"Failed to clear collection: {str(e)}"
            logger.error(error_msg)
            raise ResearchAgentError(error_msg) from e


# Convenience functions for direct usage
def research_financial_query(query: str, 
                           k: int = 3,
                           collection_name: str = "financial_docs",
                           llm_provider: str = "openai") -> List[Dict[str, Any]]:
    """
    Convenience function to research a financial query.
    
    Args:
        query (str): Financial research query
        k (int): Number of documents to retrieve
        collection_name (str): Name of the ChromaDB collection
        llm_provider (str): LLM provider to use
        
    Returns:
        List[Dict[str, Any]]: Research results
    """
    agent = ResearchAgent(
        collection_name=collection_name,
        llm_provider=llm_provider
    )
    return agent.research_query(query, k=k)


# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)
