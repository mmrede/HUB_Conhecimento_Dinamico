"""
Knowledge Document Model
Modelo de Documento de Conhecimento

Defines the core knowledge document structure and metadata.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum


class DocumentType(Enum):
    """Types of knowledge documents."""
    POLICY = "policy"
    PROCEDURE = "procedure"
    REPORT = "report"
    REGULATION = "regulation"
    GUIDELINE = "guideline"
    ANALYSIS = "analysis"
    OTHER = "other"


class DocumentStatus(Enum):
    """Document processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


@dataclass
class KnowledgeDocument:
    """
    Represents a knowledge document in the system.
    Represents a knowledge document in the system.
    """
    
    # Core identification
    id: str
    title: str
    content: str
    
    # Classification
    document_type: DocumentType = DocumentType.OTHER
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    
    # Metadata
    source: str = ""
    author: str = ""
    department: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Processing
    status: DocumentStatus = DocumentStatus.PENDING
    confidence_score: float = 0.0
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Extracted knowledge
    key_concepts: List[str] = field(default_factory=list)
    entities: List[Dict[str, str]] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert document to dictionary representation.
        
        Returns:
            Dictionary representation of the document
        """
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'document_type': self.document_type.value,
            'category': self.category,
            'tags': self.tags,
            'source': self.source,
            'author': self.author,
            'department': self.department,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'status': self.status.value,
            'confidence_score': self.confidence_score,
            'metadata': self.metadata,
            'key_concepts': self.key_concepts,
            'entities': self.entities,
            'relationships': self.relationships
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeDocument':
        """
        Create document from dictionary representation.
        
        Args:
            data: Dictionary containing document data
            
        Returns:
            KnowledgeDocument instance
        """
        # Convert string enums back to enum types
        if 'document_type' in data and isinstance(data['document_type'], str):
            data['document_type'] = DocumentType(data['document_type'])
        
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = DocumentStatus(data['status'])
        
        # Convert ISO format strings back to datetime
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        return cls(**data)
    
    def add_tag(self, tag: str):
        """Add a tag to the document."""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def add_concept(self, concept: str):
        """Add a key concept to the document."""
        if concept not in self.key_concepts:
            self.key_concepts.append(concept)
    
    def add_entity(self, entity_type: str, entity_value: str):
        """Add an extracted entity to the document."""
        entity = {'type': entity_type, 'value': entity_value}
        if entity not in self.entities:
            self.entities.append(entity)
    
    def update_status(self, status: DocumentStatus):
        """Update document processing status."""
        self.status = status
        self.updated_at = datetime.now()
