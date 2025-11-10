"""
Knowledge Processing Engine
Motor de Processamento de Conhecimento

Extracts knowledge, entities, and insights from documents.
"""

import re
from typing import List, Dict, Any, Set, Tuple
from collections import Counter

from ..core.models import KnowledgeDocument, DocumentStatus


class KnowledgeProcessor:
    """
    Processes documents to extract knowledge, entities, and concepts.
    Processa documentos para extrair conhecimento, entidades e conceitos.
    """
    
    def __init__(self, language: str = 'pt', confidence_threshold: float = 0.7):
        """
        Initialize knowledge processor.
        
        Args:
            language: Language code for processing (pt for Portuguese)
            confidence_threshold: Minimum confidence for extracted knowledge
        """
        self.language = language
        self.confidence_threshold = confidence_threshold
        
        # Portuguese stopwords (common words to filter out)
        self.stopwords = self._get_stopwords()
        
        # Common entity patterns
        self.entity_patterns = self._get_entity_patterns()
    
    def process_document(self, document: KnowledgeDocument) -> KnowledgeDocument:
        """
        Process a document to extract knowledge.
        
        Args:
            document: KnowledgeDocument to process
            
        Returns:
            Processed KnowledgeDocument with extracted knowledge
        """
        document.update_status(DocumentStatus.PROCESSING)
        
        try:
            # Extract key concepts
            document.key_concepts = self._extract_key_concepts(document.content)
            
            # Extract entities
            entities = self._extract_entities(document.content)
            for entity_type, entity_value in entities:
                document.add_entity(entity_type, entity_value)
            
            # Auto-generate tags from content
            auto_tags = self._generate_tags(document.content, document.key_concepts)
            for tag in auto_tags:
                document.add_tag(tag)
            
            # Calculate confidence score
            document.confidence_score = self._calculate_confidence(document)
            
            # Update status
            document.update_status(DocumentStatus.PROCESSED)
            
        except Exception as e:
            document.update_status(DocumentStatus.FAILED)
            document.metadata['error'] = str(e)
        
        return document
    
    def _extract_key_concepts(self, text: str, max_concepts: int = 10) -> List[str]:
        """
        Extract key concepts from text using term frequency.
        
        Args:
            text: Input text
            max_concepts: Maximum number of concepts to extract
            
        Returns:
            List of key concepts
        """
        # Tokenize and clean
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter stopwords and short words
        filtered_words = [
            word for word in words 
            if word not in self.stopwords and len(word) > 3
        ]
        
        # Count frequencies
        word_freq = Counter(filtered_words)
        
        # Get top concepts
        top_concepts = [word for word, _ in word_freq.most_common(max_concepts)]
        
        return top_concepts
    
    def _extract_entities(self, text: str) -> List[Tuple[str, str]]:
        """
        Extract named entities from text.
        
        Args:
            text: Input text
            
        Returns:
            List of (entity_type, entity_value) tuples
        """
        entities = []
        
        # Extract dates
        date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'
        for match in re.finditer(date_pattern, text):
            entities.append(('DATE', match.group()))
        
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        for match in re.finditer(email_pattern, text):
            entities.append(('EMAIL', match.group()))
        
        # Extract numbers (potential values, amounts)
        number_pattern = r'\b\d+[\.,]?\d*\b'
        for match in re.finditer(number_pattern, text):
            value = match.group()
            if len(value) > 2:  # Filter very short numbers
                entities.append(('NUMBER', value))
        
        # Extract potential organization names (capitalized words)
        org_pattern = r'\b[A-ZÀ-Ú][a-zà-ú]+(?:\s+[A-ZÀ-Ú][a-zà-ú]+){1,3}\b'
        for match in re.finditer(org_pattern, text):
            entities.append(('ORGANIZATION', match.group()))
        
        return entities
    
    def _generate_tags(self, text: str, key_concepts: List[str], max_tags: int = 10) -> List[str]:
        """
        Generate tags from text and key concepts.
        
        Args:
            text: Input text
            key_concepts: Extracted key concepts
            max_tags: Maximum number of tags to generate
            
        Returns:
            List of tags
        """
        tags = []
        
        # Use top key concepts as tags
        tags.extend(key_concepts[:max_tags])
        
        # Check for domain-specific keywords
        domain_keywords = {
            'administrativo': ['administrativo', 'administração', 'gestão'],
            'financeiro': ['financeiro', 'orçamento', 'custo', 'despesa'],
            'jurídico': ['legal', 'lei', 'regulamento', 'norma'],
            'recursos_humanos': ['rh', 'pessoal', 'funcionário', 'colaborador'],
            'tecnologia': ['sistema', 'tecnologia', 'software', 'digital'],
            'estratégia': ['estratégia', 'planejamento', 'objetivo', 'meta']
        }
        
        text_lower = text.lower()
        for tag, keywords in domain_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                if tag not in tags:
                    tags.append(tag)
        
        return tags[:max_tags]
    
    def _calculate_confidence(self, document: KnowledgeDocument) -> float:
        """
        Calculate confidence score for extracted knowledge.
        
        Args:
            document: KnowledgeDocument with extracted knowledge
            
        Returns:
            Confidence score between 0 and 1
        """
        score = 0.0
        
        # Base score from content length
        if len(document.content) > 100:
            score += 0.3
        
        # Score from key concepts
        if len(document.key_concepts) >= 5:
            score += 0.3
        elif len(document.key_concepts) >= 3:
            score += 0.2
        
        # Score from entities
        if len(document.entities) >= 5:
            score += 0.2
        elif len(document.entities) >= 2:
            score += 0.1
        
        # Score from tags
        if len(document.tags) >= 3:
            score += 0.2
        elif len(document.tags) >= 1:
            score += 0.1
        
        return min(score, 1.0)
    
    def _get_stopwords(self) -> Set[str]:
        """Get Portuguese stopwords."""
        return {
            'a', 'o', 'e', 'é', 'de', 'da', 'do', 'em', 'um', 'uma', 'os', 'as',
            'para', 'com', 'por', 'não', 'no', 'na', 'dos', 'das', 'ao', 'aos',
            'à', 'às', 'pelo', 'pela', 'pelos', 'pelas', 'este', 'esta', 'estes',
            'estas', 'esse', 'essa', 'esses', 'essas', 'aquele', 'aquela',
            'aqueles', 'aquelas', 'que', 'qual', 'quais', 'quanto', 'quantos',
            'quanta', 'quantas', 'como', 'quando', 'onde', 'se', 'mas', 'mais',
            'menos', 'ainda', 'já', 'também', 'sim', 'só', 'ou', 'nem', 'apenas',
            'sobre', 'entre', 'sem', 'até', 'foi', 'ser', 'ter', 'estar', 'fazer'
        }
    
    def _get_entity_patterns(self) -> Dict[str, str]:
        """Get regex patterns for entity extraction."""
        return {
            'DATE': r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'NUMBER': r'\b\d+[\.,]?\d*\b',
            'ORGANIZATION': r'\b[A-ZÀ-Ú][a-zà-ú]+(?:\s+[A-ZÀ-Ú][a-zà-ú]+){1,3}\b'
        }
