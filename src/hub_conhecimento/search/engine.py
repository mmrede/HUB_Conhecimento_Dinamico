"""
Knowledge Search Engine
Motor de Busca de Conhecimento

Provides search capabilities for knowledge documents.
"""

from typing import List, Dict, Any, Optional
import re

from ..core.models import KnowledgeDocument


class KnowledgeSearch:
    """
    Search engine for knowledge documents.
    Motor de busca para documentos de conhecimento.
    """
    
    def __init__(self, fuzzy_search: bool = True, fuzzy_distance: int = 2):
        """
        Initialize search engine.
        
        Args:
            fuzzy_search: Enable fuzzy search
            fuzzy_distance: Maximum edit distance for fuzzy matching
        """
        self.fuzzy_search = fuzzy_search
        self.fuzzy_distance = fuzzy_distance
        self.documents: List[KnowledgeDocument] = []
        self.index: Dict[str, List[str]] = {}  # word -> document IDs
    
    def index_document(self, document: KnowledgeDocument):
        """
        Add document to search index.
        
        Args:
            document: KnowledgeDocument to index
        """
        # Add to documents list
        if document not in self.documents:
            self.documents.append(document)
        
        # Index content words
        words = self._tokenize(document.content)
        words.extend(self._tokenize(document.title))
        words.extend(document.tags)
        words.extend(document.key_concepts)
        
        for word in words:
            word_lower = word.lower()
            if word_lower not in self.index:
                self.index[word_lower] = []
            if document.id not in self.index[word_lower]:
                self.index[word_lower].append(document.id)
    
    def search(
        self,
        query: str,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for documents matching query.
        
        Args:
            query: Search query
            category: Filter by category
            tags: Filter by tags
            max_results: Maximum number of results
            
        Returns:
            List of search results with relevance scores
        """
        query_words = self._tokenize(query)
        
        # Find matching documents
        document_scores: Dict[str, float] = {}
        
        for query_word in query_words:
            query_word_lower = query_word.lower()
            
            # Exact match
            if query_word_lower in self.index:
                for doc_id in self.index[query_word_lower]:
                    document_scores[doc_id] = document_scores.get(doc_id, 0) + 1.0
            
            # Fuzzy match if enabled
            if self.fuzzy_search:
                for indexed_word in self.index.keys():
                    if self._fuzzy_match(query_word_lower, indexed_word):
                        for doc_id in self.index[indexed_word]:
                            document_scores[doc_id] = document_scores.get(doc_id, 0) + 0.5
        
        # Filter by category and tags
        filtered_docs = []
        for doc in self.documents:
            if doc.id not in document_scores:
                continue
            
            # Apply filters
            if category and doc.category != category:
                continue
            
            if tags:
                if not any(tag in doc.tags for tag in tags):
                    continue
            
            filtered_docs.append({
                'document': doc,
                'score': document_scores[doc.id]
            })
        
        # Sort by relevance
        filtered_docs.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top results
        results = []
        for item in filtered_docs[:max_results]:
            doc = item['document']
            results.append({
                'id': doc.id,
                'title': doc.title,
                'category': doc.category,
                'tags': doc.tags,
                'score': item['score'],
                'snippet': self._generate_snippet(doc.content, query_words),
                'created_at': doc.created_at.isoformat(),
                'author': doc.author,
                'department': doc.department
            })
        
        return results
    
    def search_by_concept(self, concept: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Search documents by key concept.
        
        Args:
            concept: Concept to search for
            max_results: Maximum results to return
            
        Returns:
            List of matching documents
        """
        results = []
        concept_lower = concept.lower()
        
        for doc in self.documents:
            # Check if concept is in key concepts
            if any(concept_lower in kc.lower() for kc in doc.key_concepts):
                results.append({
                    'id': doc.id,
                    'title': doc.title,
                    'category': doc.category,
                    'tags': doc.tags,
                    'key_concepts': doc.key_concepts,
                    'created_at': doc.created_at.isoformat()
                })
        
        return results[:max_results]
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words.
        
        Args:
            text: Input text
            
        Returns:
            List of words
        """
        return re.findall(r'\b\w+\b', text.lower())
    
    def _fuzzy_match(self, word1: str, word2: str) -> bool:
        """
        Check if two words match within fuzzy distance.
        
        Args:
            word1: First word
            word2: Second word
            
        Returns:
            True if words match within fuzzy distance
        """
        # Simple fuzzy matching: check if word2 starts with word1 or vice versa
        if len(word1) < 3 or len(word2) < 3:
            return False
        
        return word1.startswith(word2[:3]) or word2.startswith(word1[:3])
    
    def _generate_snippet(self, content: str, query_words: List[str], snippet_length: int = 200) -> str:
        """
        Generate a snippet of content around query words.
        
        Args:
            content: Document content
            query_words: Query words to highlight
            snippet_length: Maximum snippet length
            
        Returns:
            Content snippet
        """
        # Find first occurrence of any query word
        content_lower = content.lower()
        first_pos = len(content)
        
        for word in query_words:
            pos = content_lower.find(word.lower())
            if pos != -1 and pos < first_pos:
                first_pos = pos
        
        if first_pos == len(content):
            # No match found, return beginning
            return content[:snippet_length] + "..."
        
        # Extract snippet around match
        start = max(0, first_pos - snippet_length // 2)
        end = min(len(content), start + snippet_length)
        snippet = content[start:end]
        
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."
        
        return snippet
