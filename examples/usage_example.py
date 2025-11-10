"""
Exemplo de Uso do Hub de Conhecimento
Example Usage of Knowledge Hub

Este script demonstra como usar a API Python do Hub de Conhecimento.
This script demonstrates how to use the Knowledge Hub Python API.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from hub_conhecimento.core.models import KnowledgeDocument, DocumentType
from hub_conhecimento.data.ingestion import DocumentIngestion
from hub_conhecimento.processing.processor import KnowledgeProcessor
from hub_conhecimento.search.engine import KnowledgeSearch
from hub_conhecimento.analytics.insights import KnowledgeAnalytics


def main():
    """Exemplo principal de uso."""
    
    print("=" * 60)
    print("Hub de Conhecimento Dinâmico - Exemplo de Uso")
    print("Dynamic Knowledge Hub - Usage Example")
    print("=" * 60)
    print()
    
    # 1. Criar documento manualmente
    print("1. Criando documento manualmente...")
    document1 = KnowledgeDocument(
        id="doc001",
        title="Política de Gestão de Documentos",
        content="""
        Esta política estabelece diretrizes para gestão eficiente de documentos
        na organização pública. Inclui procedimentos para criação, classificação,
        armazenamento, acesso e descarte de documentos institucionais.
        
        Palavras-chave: gestão, documentos, política, organização, pública
        """,
        category="administrative",
        tags=["gestão", "documentos", "política"],
        author="João Silva",
        department="Administração"
    )
    print(f"✓ Documento criado: {document1.title}")
    print()
    
    # 2. Processar documento
    print("2. Processando documento para extrair conhecimento...")
    processor = KnowledgeProcessor(language='pt', confidence_threshold=0.7)
    processed_doc = processor.process_document(document1)
    
    print(f"✓ Status: {processed_doc.status.value}")
    print(f"✓ Confiança: {processed_doc.confidence_score:.2f}")
    print(f"✓ Conceitos-chave: {', '.join(processed_doc.key_concepts[:5])}")
    print(f"✓ Tags geradas: {', '.join(processed_doc.tags)}")
    print(f"✓ Entidades extraídas: {len(processed_doc.entities)}")
    print()
    
    # 3. Criar mais documentos para exemplo
    print("3. Criando documentos adicionais...")
    documents = []
    
    doc2 = KnowledgeDocument(
        id="doc002",
        title="Manual de Procedimentos Operacionais",
        content="""
        Manual completo de procedimentos para operações diárias.
        Inclui processos de atendimento, gestão de recursos e relatórios.
        """,
        category="operations",
        tags=["manual", "procedimentos", "operações"],
        author="Maria Santos",
        department="Operações"
    )
    documents.append(processor.process_document(doc2))
    
    doc3 = KnowledgeDocument(
        id="doc003",
        title="Planejamento Estratégico 2025",
        content="""
        Planejamento estratégico organizacional com metas e objetivos
        para o ano de 2025. Inclui análise SWOT e indicadores de desempenho.
        """,
        category="strategic_planning",
        tags=["planejamento", "estratégia", "2025"],
        author="Carlos Souza",
        department="Planejamento"
    )
    documents.append(processor.process_document(doc3))
    
    documents.append(processed_doc)
    print(f"✓ Total de documentos: {len(documents)}")
    print()
    
    # 4. Indexar documentos para busca
    print("4. Indexando documentos para busca...")
    search_engine = KnowledgeSearch(fuzzy_search=True)
    for doc in documents:
        search_engine.index_document(doc)
    print(f"✓ {len(documents)} documentos indexados")
    print()
    
    # 5. Realizar buscas
    print("5. Realizando buscas...")
    print()
    
    # Busca por texto
    print("   a) Busca por 'gestão':")
    results = search_engine.search("gestão", max_results=5)
    for i, result in enumerate(results, 1):
        print(f"      {i}. {result['title']} (score: {result['score']:.2f})")
    print()
    
    # Busca com filtro de categoria
    print("   b) Busca por 'procedimentos' na categoria 'operations':")
    results = search_engine.search("procedimentos", category="operations", max_results=5)
    for i, result in enumerate(results, 1):
        print(f"      {i}. {result['title']}")
    print()
    
    # Busca por conceito
    print("   c) Busca por conceito 'planejamento':")
    results = search_engine.search_by_concept("planejamento", max_results=5)
    for i, result in enumerate(results, 1):
        print(f"      {i}. {result['title']}")
    print()
    
    # 6. Gerar analytics e insights
    print("6. Gerando analytics e insights...")
    analytics = KnowledgeAnalytics()
    for doc in documents:
        analytics.add_document(doc)
    
    insights = analytics.generate_insights()
    
    print(f"✓ Total de documentos: {insights['total_documents']}")
    print(f"✓ Distribuição por categoria:")
    for category, count in insights['categories_distribution'].items():
        print(f"   - {category}: {count}")
    
    print(f"✓ Top 5 tags:")
    for tag_info in insights['top_tags'][:5]:
        print(f"   - {tag_info['tag']}: {tag_info['count']}")
    
    print(f"✓ Cobertura de conhecimento:")
    coverage = insights['knowledge_coverage']
    print(f"   - Categorias únicas: {coverage['unique_categories']}")
    print(f"   - Tags únicas: {coverage['unique_tags']}")
    print(f"   - Confiança média: {coverage['average_confidence_score']}")
    print(f"   - Score de cobertura: {coverage['coverage_score']}")
    
    print(f"✓ Recomendações:")
    for i, rec in enumerate(insights['recommendations'], 1):
        print(f"   {i}. {rec}")
    print()
    
    # 7. Demonstrar ingestão de arquivo
    print("7. Exemplo de ingestão de arquivo...")
    ingestion = DocumentIngestion()
    
    # Criar arquivo de exemplo se não existir
    example_file = "examples/example_document.txt"
    if os.path.exists(example_file):
        try:
            ingested_doc = ingestion.ingest_file(example_file)
            print(f"✓ Arquivo ingerido: {ingested_doc.title}")
            print(f"✓ Tamanho do conteúdo: {len(ingested_doc.content)} caracteres")
        except Exception as e:
            print(f"✗ Erro ao ingerir arquivo: {e}")
    else:
        print(f"   (Arquivo de exemplo não encontrado: {example_file})")
    print()
    
    print("=" * 60)
    print("Exemplo concluído com sucesso!")
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == '__main__':
    main()
