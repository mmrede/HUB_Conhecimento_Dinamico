#!/usr/bin/env python3
"""
Knowledge Hub CLI
Interface de Linha de Comando do Hub de Conhecimento

Command-line interface for managing the Knowledge Hub.
"""

import argparse
import sys
import os
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from hub_conhecimento.core.config import get_config
from hub_conhecimento.data.ingestion import DocumentIngestion
from hub_conhecimento.processing.processor import KnowledgeProcessor
from hub_conhecimento.search.engine import KnowledgeSearch
from hub_conhecimento.analytics.insights import KnowledgeAnalytics


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Hub de Conhecimento Dinâmico - Dynamic Knowledge Hub'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Ingest command
    ingest_parser = subparsers.add_parser('ingest', help='Ingest documents')
    ingest_parser.add_argument('path', help='File or directory path to ingest')
    ingest_parser.add_argument('--recursive', action='store_true', help='Recursively scan directories')
    ingest_parser.add_argument('--category', help='Category for documents')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search documents')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--category', help='Filter by category')
    search_parser.add_argument('--max-results', type=int, default=10, help='Maximum results')
    
    # Analytics command
    analytics_parser = subparsers.add_parser('analytics', help='Generate analytics')
    analytics_parser.add_argument('--output', help='Output file for analytics JSON')
    
    # API server command
    api_parser = subparsers.add_parser('serve', help='Start API server')
    api_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    api_parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    api_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Load configuration
    config_path = os.environ.get('CONFIG_PATH', 'config.yaml')
    
    try:
        if args.command == 'ingest':
            handle_ingest(args, config_path)
        elif args.command == 'search':
            handle_search(args, config_path)
        elif args.command == 'analytics':
            handle_analytics(args, config_path)
        elif args.command == 'serve':
            handle_serve(args, config_path)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_ingest(args, config_path):
    """Handle document ingestion."""
    config = get_config(config_path)
    
    ingestion = DocumentIngestion(
        supported_formats=config.get('processing.supported_formats')
    )
    processor = KnowledgeProcessor(
        language=config.get('processing.language'),
        confidence_threshold=config.get('processing.confidence_threshold')
    )
    
    print(f"Ingesting from: {args.path}")
    
    # Ingest documents
    if os.path.isfile(args.path):
        metadata = {'category': args.category} if args.category else None
        document = ingestion.ingest_file(args.path, metadata)
        documents = [document]
    else:
        documents = ingestion.ingest_directory(args.path, recursive=args.recursive)
    
    print(f"Found {len(documents)} documents")
    
    # Process documents
    processed = 0
    for doc in documents:
        processor.process_document(doc)
        if doc.status.value == 'processed':
            processed += 1
            print(f"✓ Processed: {doc.title} (confidence: {doc.confidence_score:.2f})")
        else:
            print(f"✗ Failed: {doc.title}")
    
    print(f"\nSuccessfully processed {processed}/{len(documents)} documents")


def handle_search(args, config_path):
    """Handle search command."""
    # For demo purposes, create some sample data
    print(f"Searching for: {args.query}")
    print(f"Category filter: {args.category or 'None'}")
    print(f"\nNote: This is a demo. Connect to actual data store for production use.")
    print("\nExample results would appear here based on indexed documents.")


def handle_analytics(args, config_path):
    """Handle analytics command."""
    analytics = KnowledgeAnalytics()
    
    # For demo purposes
    print("Generating analytics...")
    insights = analytics.generate_insights()
    
    output = json.dumps(insights, indent=2, ensure_ascii=False)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Analytics saved to: {args.output}")
    else:
        print(output)


def handle_serve(args, config_path):
    """Handle API server command."""
    print(f"Starting Knowledge Hub API server...")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Debug: {args.debug}")
    
    # Import here to avoid requiring Flask if not serving
    try:
        from hub_conhecimento.api.app import KnowledgeHubAPI
        api = KnowledgeHubAPI(config_path)
        api.run(host=args.host, port=args.port, debug=args.debug)
    except ImportError as e:
        print(f"Error: Flask is required to run the API server.")
        print(f"Install it with: pip install -r requirements.txt")
        sys.exit(1)


if __name__ == '__main__':
    main()
