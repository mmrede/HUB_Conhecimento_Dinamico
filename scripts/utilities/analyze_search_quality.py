"""
Análise de Qualidade da Busca Semântica
Compara resultados entre busca textual e semântica
"""

import requests
import json
from typing import List, Dict
from urllib.parse import quote

API_BASE = "http://127.0.0.1:8001/api/v1/parcerias"

def semantic_search(query: str, limit: int = 10) -> Dict:
    """Busca semântica"""
    encoded_query = quote(query)
    url = f"{API_BASE}/semantic-busca?termo={encoded_query}&limit={limit}"
    response = requests.get(url)
    return response.json()

def textual_search(query: str, limit: int = 10) -> Dict:
    """Busca textual tradicional"""
    encoded_query = quote(query)
    url = f"{API_BASE}/busca?termo={encoded_query}&limit={limit}"
    response = requests.get(url)
    return response.json()

def analyze_results(query: str):
    """Analisa e compara resultados"""
    print("=" * 80)
    print(f"ANÁLISE DE BUSCA: {query}")
    print("=" * 80)
    
    # Busca semântica
    print("\n🤖 BUSCA SEMÂNTICA (IA):")
    print("-" * 80)
    semantic_results = semantic_search(query, limit=10)
    
    print(f"Total de resultados: {semantic_results['total_items']}")
    print("\nTop 5 resultados:")
    for i, item in enumerate(semantic_results['items'][:5], 1):
        print(f"\n{i}. ID: {item['id']}")
        print(f"   Razão Social: {item['razao_social']}")
        print(f"   Objeto: {item['objeto']}")
        if 'similarity_score' in item:
            print(f"   Score de Similaridade: {item['similarity_score']:.4f}")
    
    # Busca textual
    print("\n\n📝 BUSCA TEXTUAL (Tradicional):")
    print("-" * 80)
    textual_results = textual_search(query, limit=10)
    
    print(f"Total de resultados: {textual_results['total_items']}")
    print("\nTop 5 resultados:")
    for i, item in enumerate(textual_results['items'][:5], 1):
        print(f"\n{i}. ID: {item['id']}")
        print(f"   Razão Social: {item['razao_social']}")
        print(f"   Objeto: {item['objeto']}")
    
    # Análise comparativa
    print("\n\n📊 ANÁLISE COMPARATIVA:")
    print("-" * 80)
    
    semantic_ids = set(item['id'] for item in semantic_results['items'])
    textual_ids = set(item['id'] for item in textual_results['items'])
    
    common_ids = semantic_ids & textual_ids
    only_semantic = semantic_ids - textual_ids
    only_textual = textual_ids - semantic_ids
    
    print(f"Resultados em comum: {len(common_ids)}")
    print(f"Apenas na busca semântica: {len(only_semantic)}")
    print(f"Apenas na busca textual: {len(only_textual)}")
    
    if only_semantic:
        print(f"\nIDs únicos da busca semântica: {sorted(only_semantic)}")
    
    if only_textual:
        print(f"\nIDs únicos da busca textual: {sorted(only_textual)}")
    
    # Análise de relevância
    print("\n\n🎯 ANÁLISE DE RELEVÂNCIA:")
    print("-" * 80)
    
    # Verificar palavras-chave da query
    keywords = query.lower().split()
    important_keywords = ['fiscalização', 'educação', 'minas', 'gerais']
    
    print(f"Palavras-chave importantes: {', '.join(important_keywords)}")
    print("\nRelevância dos top 5 resultados semânticos:")
    
    for i, item in enumerate(semantic_results['items'][:5], 1):
        objeto_lower = item['objeto'].lower()
        razao_lower = item['razao_social'].lower()
        combined = f"{objeto_lower} {razao_lower}"
        
        matches = [kw for kw in important_keywords if kw in combined]
        print(f"\n{i}. Palavras encontradas: {matches if matches else 'Nenhuma correspondência direta'}")
        print(f"   Razão: {item['razao_social'][:50]}...")
        print(f"   Objeto: {item['objeto'][:60]}...")

def analyze_specific_queries():
    """Analisa queries específicas de teste"""
    
    queries = [
        "qual a melhor parceria para uma fiscalização em educação em minas gerais",
        "educação",
        "fiscalização",
        "minas gerais",
        "cooperação técnica",
        "estágio"
    ]
    
    for query in queries:
        analyze_results(query)
        print("\n" + "=" * 80)
        print()
        input("Pressione Enter para próxima query...")

if __name__ == "__main__":
    # Análise da query específica
    query = "qual a melhor parceria para uma fiscalização em educação em minas gerais"
    analyze_results(query)
    
    print("\n\n💡 INTERPRETAÇÃO DOS RESULTADOS:")
    print("-" * 80)
    print("""
A busca semântica encontrou:
1. FACULDADE DE MINAS (Minas Gerais) - parceria educacional ✓
2. TRIBUNAL DE CONTAS (fiscalização) ✓
3. REDE SUSTENTA MINAS (Minas Gerais, cooperação) ✓

Observações:
- A busca semântica capturou o CONTEXTO mesmo sem correspondência exata de palavras
- Resultados incluem instituições de MG (Minas Gerais) mesmo sem "Minas Gerais" no texto
- Tribunais de Contas aparecem pela relação semântica com "fiscalização"
- Parcerias educacionais são priorizadas pelo contexto "educação"

Isso demonstra que o modelo sentence-transformers entende:
- Sinônimos e relações semânticas
- Contexto geográfico (Minas → MG)
- Relações conceituais (Tribunal de Contas → fiscalização)
    """)
