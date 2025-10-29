"""
Analisador e gerador de relatórios para Hub Aura.
Gera métricas, insights e validações sobre parcerias e embeddings.

Uso:
    python scripts/report_analyzer.py [--plot] [--export-csv]
"""
import argparse
from sqlalchemy import create_engine, text
import pandas as pd
import numpy as np
from datetime import datetime
import logging
from collections import Counter
import json
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração do banco
DB_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:rx1800@localhost:5433/hub_aura_db')
engine = create_engine(DB_URL)

def carregar_dados_base():
    """Carrega dados básicos das parcerias."""
    with engine.connect() as conn:
        df = pd.read_sql("""
            SELECT 
                p.*,
                dv.objeto_vetor IS NOT NULL as tem_vetor,
                dv.objeto_vetor_v2 IS NOT NULL as tem_vetor_v2
            FROM instrumentos_parceria p
            LEFT JOIN documento_vetores dv ON p.id = dv.parceria_id
        """, conn)
    return df

def metricas_temporais(df):
    """Análise temporal das parcerias."""
    print("\n=== Métricas Temporais ===")
    
    # Parcerias por ano
    anos = pd.Series(df['ano_do_termo'].value_counts().sort_index())
    print("\nParcerias por ano:")
    print(anos.to_string())
    
    # Tendência (crescimento/decréscimo)
    if not anos.empty and len(anos) > 1:
        crescimento = ((anos.iloc[-1] / anos.iloc[0]) ** (1/(len(anos)-1)) - 1) * 100
        print(f"\nTaxa média de crescimento anual: {crescimento:.1f}%")

def analisar_vetores(df):
    """Análise dos embeddings."""
    print("\n=== Análise de Vetores ===")
    
    total = len(df)
    com_vetor = df['tem_vetor'].sum()
    com_vetor_v2 = df['tem_vetor_v2'].sum()
    
    print(f"\nTotal de parcerias: {total}")
    print(f"Com vetor (spaCy): {com_vetor} ({com_vetor/total*100:.1f}%)")
    print(f"Com vetor v2 (sentence-transformers): {com_vetor_v2} ({com_vetor_v2/total*100:.1f}%)")

    # Buscar alguns vetores para análise
    with engine.connect() as conn:
        vetores = pd.read_sql("""
            SELECT objeto_vetor, objeto_vetor_v2
            FROM documento_vetores
            LIMIT 100
        """, conn)
    
    if not vetores.empty:
        print("\nAnálise de dimensionalidade:")
        if 'objeto_vetor' in vetores.columns and vetores['objeto_vetor'].notna().any():
            dim = len(vetores['objeto_vetor'].iloc[0])
            print(f"- Vetores spaCy: {dim} dimensões")
        if 'objeto_vetor_v2' in vetores.columns and vetores['objeto_vetor_v2'].notna().any():
            dim = len(vetores['objeto_vetor_v2'].iloc[0])
            print(f"- Vetores sentence-transformers: {dim} dimensões")

def analisar_similaridades():
    """Análise das similaridades entre parcerias."""
    print("\n=== Análise de Similaridades ===")
    
    with engine.connect() as conn:
        # Estatísticas de similaridade
        stats = pd.read_sql("""
            SELECT 
                COUNT(*) as total_pairs,
                AVG(score) as avg_score,
                MIN(score) as min_score,
                MAX(score) as max_score,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY score) as median_score
            FROM similaridades
        """, conn)
        
        print("\nEstatísticas de similaridade:")
        for col in stats.columns:
            val = stats[col].iloc[0]
            print(f"- {col}: {val:.4f}")
        
        # Top pares mais similares
        print("\nTop 5 pares mais similares:")
        top_pairs = pd.read_sql("""
            SELECT 
                s.parceria_id_1,
                s.parceria_id_2,
                p1.razao_social as razao_1,
                p2.razao_social as razao_2,
                s.score
            FROM similaridades s
            JOIN instrumentos_parceria p1 ON s.parceria_id_1 = p1.id
            JOIN instrumentos_parceria p2 ON s.parceria_id_2 = p2.id
            ORDER BY s.score DESC
            LIMIT 5
        """, conn)
        
        for _, row in top_pairs.iterrows():
            print(f"- Score {row['score']:.4f}: {row['razao_1']} <-> {row['razao_2']}")

def main():
    parser = argparse.ArgumentParser(description='Analisador de métricas do Hub Aura')
    parser.add_argument('--plot', action='store_true', help='Gerar gráficos (requer matplotlib)')
    parser.add_argument('--export-csv', action='store_true', help='Exportar dados para CSV')
    args = parser.parse_args()

    try:
        print("\n=== Relatório Hub Aura ===")
        print(f"Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        df = carregar_dados_base()
        
        metricas_temporais(df)
        analisar_vetores(df)
        analisar_similaridades()
        
        if args.export_csv:
            output_dir = 'reports'
            os.makedirs(output_dir, exist_ok=True)
            df.to_csv(f"{output_dir}/parcerias_report.csv", index=False)
            print(f"\nDados exportados para {output_dir}/parcerias_report.csv")
        
        if args.plot:
            try:
                import matplotlib.pyplot as plt
                import seaborn as sns
                
                # Configurar estilo
                plt.style.use('seaborn')
                
                # Gráfico: Parcerias por ano
                plt.figure(figsize=(12, 6))
                anos_count = df['ano_do_termo'].value_counts().sort_index()
                anos_count.plot(kind='bar')
                plt.title('Parcerias por Ano')
                plt.xlabel('Ano')
                plt.ylabel('Quantidade')
                plt.tight_layout()
                plt.savefig(f"{output_dir}/parcerias_por_ano.png")
                print(f"\nGráfico salvo em {output_dir}/parcerias_por_ano.png")
                
            except ImportError:
                print("\nAviso: matplotlib não instalado. Skipping plots.")
        
    except Exception as e:
        logger.error(f"Erro ao gerar relatório: {e}", exc_info=True)
        raise

if __name__ == '__main__':
    main()