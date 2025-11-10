"""
Data Ingestion Module
Módulo de Ingestão de Dados

Handles ingestion of various document formats into the knowledge hub.
"""

import hashlib
import os
from typing import List, Optional, BinaryIO
from pathlib import Path

from ..core.models import KnowledgeDocument, DocumentType, DocumentStatus


class DocumentIngestion:
    """Handles document ingestion and initial processing."""
    
    def __init__(self, supported_formats: Optional[List[str]] = None):
        """
        Initialize document ingestion.
        
        Args:
            supported_formats: List of supported file extensions
        """
        self.supported_formats = supported_formats or ['txt', 'pdf', 'docx', 'csv', 'json', 'xml']
    
    def ingest_file(self, file_path: str, metadata: Optional[dict] = None) -> KnowledgeDocument:
        """
        Ingest a single file into the knowledge hub.
        
        Args:
            file_path: Path to the file to ingest
            metadata: Optional metadata dictionary
            
        Returns:
            KnowledgeDocument instance
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is not supported
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Check file extension
        file_ext = Path(file_path).suffix[1:].lower()
        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        # Generate document ID from file hash
        doc_id = self._generate_document_id(file_path)
        
        # Extract content based on file type
        content = self._extract_content(file_path, file_ext)
        
        # Create document
        title = metadata.get('title', Path(file_path).stem) if metadata else Path(file_path).stem
        
        document = KnowledgeDocument(
            id=doc_id,
            title=title,
            content=content,
            source=file_path,
            status=DocumentStatus.PENDING
        )
        
        # Apply metadata if provided
        if metadata:
            if 'category' in metadata:
                document.category = metadata['category']
            if 'author' in metadata:
                document.author = metadata['author']
            if 'department' in metadata:
                document.department = metadata['department']
            if 'tags' in metadata:
                document.tags = metadata['tags']
            if 'document_type' in metadata:
                document.document_type = DocumentType(metadata['document_type'])
        
        return document
    
    def ingest_directory(self, directory_path: str, recursive: bool = True) -> List[KnowledgeDocument]:
        """
        Ingest all supported files from a directory.
        
        Args:
            directory_path: Path to the directory
            recursive: Whether to search recursively
            
        Returns:
            List of KnowledgeDocument instances
        """
        documents = []
        
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        # Walk through directory
        if recursive:
            for root, _, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        doc = self.ingest_file(file_path)
                        documents.append(doc)
                    except (ValueError, Exception):
                        # Skip unsupported or problematic files
                        continue
        else:
            for file in os.listdir(directory_path):
                file_path = os.path.join(directory_path, file)
                if os.path.isfile(file_path):
                    try:
                        doc = self.ingest_file(file_path)
                        documents.append(doc)
                    except (ValueError, Exception):
                        continue
        
        return documents
    
    def _generate_document_id(self, file_path: str) -> str:
        """
        Generate unique document ID based on file content hash.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Hexadecimal hash string
        """
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _extract_content(self, file_path: str, file_ext: str) -> str:
        """
        Extract text content from file based on its type.
        
        Args:
            file_path: Path to the file
            file_ext: File extension
            
        Returns:
            Extracted text content
        """
        if file_ext == 'txt':
            return self._extract_txt(file_path)
        elif file_ext == 'json':
            return self._extract_json(file_path)
        elif file_ext == 'csv':
            return self._extract_csv(file_path)
        else:
            # For other formats, basic text extraction
            # In production, use proper libraries (PyPDF2, python-docx, etc.)
            return self._extract_txt(file_path)
    
    def _extract_txt(self, file_path: str) -> str:
        """Extract content from text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with latin-1 encoding as fallback
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
    
    def _extract_json(self, file_path: str) -> str:
        """Extract content from JSON file."""
        import json
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return json.dumps(data, indent=2, ensure_ascii=False)
    
    def _extract_csv(self, file_path: str) -> str:
        """Extract content from CSV file."""
        import csv
        content_lines = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                content_lines.append(', '.join(row))
        return '\n'.join(content_lines)
