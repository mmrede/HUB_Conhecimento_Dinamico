"""
Knowledge Hub API
API do Hub de Conhecimento

REST API for accessing and managing knowledge documents.
"""

from flask import Flask, request, jsonify
from typing import Dict, Any

from ..core.config import get_config
from ..core.models import KnowledgeDocument, DocumentType
from ..data.ingestion import DocumentIngestion
from ..processing.processor import KnowledgeProcessor
from ..search.engine import KnowledgeSearch
from ..analytics.insights import KnowledgeAnalytics


class KnowledgeHubAPI:
    """
    Flask-based REST API for Knowledge Hub.
    API REST baseada em Flask para o Hub de Conhecimento.
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize API.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = get_config(config_path)
        self.app = Flask(__name__)
        
        # Initialize components
        self.ingestion = DocumentIngestion(
            supported_formats=self.config.get('processing.supported_formats')
        )
        self.processor = KnowledgeProcessor(
            language=self.config.get('processing.language'),
            confidence_threshold=self.config.get('processing.confidence_threshold')
        )
        self.search = KnowledgeSearch(
            fuzzy_search=self.config.get('search.fuzzy_search'),
            fuzzy_distance=self.config.get('search.fuzzy_distance')
        )
        self.analytics = KnowledgeAnalytics()
        
        # Setup routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes."""
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint."""
            return jsonify({'status': 'healthy', 'version': '1.0.0'})
        
        @self.app.route('/api/documents', methods=['POST'])
        def ingest_document():
            """Ingest a new document."""
            data = request.get_json()
            
            if 'content' not in data or 'title' not in data:
                return jsonify({'error': 'Missing required fields: content, title'}), 400
            
            # Create document
            import hashlib
            doc_id = hashlib.md5(data['content'].encode()).hexdigest()
            
            document = KnowledgeDocument(
                id=doc_id,
                title=data['title'],
                content=data['content']
            )
            
            # Apply metadata
            if 'category' in data:
                document.category = data['category']
            if 'tags' in data:
                document.tags = data['tags']
            if 'author' in data:
                document.author = data['author']
            if 'department' in data:
                document.department = data['department']
            
            # Process document
            document = self.processor.process_document(document)
            
            # Index for search
            self.search.index_document(document)
            
            # Add to analytics
            self.analytics.add_document(document)
            
            return jsonify({
                'message': 'Document ingested successfully',
                'document_id': document.id,
                'status': document.status.value,
                'confidence_score': document.confidence_score
            }), 201
        
        @self.app.route('/api/search', methods=['GET'])
        def search_documents():
            """Search for documents."""
            query = request.args.get('q', '')
            category = request.args.get('category')
            tags = request.args.getlist('tag')
            max_results = int(request.args.get('max_results', 20))
            
            if not query:
                return jsonify({'error': 'Query parameter "q" is required'}), 400
            
            results = self.search.search(
                query=query,
                category=category,
                tags=tags if tags else None,
                max_results=max_results
            )
            
            return jsonify({
                'query': query,
                'total_results': len(results),
                'results': results
            })
        
        @self.app.route('/api/search/concepts', methods=['GET'])
        def search_by_concept():
            """Search documents by concept."""
            concept = request.args.get('concept', '')
            max_results = int(request.args.get('max_results', 20))
            
            if not concept:
                return jsonify({'error': 'Parameter "concept" is required'}), 400
            
            results = self.search.search_by_concept(concept, max_results)
            
            return jsonify({
                'concept': concept,
                'total_results': len(results),
                'results': results
            })
        
        @self.app.route('/api/analytics/insights', methods=['GET'])
        def get_insights():
            """Get analytics insights."""
            insights = self.analytics.generate_insights()
            return jsonify(insights)
        
        @self.app.route('/api/categories', methods=['GET'])
        def get_categories():
            """Get available categories."""
            categories = self.config.get('categorization.categories', [])
            return jsonify({'categories': categories})
        
        @self.app.route('/api/documents/<doc_id>', methods=['GET'])
        def get_document(doc_id):
            """Get a specific document."""
            # Find document
            for doc in self.search.documents:
                if doc.id == doc_id:
                    return jsonify(doc.to_dict())
            
            return jsonify({'error': 'Document not found'}), 404
    
    def run(self, host: str = None, port: int = None, debug: bool = None):
        """
        Run the API server.
        
        Args:
            host: Host to bind to
            port: Port to bind to
            debug: Enable debug mode
        """
        api_config = self.config.get('api', {})
        
        host = host or api_config.get('host', '0.0.0.0')
        port = port or api_config.get('port', 5000)
        debug = debug if debug is not None else api_config.get('debug', False)
        
        self.app.run(host=host, port=port, debug=debug)


def create_app(config_path: str = "config.yaml") -> Flask:
    """
    Create and configure Flask application.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configured Flask application
    """
    api = KnowledgeHubAPI(config_path)
    return api.app
