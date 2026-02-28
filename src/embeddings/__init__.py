"""Embeddings module for local AI embeddings"""
from .ollama_service import OllamaEmbeddingService, embedding_service

__all__ = ['OllamaEmbeddingService', 'embedding_service']
