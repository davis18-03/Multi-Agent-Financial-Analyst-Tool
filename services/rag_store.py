"""
RAG Store Module for Multi-Agent Financial Analyst Tool

This module provides functions to manage a ChromaDB vector store for
Retrieval-Augmented Generation (RAG) operations using sentence-transformers
for embeddings and local document storage.

Author: Multi-Agent Financial Analyst Tool
Version: 1.0.0
"""

import chromadb
from chromadb.config import Settings
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional, Tuple
import os
import json
from pathlib import Path
from datetime import datetime
from loguru import logger
import hashlib
import re
from dataclasses import dataclass


@dataclass
class DocumentResult:
    """Data class for document retrieval results."""
    title: str
    text_excerpt: str
    source_path: str
    score: float
    metadata: Optional[Dict] = None


class RAGStoreError(Exception):
    """Custom exception for RAG store operations."""
    pass


class RAGStore:
    """
    A class to manage ChromaDB vector store for RAG operations.
    
    This class provides methods to initialize, ingest documents, and retrieve
    relevant documents using semantic search with sentence-transformers embeddings.
    """
    
    def __init__(self, 
                 collection_name: str = "financial_docs",
                 persist_directory: str = "vector_store",
                 embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize the RAG Store.
        
        Args:
            collection_name (str): Name of the ChromaDB collection
            persist_directory (str): Directory to persist vector data
            embedding_model (str): Sentence transformer model name
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.embedding_model_name = embedding_model
        
        # Initialize components
        self.client = None
        self.collection = None
        self.embedding_model = None
        
        self._setup_logging()
        
    def _setup_logging(self) -> None:
        """Setup logging configuration for the RAG store."""
        logger.add(
            "logs/rag_store.log",
            rotation="10 MB",
            retention="7 days",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}"
        )
        
    def initialize_vector_store(self) -> bool:
        """
        Initialize the ChromaDB vector store and embedding model.
        
        Returns:
            bool: True if initialization successful, False otherwise
            
        Raises:
            RAGStoreError: If initialization fails
        """
        try:
            logger.info("Initializing vector store...")
            
            # Create persist directory if it doesn't exist
            os.makedirs(self.persist_directory, exist_ok=True)
            
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Initialize embedding model
            logger.info(f"Loading embedding model: {self.embedding_model_name}")
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection(name=self.collection_name)
                logger.info(f"Retrieved existing collection: {self.collection_name}")
            except ValueError:
                # Collection doesn't exist, create it
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "Financial documents for RAG"}
                )
                logger.info(f"Created new collection: {self.collection_name}")
            
            # Test the setup
            test_query = "test query"
            test_embedding = self.embedding_model.encode(test_query)
            
            logger.info("Vector store initialized successfully")
            return True
            
        except Exception as e:
            error_msg = f"Failed to initialize vector store: {str(e)}"
            logger.error(error_msg)
            raise RAGStoreError(error_msg) from e
    
    def ingest_documents(self, folder_path: str) -> Dict[str, int]:
        """
        Ingest documents from a folder into the vector store.
        
        Args:
            folder_path (str): Path to folder containing documents
            
        Returns:
            Dict[str, int]: Summary of ingestion results
            
        Raises:
            RAGStoreError: If ingestion fails
            
        Example:
            >>> rag_store = RAGStore()
            >>> rag_store.initialize_vector_store()
            >>> results = rag_store.ingest_documents("documents/")
        """
        try:
            if not self.collection:
                raise RAGStoreError("Vector store not initialized. Call initialize_vector_store() first.")
            
            folder_path = Path(folder_path)
            if not folder_path.exists():
                raise RAGStoreError(f"Folder path does not exist: {folder_path}")
            
            logger.info(f"Ingesting documents from: {folder_path}")
            
            # Supported file extensions
            supported_extensions = {'.txt', '.md', '.pdf', '.csv', '.json'}
            
            documents = []
            metadatas = []
            ids = []
            
            ingestion_stats = {
                'total_files': 0,
                'processed_files': 0,
                'failed_files': 0,
                'chunks_created': 0
            }
            
            # Process all files in the folder
            for file_path in folder_path.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                    ingestion_stats['total_files'] += 1
                    
                    try:
                        # Extract text content
                        text_content = self._extract_text_from_file(file_path)
                        
                        if not text_content.strip():
                            logger.warning(f"No text content found in: {file_path}")
                            continue
                        
                        # Chunk the document
                        chunks = self._chunk_document(text_content, file_path)
                        
                        for i, chunk in enumerate(chunks):
                            # Generate unique ID for the chunk
                            chunk_id = self._generate_chunk_id(file_path, i)
                            
                            # Create metadata
                            metadata = {
                                'source_path': str(file_path),
                                'file_name': file_path.name,
                                'file_type': file_path.suffix,
                                'chunk_index': i,
                                'total_chunks': len(chunks),
                                'ingestion_date': datetime.now().isoformat(),
                                'file_size': file_path.stat().st_size
                            }
                            
                            documents.append(chunk)
                            metadatas.append(metadata)
                            ids.append(chunk_id)
                            
                            ingestion_stats['chunks_created'] += 1
                        
                        ingestion_stats['processed_files'] += 1
                        logger.info(f"Processed {file_path.name}: {len(chunks)} chunks")
                        
                    except Exception as e:
                        ingestion_stats['failed_files'] += 1
                        logger.error(f"Failed to process {file_path}: {str(e)}")
                        continue
            
            # Add documents to collection in batches
            if documents:
                batch_size = 100
                for i in range(0, len(documents), batch_size):
                    batch_docs = documents[i:i + batch_size]
                    batch_metadatas = metadatas[i:i + batch_size]
                    batch_ids = ids[i:i + batch_size]
                    
                    self.collection.add(
                        documents=batch_docs,
                        metadatas=batch_metadatas,
                        ids=batch_ids
                    )
                
                logger.info(f"Ingestion complete: {ingestion_stats}")
            else:
                logger.warning("No documents found to ingest")
            
            return ingestion_stats
            
        except Exception as e:
            error_msg = f"Failed to ingest documents: {str(e)}"
            logger.error(error_msg)
            raise RAGStoreError(error_msg) from e
    
    def retrieve_docs(self, query: str, k: int = 3) -> List[DocumentResult]:
        """
        Retrieve relevant documents based on a query.
        
        Args:
            query (str): Search query
            k (int): Number of documents to retrieve
            
        Returns:
            List[DocumentResult]: List of relevant documents with metadata
            
        Raises:
            RAGStoreError: If retrieval fails
            
        Example:
            >>> rag_store = RAGStore()
            >>> rag_store.initialize_vector_store()
            >>> results = rag_store.retrieve_docs("What is market volatility?", k=5)
        """
        try:
            if not self.collection:
                raise RAGStoreError("Vector store not initialized. Call initialize_vector_store() first.")
            
            logger.info(f"Retrieving documents for query: '{query}' (k={k})")
            
            # Perform similarity search
            results = self.collection.query(
                query_texts=[query],
                n_results=k,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Process results
            document_results = []
            
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    # Convert distance to similarity score (higher is better)
                    score = 1 / (1 + distance) if distance > 0 else 1.0
                    
                    # Create text excerpt (first 200 characters)
                    text_excerpt = doc[:200] + "..." if len(doc) > 200 else doc
                    
                    # Generate title from file name or first line
                    title = self._generate_title(doc, metadata)
                    
                    document_result = DocumentResult(
                        title=title,
                        text_excerpt=text_excerpt,
                        source_path=metadata.get('source_path', ''),
                        score=score,
                        metadata=metadata
                    )
                    
                    document_results.append(document_result)
            
            logger.info(f"Retrieved {len(document_results)} documents")
            return document_results
            
        except Exception as e:
            error_msg = f"Failed to retrieve documents: {str(e)}"
            logger.error(error_msg)
            raise RAGStoreError(error_msg) from e
    
    def get_collection_stats(self) -> Dict:
        """
        Get statistics about the vector store collection.
        
        Returns:
            Dict: Collection statistics
        """
        try:
            if not self.collection:
                raise RAGStoreError("Vector store not initialized")
            
            count = self.collection.count()
            
            # Get sample documents to analyze
            sample_results = self.collection.get(limit=100)
            
            # Analyze file types
            file_types = {}
            source_files = set()
            
            if sample_results['metadatas']:
                for metadata in sample_results['metadatas']:
                    file_type = metadata.get('file_type', 'unknown')
                    file_types[file_type] = file_types.get(file_type, 0) + 1
                    source_files.add(metadata.get('source_path', ''))
            
            stats = {
                'total_chunks': count,
                'unique_source_files': len(source_files),
                'file_types': file_types,
                'collection_name': self.collection_name,
                'embedding_model': self.embedding_model_name
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {str(e)}")
            return {'error': str(e)}
    
    def clear_collection(self) -> bool:
        """
        Clear all documents from the collection.
        
        Returns:
            bool: True if successful
        """
        try:
            if not self.collection:
                raise RAGStoreError("Vector store not initialized")
            
            # Delete and recreate collection
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Financial documents for RAG"}
            )
            
            logger.info("Collection cleared successfully")
            return True
            
        except Exception as e:
            error_msg = f"Failed to clear collection: {str(e)}"
            logger.error(error_msg)
            raise RAGStoreError(error_msg) from e
    
    def _extract_text_from_file(self, file_path: Path) -> str:
        """Extract text content from various file types."""
        try:
            if file_path.suffix.lower() == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            elif file_path.suffix.lower() == '.md':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            elif file_path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path)
                return df.to_string()
            
            elif file_path.suffix.lower() == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return json.dumps(data, indent=2)
            
            elif file_path.suffix.lower() == '.pdf':
                # Basic PDF text extraction (you might want to use PyPDF2 or pdfplumber)
                logger.warning(f"PDF support not fully implemented for: {file_path}")
                return ""
            
            else:
                # Try to read as text
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
                    
        except Exception as e:
            logger.error(f"Failed to extract text from {file_path}: {str(e)}")
            return ""
    
    def _chunk_document(self, text: str, file_path: Path) -> List[str]:
        """Split document into chunks for better retrieval."""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Chunk size and overlap
        chunk_size = 500  # characters
        overlap = 50      # characters
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings within the last 100 characters
                search_start = max(start + chunk_size - 100, start)
                sentence_endings = ['.', '!', '?', '\n']
                
                for i in range(end, search_start, -1):
                    if text[i] in sentence_endings:
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks if chunks else [text]
    
    def _generate_chunk_id(self, file_path: Path, chunk_index: int) -> str:
        """Generate a unique ID for a document chunk."""
        # Create a hash of the file path and chunk index
        content = f"{file_path}_{chunk_index}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _generate_title(self, text: str, metadata: Dict) -> str:
        """Generate a title for a document chunk."""
        # Try to get title from metadata first
        file_name = metadata.get('file_name', '')
        if file_name:
            # Remove extension for cleaner title
            title = Path(file_name).stem
            if metadata.get('total_chunks', 1) > 1:
                chunk_idx = metadata.get('chunk_index', 0)
                title = f"{title} (Part {chunk_idx + 1})"
            return title
        
        # Generate title from first line of text
        first_line = text.split('\n')[0].strip()
        if len(first_line) > 50:
            first_line = first_line[:50] + "..."
        
        return first_line if first_line else "Untitled Document"


# Convenience functions for direct usage
def initialize_vector_store(collection_name: str = "financial_docs") -> bool:
    """
    Convenience function to initialize the vector store.
    
    Args:
        collection_name (str): Name of the ChromaDB collection
        
    Returns:
        bool: True if initialization successful
    """
    rag_store = RAGStore(collection_name=collection_name)
    return rag_store.initialize_vector_store()


def ingest_documents(folder_path: str, collection_name: str = "financial_docs") -> Dict[str, int]:
    """
    Convenience function to ingest documents.
    
    Args:
        folder_path (str): Path to folder containing documents
        collection_name (str): Name of the ChromaDB collection
        
    Returns:
        Dict[str, int]: Summary of ingestion results
    """
    rag_store = RAGStore(collection_name=collection_name)
    rag_store.initialize_vector_store()
    return rag_store.ingest_documents(folder_path)


def retrieve_docs(query: str, k: int = 3, collection_name: str = "financial_docs") -> List[DocumentResult]:
    """
    Convenience function to retrieve documents.
    
    Args:
        query (str): Search query
        k (int): Number of documents to retrieve
        collection_name (str): Name of the ChromaDB collection
        
    Returns:
        List[DocumentResult]: List of relevant documents
    """
    rag_store = RAGStore(collection_name=collection_name)
    rag_store.initialize_vector_store()
    return rag_store.retrieve_docs(query, k)


# Create necessary directories
os.makedirs("vector_store", exist_ok=True)
os.makedirs("logs", exist_ok=True)
