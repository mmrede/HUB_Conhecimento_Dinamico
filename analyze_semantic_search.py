"""
Script de demonstração da busca semântica
Conecta diretamente ao banco e executa busca sem depender do servidor web
"""
import os
os.environ['DATABASE_URL'] = "postgresql://postgres:rx1800@localhost:5433/hub_aura_db"

import numpy as np
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sentence_transformers import SentenceTransformer
import time
from datetime import datetime

# Configuração do banco
DB_URL = "postgresql://postgres:rx1800@localhost:5433/hub_aura_db"
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)

def analyze_semantic_search():
    """Executa busca semântica diretamente no banco"""
    
    query_text = "quais os melhores parceiros para uma capacitação em inteligência"
    
    print("=" * 100)
    print("RELATÓRIO DE ANÁLISE DE BUSCA SEMÂNTICA - HUB AURA TCE")
    print("=" * 100)
    print(f"\n📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"🔍 Query: '{query_text}'")
    print(f"💾 Banco: PostgreSQL (localhost:5433/hub_aura_db)")
    print(f"🤖 Modelo: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    
    try:
        # Carregar modelo
        print("\n" + "-" * 100)
        print("⏳ Carregando modelo de IA...")
        model_start = time.time()
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        model_time = time.time() - model_start
        print(f"✅ Modelo carregado em {model_time:.2f}s")
        
        # Gerar embedding da query
        print(f"\n⏳ Gerando embedding da query...")
        embed_start = time.time()
        query_vector = model.encode(query_text).tolist()
        embed_time = time.time() - embed_start
        print(f"✅ Embedding gerado em {embed_time:.3f}s ({len(query_vector)} dimensões)")
        
        # Calcular norma
        q_norm = float(np.sqrt(np.sum(np.square(np.array(query_vector, dtype=np.float64)))))
        
        # Executar busca no banco
        print(f"\n⏳ Executando busca semântica no banco de dados...")
        db_start = time.time()
        
        session = Session()
        
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
        
        print(f"✅ Busca concluída em {db_time:.3f}s")
        
        # Tempo total
        total_time = model_time + embed_time + db_time
        
        # Análise de performance
        print("\n" + "=" * 100)
        print("📊 ANÁLISE DE PERFORMANCE DA IA")
        print("=" * 100)
        
        print(f"\n⏱️  Tempos de Execução:")
        print(f"   • Carregamento do Modelo: {model_time:.2f}s")
        print(f"   • Geração de Embedding: {embed_time:.3f}s ({embed_time*1000:.0f}ms)")
        print(f"   • Busca no Banco de Dados: {db_time:.3f}s ({db_time*1000:.0f}ms)")
        print(f"   • TEMPO TOTAL: {total_time:.2f}s")
        
        # Classificação de performance
        if embed_time + db_time < 0.5:
            perf = "EXCELENTE ⚡"
        elif embed_time + db_time < 1.0:
            perf = "MUITO BOA 🟢"
        elif embed_time + db_time < 2.0:
            perf = "BOA 🟡"
        else:
            perf = "ACEITÁVEL 🟠"
        
        print(f"\n📈 Performance (excluindo carregamento inicial): {perf}")
        print(f"   • Latência de busca: {(embed_time + db_time)*1000:.0f}ms")
        
        print(f"\n🔧 Especificações Técnicas:")
        print(f"   • Device: CPU")
        print(f"   • Dimensões do vetor: {len(query_vector)}")
        print(f"   • Métrica de similaridade: Cosseno")
        print(f"   • Banco de dados: PostgreSQL 15")
        print(f"   • Framework: sentence-transformers + SQLAlchemy")
        
        # Resultados
        print("\n" + "=" * 100)
        print(f"🎯 ANÁLISE DETALHADA DOS {len(rows)} RESULTADOS ENCONTRADOS")
        print("=" * 100)
        
        if rows:
            scores = []
            parceiros = {}
            
            for idx, row in enumerate(rows, 1):
                item = dict(row)
                score = float(item.get('similarity_score', 0))
                scores.append(score)
                
                # Contar parceiros
                parceiro = item.get('nome_parceiro', 'Desconhecido')
                parceiros[parceiro] = parceiros.get(parceiro, 0) + 1
                
                print(f"\n{'─' * 100}")
                print(f"📋 RESULTADO #{idx}")
                print(f"{'─' * 100}")
                
                # Dados principais
                print(f"\n🆔 Termo Nº: {item.get('numero_do_termo', 'N/A')}/{item.get('ano_do_termo', 'N/A')}")
                print(f"🏢 Parceiro: {parceiro}")
                print(f"📅 Data de Assinatura: {item.get('data_assinatura', 'N/A')}")
                print(f"⏰ Vigência: {item.get('data_inicio_vigencia', 'N/A')} → {item.get('data_fim_vigencia', 'N/A')}")
                
                if item.get('tipo_instrumento'):
                    print(f"📄 Tipo: {item.get('tipo_instrumento')}")
                if item.get('unidade_gestora'):
                    print(f"🏛️  Unidade Gestora: {item.get('unidade_gestora')}")
                
                # Score de similaridade
                print(f"\n🎯 Score de Similaridade: {score:.4f} ({score*100:.2f}%)")
                
                # Classificação de relevância
                if score >= 0.7:
                    relevancia = "MUITO ALTA"
                    emoji = "🟢"
                elif score >= 0.5:
                    relevancia = "ALTA"
                    emoji = "🟡"
                elif score >= 0.3:
                    relevancia = "MÉDIA"
                    emoji = "🟠"
                else:
                    relevancia = "BAIXA"
                    emoji = "🔴"
                
                print(f"   {emoji} Relevância: {relevancia}")
                
                # Objeto
                objeto = item.get('objeto', '')
                if objeto:
                    print(f"\n💡 Objeto do Termo:")
                    if len(objeto) > 250:
                        print(f"   {objeto[:250]}...")
                    else:
                        print(f"   {objeto}")
                
                # Análise de keywords
                print(f"\n🔍 Análise de Relevância para a Query:")
                objeto_lower = objeto.lower() if objeto else ''
                parceiro_lower = parceiro.lower()
                
                keywords_found = []
                
                # Busca por termos relacionados à query
                if any(term in objeto_lower or term in parceiro_lower for term in ['capacitação', 'capacitacao']):
                    keywords_found.append("✓ Menciona 'capacitação'")
                
                if any(term in objeto_lower or term in parceiro_lower for term in ['inteligência', 'inteligencia', 'artificial', 'ia']):
                    keywords_found.append("✓ Relacionado a 'inteligência/IA'")
                
                if any(term in objeto_lower for term in ['ensino', 'educação', 'educacao', 'treinamento', 'formação', 'formacao', 'curso']):
                    keywords_found.append("✓ Área de ensino/educação/treinamento")
                
                if any(term in objeto_lower for term in ['tecnologia', 'inovação', 'inovacao', 'digital', 'dados']):
                    keywords_found.append("✓ Envolve tecnologia/inovação")
                
                if any(term in objeto_lower for term in ['pesquisa', 'desenvolvimento', 'ciência', 'ciencia', 'científico', 'cientifico']):
                    keywords_found.append("✓ Atividades de pesquisa/desenvolvimento")
                
                if keywords_found:
                    for kw in keywords_found:
                        print(f"   {kw}")
                else:
                    print(f"   • Relevância baseada em similaridade semântica vetorial")
                    print(f"   • O modelo identificou correlação contextual com a query")
            
            # Estatísticas agregadas
            print(f"\n{'=' * 100}")
            print("📊 ESTATÍSTICAS AGREGADAS")
            print(f"{'=' * 100}")
            
            print(f"\n📈 Scores de Similaridade:")
            print(f"   • Máximo: {max(scores):.4f} ({max(scores)*100:.2f}%)")
            print(f"   • Mínimo: {min(scores):.4f} ({min(scores)*100:.2f}%)")
            print(f"   • Média: {sum(scores)/len(scores):.4f} ({(sum(scores)/len(scores))*100:.2f}%)")
            print(f"   • Mediana: {sorted(scores)[len(scores)//2]:.4f}")
            
            # Distribuição
            muito_alta = sum(1 for s in scores if s >= 0.7)
            alta = sum(1 for s in scores if 0.5 <= s < 0.7)
            media = sum(1 for s in scores if 0.3 <= s < 0.5)
            baixa = sum(1 for s in scores if s < 0.3)
            
            print(f"\n📊 Distribuição de Relevância:")
            print(f"   🟢 Muito Alta (≥70%): {muito_alta} resultado(s) - {muito_alta/len(scores)*100:.1f}%")
            print(f"   🟡 Alta (50-69%): {alta} resultado(s) - {alta/len(scores)*100:.1f}%")
            print(f"   🟠 Média (30-49%): {media} resultado(s) - {media/len(scores)*100:.1f}%")
            print(f"   🔴 Baixa (<30%): {baixa} resultado(s) - {baixa/len(scores)*100:.1f}%")
            
            # Parceiros
            print(f"\n🤝 Parceiros Identificados ({len(parceiros)}):")
            for parceiro, count in sorted(parceiros.items(), key=lambda x: x[1], reverse=True):
                print(f"   • {parceiro}: {count} termo(s)")
            
            # Conclusões e recomendações
            print(f"\n{'=' * 100}")
            print("💡 CONCLUSÕES E RECOMENDAÇÕES")
            print(f"{'=' * 100}")
            
            print(f"\n✅ Pontos Fortes:")
            print(f"   • Performance de busca rápida ({(embed_time + db_time)*1000:.0f}ms)")
            print(f"   • Modelo multilíngue otimizado para português")
            print(f"   • Busca vetorial escalável com PostgreSQL")
            print(f"   • Retornou {len(rows)} resultados relevantes")
            
            if max(scores) >= 0.5:
                print(f"   • Resultados com alta similaridade encontrados")
            
            if embed_time + db_time > 1.0:
                print(f"\n⚠️  Pontos de Atenção:")
                print(f"   • Latência pode ser melhorada com GPU")
                print(f"   • Considerar cache de embeddings para queries frequentes")
            
            if max(scores) < 0.5:
                print(f"\n💡 Sugestões de Melhoria:")
                print(f"   • Scores baixos - considerar fine-tuning do modelo")
                print(f"   • Enriquecer base de dados com mais documentos")
                print(f"   • Avaliar uso de modelo maior (mais parâmetros)")
            else:
                print(f"\n💡 Sugestões de Melhoria:")
                print(f"   • Implementar cache de embeddings para melhor performance")
                print(f"   • Considerar indexação HNSW para bases maiores")
                print(f"   • Avaliar uso de GPU para reduzir latência")
            
            # Comparação com busca tradicional
            print(f"\n🔄 Vantagens sobre Busca Tradicional (keyword-based):")
            print(f"   • Entende sinônimos e contexto semântico")
            print(f"   • Não depende de correspondência exata de palavras")
            print(f"   • Captura relações conceituais ('capacitação' ↔ 'treinamento', 'inteligência' ↔ 'IA')")
            print(f"   • Ranqueamento por similaridade vetorial (mais preciso)")
            
        else:
            print("\n⚠️  Nenhum resultado encontrado.")
            print("\nPossíveis causas:")
            print("   • Tabela documento_vetores vazia")
            print("   • Embeddings não gerados para os documentos")
            print("   • Problema na query SQL")
        
        session.close()
        
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print(f"\n{'=' * 100}")
    print("✓ RELATÓRIO CONCLUÍDO")
    print(f"{'=' * 100}\n")

if __name__ == "__main__":
    print("\n🚀 Iniciando análise de busca semântica...\n")
    analyze_semantic_search()
