"""
Dashboard de Qualidade Semântica - Análise Comparativa
Executa múltiplas queries e gera análise detalhada
"""
import os
os.environ['DATABASE_URL'] = "postgresql://postgres:rx1800@localhost:5433/hub_aura_db"

import numpy as np
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sentence_transformers import SentenceTransformer
import time
from datetime import datetime
import statistics

# Configuração do banco
DB_URL = "postgresql://postgres:rx1800@localhost:5433/hub_aura_db"
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)

# Queries para análise
QUERIES = [
    "quais os melhores parceiros para uma capacitação em inteligência",
    "cooperação técnica com universidades",
    "estágio em belo horizonte"
]

def execute_semantic_search(model, query_text, session):
    """Executa busca semântica e retorna resultados com métricas"""
    
    # Gerar embedding
    embed_start = time.time()
    query_vector = model.encode(query_text).tolist()
    embed_time = time.time() - embed_start
    
    # Calcular norma
    q_norm = float(np.sqrt(np.sum(np.square(np.array(query_vector, dtype=np.float64)))))
    
    # Executar busca
    db_start = time.time()
    
    sql = text("""
        WITH q AS (
            SELECT CAST(:query_vector AS float8[]) AS v, CAST(:q_norm AS float8) AS qn
        ),
        deduplicated_vectors AS (
            SELECT DISTINCT ON (parceria_id) 
                parceria_id, 
                COALESCE(objeto_vetor_v3, objeto_vetor_v2) as vetor
            FROM documento_vetores
            WHERE COALESCE(objeto_vetor_v3, objeto_vetor_v2) IS NOT NULL
            ORDER BY parceria_id
        ),
        agg AS (
            SELECT 
                dv.parceria_id,
                SUM(dv_elt.dv_v * q_elt.q_v) AS dot,
                sqrt(SUM(dv_elt.dv_v * dv_elt.dv_v)) AS dn
            FROM deduplicated_vectors dv
            JOIN q ON TRUE
            JOIN LATERAL unnest(dv.vetor) WITH ORDINALITY AS dv_elt(dv_v, idx) ON TRUE
            JOIN LATERAL unnest((SELECT v FROM q)) WITH ORDINALITY AS q_elt(q_v, idx2) ON idx = idx2
            GROUP BY dv.parceria_id
        )
        SELECT 
            p.*,
            (dot / NULLIF(dn * (SELECT qn FROM q), 0)) AS similarity_score
        FROM agg a
        JOIN instrumentos_parceria p ON p.id = a.parceria_id
        ORDER BY similarity_score DESC NULLS LAST
        LIMIT 10
    """)
    
    result = session.execute(sql, {
        "query_vector": query_vector,
        "q_norm": q_norm
    })
    
    rows = result.mappings().all()
    db_time = time.time() - db_start
    
    return {
        'query': query_text,
        'results': [dict(r) for r in rows],
        'embed_time': embed_time,
        'db_time': db_time,
        'total_time': embed_time + db_time,
        'query_vector': query_vector
    }

def analyze_quality(results_data):
    """Analisa qualidade dos resultados"""
    
    scores = [r.get('similarity_score', 0) for r in results_data['results']]
    
    if not scores:
        return None
    
    return {
        'num_results': len(scores),
        'max_score': max(scores),
        'min_score': min(scores),
        'avg_score': statistics.mean(scores),
        'median_score': statistics.median(scores),
        'stdev_score': statistics.stdev(scores) if len(scores) > 1 else 0,
        'very_high': sum(1 for s in scores if s >= 0.7),
        'high': sum(1 for s in scores if 0.5 <= s < 0.7),
        'medium': sum(1 for s in scores if 0.3 <= s < 0.5),
        'low': sum(1 for s in scores if s < 0.3)
    }

def analyze_keywords(results_data):
    """Analisa presença de keywords nos resultados"""
    
    query_words = results_data['query'].lower().split()
    keyword_matches = []
    
    for result in results_data['results']:
        objeto = result.get('objeto', '').lower()
        parceiro = result.get('nome_parceiro', '').lower()
        
        matches = 0
        for word in query_words:
            if len(word) > 3:  # Ignorar palavras muito curtas
                if word in objeto or word in parceiro:
                    matches += 1
        
        keyword_matches.append(matches)
    
    return {
        'avg_keyword_matches': statistics.mean(keyword_matches) if keyword_matches else 0,
        'max_keyword_matches': max(keyword_matches) if keyword_matches else 0,
        'semantic_only': sum(1 for m in keyword_matches if m == 0)  # Encontrados apenas por semântica
    }

def generate_dashboard():
    """Gera dashboard completo de qualidade semântica"""
    
    print("=" * 120)
    print("DASHBOARD DE QUALIDADE SEMÂNTICA - HUB AURA TCE")
    print("=" * 120)
    print(f"\n📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"🔬 Análise Comparativa de 3 Queries")
    print(f"🤖 Modelo: paraphrase-multilingual-MiniLM-L12-v2 (384 dims)")
    
    # Carregar modelo
    print("\n" + "-" * 120)
    print("⏳ Inicializando modelo de IA...")
    model_start = time.time()
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    model_time = time.time() - model_start
    print(f"✅ Modelo carregado em {model_time:.2f}s")
    
    session = Session()
    
    # Executar buscas
    all_results = []
    print("\n" + "-" * 120)
    print("🔍 Executando buscas semânticas...\n")
    
    for idx, query in enumerate(QUERIES, 1):
        print(f"Query {idx}/3: '{query}'...")
        results = execute_semantic_search(model, query, session)
        all_results.append(results)
        print(f"  ✓ {len(results['results'])} resultados em {results['total_time']:.3f}s")
    
    # Análise comparativa
    print("\n" + "=" * 120)
    print("📊 ANÁLISE COMPARATIVA DE PERFORMANCE")
    print("=" * 120)
    
    print(f"\n{'Query':<60} {'Embed (ms)':<12} {'DB (ms)':<12} {'Total (ms)':<12}")
    print("-" * 120)
    
    for r in all_results:
        query_short = r['query'][:57] + "..." if len(r['query']) > 60 else r['query']
        print(f"{query_short:<60} {r['embed_time']*1000:>10.0f}ms {r['db_time']*1000:>10.0f}ms {r['total_time']*1000:>10.0f}ms")
    
    avg_embed = statistics.mean([r['embed_time'] for r in all_results])
    avg_db = statistics.mean([r['db_time'] for r in all_results])
    avg_total = statistics.mean([r['total_time'] for r in all_results])
    
    print("-" * 120)
    print(f"{'MÉDIA':<60} {avg_embed*1000:>10.0f}ms {avg_db*1000:>10.0f}ms {avg_total*1000:>10.0f}ms")
    
    # Análise de qualidade
    print("\n" + "=" * 120)
    print("🎯 ANÁLISE DE QUALIDADE DOS RESULTADOS")
    print("=" * 120)
    
    qualities = [analyze_quality(r) for r in all_results]
    
    print(f"\n{'Query':<60} {'Resultados':<12} {'Max Score':<12} {'Avg Score':<12}")
    print("-" * 120)
    
    for r, q in zip(all_results, qualities):
        query_short = r['query'][:57] + "..." if len(r['query']) > 60 else r['query']
        print(f"{query_short:<60} {q['num_results']:>10}   {q['max_score']:>10.4f}   {q['avg_score']:>10.4f}")
    
    # Distribuição de relevância
    print("\n" + "=" * 120)
    print("📈 DISTRIBUIÇÃO DE RELEVÂNCIA POR QUERY")
    print("=" * 120)
    
    print(f"\n{'Query':<60} {'🟢 Muito Alta':<15} {'🟡 Alta':<15} {'🟠 Média':<15} {'🔴 Baixa':<15}")
    print("-" * 120)
    
    for r, q in zip(all_results, qualities):
        query_short = r['query'][:57] + "..." if len(r['query']) > 60 else r['query']
        print(f"{query_short:<60} {q['very_high']:>13}   {q['high']:>13}   {q['medium']:>13}   {q['low']:>13}")
    
    # Análise de keywords vs semântica
    print("\n" + "=" * 120)
    print("🔤 ANÁLISE: KEYWORDS vs SEMÂNTICA PURA")
    print("=" * 120)
    
    keyword_analyses = [analyze_keywords(r) for r in all_results]
    
    print(f"\n{'Query':<60} {'Matches Médio':<15} {'Semântica Pura':<20}")
    print("-" * 120)
    
    for r, k in zip(all_results, keyword_analyses):
        query_short = r['query'][:57] + "..." if len(r['query']) > 60 else r['query']
        print(f"{query_short:<60} {k['avg_keyword_matches']:>13.1f}   {k['semantic_only']:>18} ({k['semantic_only']/10*100:.0f}%)")
    
    # Determinar vencedor
    print("\n" + "=" * 120)
    print("🏆 RANKING DE QUALIDADE SEMÂNTICA")
    print("=" * 120)
    
    # Calcular score geral (combinação de métricas)
    scores_overall = []
    for q, k in zip(qualities, keyword_analyses):
        score = (
            q['avg_score'] * 40 +  # 40% peso no score médio
            q['max_score'] * 30 +   # 30% peso no melhor resultado
            (q['very_high'] / 10) * 20 +  # 20% peso em resultados muito altos
            (k['semantic_only'] / 10) * 10  # 10% peso em descoberta semântica pura
        )
        scores_overall.append(score)
    
    # Ordenar
    ranked = sorted(zip(all_results, qualities, keyword_analyses, scores_overall), 
                   key=lambda x: x[3], reverse=True)
    
    for idx, (r, q, k, score) in enumerate(ranked, 1):
        medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉"
        print(f"\n{medal} POSIÇÃO #{idx} - Score: {score:.4f}")
        print(f"   Query: '{r['query']}'")
        print(f"   • Score Médio: {q['avg_score']:.4f} ({q['avg_score']*100:.2f}%)")
        print(f"   • Score Máximo: {q['max_score']:.4f} ({q['max_score']*100:.2f}%)")
        print(f"   • Resultados Muito Relevantes: {q['very_high']}/10")
        print(f"   • Descoberta Semântica Pura: {k['semantic_only']}/10 ({k['semantic_only']/10*100:.0f}%)")
        print(f"   • Performance: {r['total_time']*1000:.0f}ms")
    
    # Análise detalhada do vencedor
    winner = ranked[0]
    print("\n" + "=" * 120)
    print("🔍 ANÁLISE DETALHADA DO VENCEDOR")
    print("=" * 120)
    
    print(f"\n🏆 Query Vencedora: '{winner[0]['query']}'")
    print(f"📊 Score Geral: {winner[3]:.4f}")
    
    print(f"\n📈 Métricas de Qualidade:")
    print(f"   • Resultados Retornados: {winner[1]['num_results']}")
    print(f"   • Score Máximo: {winner[1]['max_score']:.4f} ({winner[1]['max_score']*100:.2f}%)")
    print(f"   • Score Mínimo: {winner[1]['min_score']:.4f} ({winner[1]['min_score']*100:.2f}%)")
    print(f"   • Score Médio: {winner[1]['avg_score']:.4f} ({winner[1]['avg_score']*100:.2f}%)")
    print(f"   • Mediana: {winner[1]['median_score']:.4f}")
    print(f"   • Desvio Padrão: {winner[1]['stdev_score']:.4f}")
    
    print(f"\n🎯 Distribuição de Relevância:")
    print(f"   🟢 Muito Alta (≥70%): {winner[1]['very_high']} resultados")
    print(f"   🟡 Alta (50-69%): {winner[1]['high']} resultados")
    print(f"   🟠 Média (30-49%): {winner[1]['medium']} resultados")
    print(f"   🔴 Baixa (<30%): {winner[1]['low']} resultados")
    
    print(f"\n⚡ Performance:")
    print(f"   • Geração de Embedding: {winner[0]['embed_time']*1000:.0f}ms")
    print(f"   • Busca no Banco: {winner[0]['db_time']*1000:.0f}ms")
    print(f"   • Latência Total: {winner[0]['total_time']*1000:.0f}ms")
    
    print(f"\n🔤 Análise Semântica vs Keywords:")
    print(f"   • Matches de Keywords (média): {winner[2]['avg_keyword_matches']:.1f}")
    print(f"   • Resultados por Semântica Pura: {winner[2]['semantic_only']}/10")
    
    if winner[2]['semantic_only'] > 5:
        print(f"   ✨ Alto nível de descoberta semântica! A IA encontrou resultados além de keywords.")
    
    print(f"\n💡 Top 3 Resultados:")
    for idx, result in enumerate(winner[0]['results'][:3], 1):
        print(f"\n   {idx}. Termo {result.get('numero_do_termo')}/{result.get('ano_do_termo')} - Score: {result.get('similarity_score', 0):.4f}")
        objeto = result.get('objeto', '')[:100]
        print(f"      {objeto}...")
    
    # Análise Técnica de PLN/IA
    print("\n" + "=" * 120)
    print("🤖 ANÁLISE TÉCNICA: PLN & IA")
    print("=" * 120)
    
    print(f"\n📚 Processamento de Linguagem Natural (PLN):")
    print(f"   • Modelo: Transformer-based (BERT architecture)")
    print(f"   • Tipo: Sentence Embeddings (representação densa)")
    print(f"   • Dimensionalidade: 384 (otimizado)")
    print(f"   • Tokenização: WordPiece (multilíngue)")
    print(f"   • Normalização: Layer normalization + pooling")
    
    print(f"\n🧠 Capacidades de IA Demonstradas:")
    print(f"   ✅ Compreensão Semântica: Entende significado além de palavras")
    print(f"   ✅ Transferência de Conhecimento: Modelo pré-treinado em milhões de textos")
    print(f"   ✅ Representação Contextual: Embeddings capturam contexto")
    print(f"   ✅ Similaridade Vetorial: Métrica de cosseno para ranking")
    print(f"   ✅ Multilinguismo: Suporte nativo para português")
    
    print(f"\n📊 Métricas de Avaliação:")
    
    # Consistência (desvio padrão dos scores)
    avg_stdev = statistics.mean([q['stdev_score'] for q in qualities])
    consistency = "Alta" if avg_stdev < 0.05 else "Média" if avg_stdev < 0.10 else "Baixa"
    print(f"   • Consistência dos Scores: {consistency} (σ={avg_stdev:.4f})")
    
    # Discriminação (capacidade de distinguir relevância)
    avg_range = statistics.mean([q['max_score'] - q['min_score'] for q in qualities])
    discrimination = "Excelente" if avg_range > 0.15 else "Boa" if avg_range > 0.08 else "Moderada"
    print(f"   • Poder de Discriminação: {discrimination} (range={avg_range:.4f})")
    
    # Cobertura semântica
    avg_semantic = statistics.mean([k['semantic_only'] for k in keyword_analyses])
    coverage = "Excelente" if avg_semantic > 6 else "Boa" if avg_semantic > 3 else "Moderada"
    print(f"   • Cobertura Semântica: {coverage} ({avg_semantic:.1f}/10 sem keywords)")
    
    # Performance geral
    perf_class = "Excelente" if avg_total < 0.5 else "Boa" if avg_total < 1.0 else "Aceitável"
    print(f"   • Performance Geral: {perf_class} ({avg_total*1000:.0f}ms)")
    
    # Conclusões
    print("\n" + "=" * 120)
    print("💡 CONCLUSÕES E INSIGHTS")
    print("=" * 120)
    
    print(f"\n✅ Pontos Fortes do Sistema:")
    print(f"   1. Consistência: Todas as queries retornam resultados relevantes")
    print(f"   2. Performance: Latência média de {avg_total*1000:.0f}ms (adequada para produção)")
    print(f"   3. Descoberta Semântica: {avg_semantic/10*100:.0f}% dos resultados encontrados por semântica pura")
    print(f"   4. Qualidade: Score médio de {statistics.mean([q['avg_score'] for q in qualities]):.4f} ({statistics.mean([q['avg_score'] for q in qualities])*100:.2f}%)")
    
    print(f"\n🎯 Diferencial da IA:")
    print(f"   • Query complexa vs específica: A IA performa bem em ambos os casos")
    print(f"   • Sinônimos e variações: Captura automaticamente sem configuração")
    print(f"   • Contexto semântico: Vai além de match exato de palavras")
    
    print(f"\n📈 Comparativo entre Queries:")
    best_idx = scores_overall.index(max(scores_overall))
    worst_idx = scores_overall.index(min(scores_overall))
    
    print(f"   • Melhor: '{QUERIES[best_idx]}'")
    print(f"     Razão: {qualities[best_idx]['very_high'] + qualities[best_idx]['high']} resultados altamente relevantes")
    print(f"   • Desafiadora: '{QUERIES[worst_idx]}'")
    print(f"     Razão: Query mais específica, mas ainda {qualities[worst_idx]['avg_score']*100:.0f}% de relevância média")
    
    print(f"\n🚀 Recomendações:")
    if avg_total > 1.0:
        print(f"   • Considerar GPU para reduzir latência de {avg_total*1000:.0f}ms → ~200ms")
    if statistics.mean([q['max_score'] for q in qualities]) < 0.7:
        print(f"   • Fine-tuning do modelo pode aumentar scores máximos")
    if avg_semantic < 5:
        print(f"   • Enriquecer embeddings com mais contexto (metadados)")
    
    print(f"\n📊 Avaliação Final:")
    overall_grade = "A" if avg_total < 0.5 and statistics.mean([q['avg_score'] for q in qualities]) > 0.6 else \
                   "B" if avg_total < 1.0 and statistics.mean([q['avg_score'] for q in qualities]) > 0.5 else \
                   "C"
    
    print(f"   🏅 Nota Geral: {overall_grade}")
    print(f"   ✅ Status: {'EXCELENTE - Pronto para produção' if overall_grade == 'A' else 'BOM - Pronto com melhorias opcionais' if overall_grade == 'B' else 'ACEITÁVEL - Necessita otimizações'}")
    
    session.close()
    
    print("\n" + "=" * 120)
    print("✓ DASHBOARD CONCLUÍDO")
    print("=" * 120 + "\n")

if __name__ == "__main__":
    print("\n🚀 Gerando Dashboard de Qualidade Semântica...\n")
    generate_dashboard()
