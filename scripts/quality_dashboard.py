"""
Dashboard de Métricas de Qualidade da Busca Semântica
Gera relatórios HTML interativos com análises detalhadas
"""

import requests
import json
from typing import List, Dict
from urllib.parse import quote
from datetime import datetime
import statistics

API_BASE = "http://127.0.0.1:8001/api/v1/parcerias"

# Queries de teste para análise de qualidade
TEST_QUERIES = [
    {
        "query": "qual a melhor parceria para uma fiscalização em educação em minas gerais",
        "keywords": ["fiscalização", "educação", "minas", "gerais"],
        "expected_concepts": ["Tribunal de Contas", "educação", "Minas Gerais"]
    },
    {
        "query": "cooperação técnica com universidades",
        "keywords": ["cooperação", "técnica", "universidade"],
        "expected_concepts": ["universidade", "cooperação", "ensino"]
    },
    {
        "query": "estágio em belo horizonte",
        "keywords": ["estágio", "belo horizonte"],
        "expected_concepts": ["estágio", "Minas", "BH"]
    },
    {
        "query": "tecnologia da informação",
        "keywords": ["tecnologia", "informação"],
        "expected_concepts": ["TI", "sistema", "software"]
    },
    {
        "query": "controle social e transparência",
        "keywords": ["controle", "social", "transparência"],
        "expected_concepts": ["auditoria", "participação", "cidadão"]
    }
]

def semantic_search(query: str, limit: int = 10) -> Dict:
    """Busca semântica com timing"""
    import time
    encoded_query = quote(query)
    url = f"{API_BASE}/semantic-busca?termo={encoded_query}&limit={limit}"
    
    try:
        start = time.time()
        response = requests.get(url, timeout=10)
        elapsed = time.time() - start
        
        if response.status_code != 200:
            print(f"  ⚠️ Erro HTTP {response.status_code}: {response.text[:200]}")
            return {'items': [], 'total_items': 0, 'response_time_ms': round(elapsed * 1000, 2)}
        
        data = response.json()
        data['response_time_ms'] = round(elapsed * 1000, 2)
        
        # Garantir estrutura esperada
        if 'items' not in data:
            print(f"  ⚠️ Resposta sem 'items'. Keys disponíveis: {list(data.keys())}")
            data['items'] = []
        if 'total_items' not in data:
            data['total_items'] = len(data.get('items', []))
        
        return data
        
    except Exception as e:
        print(f"  ❌ Erro na busca semântica: {e}")
        return {'items': [], 'total_items': 0, 'response_time_ms': 0}

def textual_search(query: str, limit: int = 10) -> Dict:
    """Busca textual com timing"""
    import time
    encoded_query = quote(query)
    url = f"{API_BASE}/busca?termo={encoded_query}&limit={limit}"
    
    start = time.time()
    response = requests.get(url)
    elapsed = time.time() - start
    
    data = response.json()
    data['response_time_ms'] = round(elapsed * 1000, 2)
    return data

def analyze_result_relevance(item: Dict, keywords: List[str]) -> Dict:
    """Analisa relevância de um resultado"""
    objeto = item.get('objeto', '').lower()
    razao = item.get('razao_social', '').lower()
    combined = f"{objeto} {razao}"
    
    matched_keywords = [kw for kw in keywords if kw.lower() in combined]
    relevance_score = len(matched_keywords) / len(keywords) if keywords else 0
    
    return {
        'matched_keywords': matched_keywords,
        'relevance_score': relevance_score,
        'has_similarity_score': 'similarity_score' in item,
        'similarity_score': item.get('similarity_score', 0)
    }

def generate_html_dashboard(results: List[Dict]) -> str:
    """Gera dashboard HTML interativo"""
    
    # Calcular métricas agregadas
    total_queries = len(results)
    semantic_wins = sum(1 for r in results if r['semantic_results']['total_items'] > r['textual_results']['total_items'])
    textual_wins = sum(1 for r in results if r['textual_results']['total_items'] > r['semantic_results']['total_items'])
    ties = total_queries - semantic_wins - textual_wins
    
    avg_semantic_time = statistics.mean([r['semantic_results']['response_time_ms'] for r in results])
    avg_textual_time = statistics.mean([r['textual_results']['response_time_ms'] for r in results])
    
    avg_relevance = statistics.mean([
        r['semantic_analysis']['avg_relevance'] for r in results 
        if r['semantic_analysis']['avg_relevance'] > 0
    ]) if any(r['semantic_analysis']['avg_relevance'] > 0 for r in results) else 0
    
    html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard de Qualidade - Busca Semântica</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #667eea;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}
        .timestamp {{
            color: #666;
            margin-bottom: 30px;
            font-size: 0.9em;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }}
        .metric-value {{
            font-size: 3em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .metric-label {{
            font-size: 0.9em;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .comparison-chart {{
            margin: 40px 0;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 15px;
        }}
        .chart-title {{
            font-size: 1.5em;
            margin-bottom: 20px;
            color: #667eea;
        }}
        .bar-container {{
            margin: 15px 0;
        }}
        .bar-label {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-weight: 500;
        }}
        .bar {{
            height: 30px;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            transition: all 0.3s ease;
            position: relative;
        }}
        .bar:hover {{
            transform: scaleX(1.02);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}
        .bar-value {{
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            color: white;
            font-weight: bold;
            font-size: 0.9em;
        }}
        .query-results {{
            margin: 40px 0;
        }}
        .query-card {{
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
            transition: all 0.3s ease;
        }}
        .query-card:hover {{
            border-color: #667eea;
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.2);
        }}
        .query-text {{
            font-size: 1.2em;
            color: #667eea;
            margin-bottom: 15px;
            font-weight: 500;
        }}
        .result-comparison {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }}
        .result-column {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
        }}
        .result-column h4 {{
            margin-bottom: 15px;
            color: #333;
        }}
        .result-item {{
            background: white;
            padding: 12px;
            margin: 8px 0;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .score-badge {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: bold;
            margin-left: 10px;
        }}
        .status-good {{ background: #10b981; }}
        .status-medium {{ background: #f59e0b; }}
        .status-bad {{ background: #ef4444; }}
        .footer {{
            margin-top: 60px;
            text-align: center;
            color: #666;
            padding-top: 30px;
            border-top: 2px solid #e0e0e0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 Dashboard de Qualidade - Busca Semântica</h1>
        <div class="timestamp">Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Total de Queries</div>
                <div class="metric-value">{total_queries}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Vitórias Semânticas</div>
                <div class="metric-value">{semantic_wins}</div>
                <div style="opacity: 0.8; margin-top: 10px;">
                    {round(semantic_wins/total_queries*100)}% das queries
                </div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Tempo Médio (Semântica)</div>
                <div class="metric-value">{round(avg_semantic_time)}ms</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Relevância Média</div>
                <div class="metric-value">{round(avg_relevance*100)}%</div>
            </div>
        </div>
        
        <div class="comparison-chart">
            <div class="chart-title">⚡ Performance Comparativa</div>
            <div class="bar-container">
                <div class="bar-label">
                    <span>🤖 Busca Semântica (IA)</span>
                    <span>{round(avg_semantic_time, 1)}ms</span>
                </div>
                <div class="bar" style="width: {min(avg_semantic_time/max(avg_semantic_time, avg_textual_time, 1)*100, 100)}%">
                    <span class="bar-value">{round(avg_semantic_time, 1)}ms</span>
                </div>
            </div>
            <div class="bar-container">
                <div class="bar-label">
                    <span>📝 Busca Textual</span>
                    <span>{round(avg_textual_time, 1)}ms</span>
                </div>
                <div class="bar" style="width: {min(avg_textual_time/max(avg_semantic_time, avg_textual_time, 1)*100, 100)}%; background: linear-gradient(90deg, #64748b 0%, #475569 100%);">
                    <span class="bar-value">{round(avg_textual_time, 1)}ms</span>
                </div>
            </div>
        </div>
        
        <div class="query-results">
            <h2 style="color: #667eea; margin-bottom: 20px;">📊 Análise Detalhada por Query</h2>
    """
    
    # Adicionar resultados de cada query
    for i, result in enumerate(results, 1):
        query_data = result['query_data']
        semantic = result['semantic_results']
        textual = result['textual_results']
        analysis = result['semantic_analysis']
        
        winner = "🤖 Semântica" if semantic['total_items'] > textual['total_items'] else ("📝 Textual" if textual['total_items'] > semantic['total_items'] else "🤝 Empate")
        
        html += f"""
            <div class="query-card">
                <div class="query-text">Query {i}: "{query_data['query']}"</div>
                <div style="margin: 15px 0;">
                    <strong>Vencedor:</strong> {winner} 
                    <span class="score-badge">Semântica: {semantic['total_items']} resultados</span>
                    <span class="score-badge" style="background: #64748b;">Textual: {textual['total_items']} resultados</span>
                </div>
                
                <div class="result-comparison">
                    <div class="result-column">
                        <h4>🤖 Top 3 Semânticos (Score)</h4>
        """
        
        for j, item in enumerate(semantic['items'][:3], 1):
            score = item.get('similarity_score', 0)
            score_class = 'status-good' if score > 0.7 else ('status-medium' if score > 0.4 else 'status-bad')
            html += f"""
                        <div class="result-item">
                            <div><strong>{j}.</strong> {item.get('razao_social', 'N/A')[:50]}...</div>
                            <div style="font-size: 0.9em; color: #666; margin-top: 5px;">
                                {item.get('objeto', '')[:80]}...
                                <span class="score-badge {score_class}">{score:.3f}</span>
                            </div>
                        </div>
            """
        
        html += """
                    </div>
                    <div class="result-column">
                        <h4>📝 Top 3 Textuais</h4>
        """
        
        if textual['total_items'] > 0:
            for j, item in enumerate(textual['items'][:3], 1):
                html += f"""
                        <div class="result-item">
                            <div><strong>{j}.</strong> {item.get('razao_social', 'N/A')[:50]}...</div>
                            <div style="font-size: 0.9em; color: #666; margin-top: 5px;">
                                {item.get('objeto', '')[:80]}...
                            </div>
                        </div>
                """
        else:
            html += '<div style="color: #999; font-style: italic;">Nenhum resultado encontrado</div>'
        
        html += f"""
                    </div>
                </div>
                
                <div style="margin-top: 20px; padding: 15px; background: #f0f4ff; border-radius: 10px;">
                    <strong>📈 Métricas:</strong><br>
                    Relevância Média: <span class="score-badge">{round(analysis['avg_relevance']*100)}%</span>
                    Tempo de Resposta: <span class="score-badge">{semantic['response_time_ms']}ms</span>
                    Palavras-chave Encontradas: <span class="score-badge">{analysis['total_keyword_matches']}</span>
                </div>
            </div>
        """
    
    html += """
        </div>
        
        <div class="footer">
            <p><strong>Hub Aura - Sistema de Busca Semântica</strong></p>
            <p>Modelo: sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2)</p>
            <p>384 dimensões • PostgreSQL 15 • 276 embeddings</p>
        </div>
    </div>
</body>
</html>
    """
    
    return html

def run_quality_analysis():
    """Executa análise completa de qualidade"""
    print("🚀 Iniciando análise de qualidade da busca semântica...")
    print("=" * 80)
    
    results = []
    
    for i, test in enumerate(TEST_QUERIES, 1):
        print(f"\n📝 Query {i}/{len(TEST_QUERIES)}: {test['query'][:60]}...")
        
        # Executar buscas
        semantic = semantic_search(test['query'])
        textual = textual_search(test['query'])
        
        # Verificar se há items na resposta
        if 'items' not in semantic:
            print(f"  ⚠️ Resposta semântica sem campo 'items': {semantic}")
            semantic['items'] = []
        if 'items' not in textual:
            textual['items'] = []
        
        # Análise de relevância
        relevance_scores = []
        total_keywords_matched = 0
        
        for item in semantic.get('items', [])[:5]:
            analysis = analyze_result_relevance(item, test['keywords'])
            relevance_scores.append(analysis['relevance_score'])
            total_keywords_matched += len(analysis['matched_keywords'])
        
        avg_relevance = statistics.mean(relevance_scores) if relevance_scores else 0
        
        result = {
            'query_data': test,
            'semantic_results': semantic,
            'textual_results': textual,
            'semantic_analysis': {
                'avg_relevance': avg_relevance,
                'total_keyword_matches': total_keywords_matched
            }
        }
        
        results.append(result)
        
        print(f"  ✅ Semântica: {semantic['total_items']} resultados em {semantic['response_time_ms']}ms")
        print(f"  ✅ Textual: {textual['total_items']} resultados em {textual['response_time_ms']}ms")
        print(f"  ✅ Relevância média: {round(avg_relevance*100)}%")
    
    print("\n" + "=" * 80)
    print("📊 Gerando dashboard HTML...")
    
    # Gerar HTML
    html = generate_html_dashboard(results)
    
    # Salvar arquivo
    output_file = "c:/Users/manoe/hub_aura/quality_dashboard.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Dashboard salvo em: {output_file}")
    print("\n🎯 Resumo Geral:")
    print(f"  • Total de queries testadas: {len(results)}")
    print(f"  • Semântica venceu: {sum(1 for r in results if r['semantic_results']['total_items'] > r['textual_results']['total_items'])} vezes")
    print(f"  • Tempo médio semântica: {statistics.mean([r['semantic_results']['response_time_ms'] for r in results]):.1f}ms")
    
    return output_file

if __name__ == "__main__":
    dashboard_file = run_quality_analysis()
    print(f"\n🌐 Abra o dashboard em seu navegador:")
    print(f"   file:///{dashboard_file}")
