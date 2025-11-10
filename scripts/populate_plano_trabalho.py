"""
Script para popular o campo plano_de_trabalho com conteúdo sintético gerado a partir
do objeto e razão social de cada parceria.

Gera textos seguindo a estrutura jurídica típica de Termos de Cooperação Técnica.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import random
import os

# Configuração do banco (usa variável de ambiente DATABASE_URL quando definida)
DB_CONNECTION_STRING = os.environ.get("DATABASE_URL", "postgresql://postgres:rx1800@localhost:5433/hub_aura_db")
engine = create_engine(DB_CONNECTION_STRING)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Templates de texto para planos de trabalho
TEMPLATES = [
    # Template 1: Desenvolvimento de programas
    """Constitui objeto do presente Termo de Cooperação Técnica o desenvolvimento de programas específicos de cooperação relacionados a {tema_principal}, tanto nos aspectos técnicos e profissionais, quanto nas áreas de pesquisas institucionais, bem como na colaboração pelo desenvolvimento conjunto de pesquisas e estudos vinculados {contexto_razao_social}, incluindo a facilitação da cooperação nos campos da investigação em Programas de Pós-Graduação, cursos, seminários, colóquios, congressos, formação profissional e outros programas relacionados com as temáticas do desenvolvimento sustentável, da democracia, da cidadania, das políticas públicas, do direito comunitário, do direito de integração, da proteção dos direitos fundamentais, de direitos humanos e do Estado de Direito.""",
    
    # Template 2: Intercâmbio técnico-científico
    """O presente Termo de Cooperação visa estabelecer intercâmbio técnico-científico entre as partes para o desenvolvimento de ações conjuntas na área de {tema_principal}, contemplando {contexto_razao_social}. As atividades incluem a realização de estudos, pesquisas, eventos, capacitações e desenvolvimento de metodologias, bem como o compartilhamento de experiências, conhecimentos técnicos e boas práticas, observados os princípios da administração pública e da cooperação institucional, com vistas ao fortalecimento das instituições públicas e ao aprimoramento dos serviços prestados à sociedade.""",
    
    # Template 3: Capacitação e desenvolvimento institucional
    """Constitui objeto deste instrumento a promoção de ações de capacitação, desenvolvimento institucional e transferência de conhecimento na área de {tema_principal}, envolvendo {contexto_razao_social}. O plano de trabalho contempla a realização de cursos de formação e aperfeiçoamento, workshops, seminários técnicos, elaboração de materiais didáticos e institucionais, desenvolvimento de sistemas e ferramentas de gestão, além da troca de experiências e do estabelecimento de parcerias estratégicas para o fortalecimento das competências organizacionais e para a modernização dos processos administrativos e técnicos.""",
    
    # Template 4: Execução de projetos específicos
    """O presente Termo tem por finalidade viabilizar a execução conjunta de projetos específicos relacionados a {tema_principal}, com participação de {contexto_razao_social}, mediante a conjugação de esforços técnicos, administrativos e operacionais. As atividades previstas compreendem o planejamento, desenvolvimento, implementação e avaliação de soluções, ferramentas e metodologias, a realização de diagnósticos e estudos de viabilidade, a elaboração de documentos técnicos e normativos, bem como o acompanhamento e monitoramento das ações executadas, sempre em conformidade com os princípios da eficiência, transparência e responsabilidade pública.""",
    
    # Template 5: Assessoria técnica e consultoria
    """Este Termo de Cooperação Técnica objetiva a prestação de assessoria técnica especializada e consultoria nas áreas relacionadas a {tema_principal}, considerando a expertise de {contexto_razao_social}. O plano de trabalho abrange atividades de orientação técnica, análise de processos e procedimentos, elaboração de pareceres e recomendações, desenvolvimento de planos e estratégias institucionais, apoio à implementação de políticas públicas, realização de auditorias e avaliações, além da capacitação de equipes técnicas para o aprimoramento contínuo dos serviços prestados e para o fortalecimento da governança institucional.""",
]

# Palavras-chave para identificar temas principais
TEMAS_MAP = {
    'educação': 'educação, formação acadêmica e desenvolvimento educacional',
    'ensino': 'ensino, capacitação pedagógica e processos educativos',
    'saúde': 'saúde pública, assistência médica e promoção da saúde',
    'tecnologia': 'tecnologia da informação, sistemas informatizados e inovação tecnológica',
    'informação': 'gestão da informação, sistemas de dados e compartilhamento de informações',
    'meio ambiente': 'preservação ambiental, sustentabilidade e gestão de recursos naturais',
    'fiscal': 'controle fiscal, auditoria governamental e gestão orçamentária',
    'auditoria': 'auditoria, controle interno e conformidade normativa',
    'gestão': 'gestão pública, administração e modernização institucional',
    'jurídico': 'assessoria jurídica, suporte legal e conformidade normativa',
    'pesquisa': 'pesquisa científica, desenvolvimento acadêmico e produção de conhecimento',
    'estágio': 'formação profissional, estágios supervisionados e desenvolvimento de competências',
    'capacitação': 'capacitação profissional, treinamento e desenvolvimento de recursos humanos',
    'social': 'desenvolvimento social, assistência social e políticas de inclusão',
    'cultural': 'promoção cultural, patrimônio histórico e ações culturais',
    'segurança': 'segurança pública, proteção social e prevenção',
    'infraestrutura': 'obras públicas, infraestrutura e desenvolvimento urbano',
    'transporte': 'mobilidade urbana, transporte público e logística',
    'comunicação': 'comunicação institucional, divulgação e transparência',
    'planejamento': 'planejamento estratégico, gestão de projetos e desenvolvimento institucional',
}

def extrair_tema_principal(objeto: str, razao_social: str) -> str:
    """Extrai o tema principal com base no objeto e razão social"""
    texto_completo = f"{objeto or ''} {razao_social or ''}".lower()
    
    # Procurar por palavras-chave
    for palavra, tema in TEMAS_MAP.items():
        if palavra in texto_completo:
            return tema
    
    # Fallback genérico baseado no objeto
    if objeto and len(objeto) > 30:
        # Pegar primeiras palavras significativas do objeto
        palavras = objeto.split()[:8]
        return ' '.join(palavras).lower()
    
    return "cooperação técnica e institucional"

def criar_contexto_razao_social(razao_social: str, objeto: str) -> str:
    """Cria contexto baseado na razão social"""
    if not razao_social:
        return "às atividades institucionais"
    
    razao_lower = razao_social.lower()
    
    # Identificar tipo de instituição
    if any(x in razao_lower for x in ['universidade', 'faculdade', 'instituto de ensino', 'escola']):
        return f"à atuação de {razao_social} no campo do ensino superior, pesquisa e extensão universitária"
    elif any(x in razao_lower for x in ['tribunal', 'justiça', 'ministério público']):
        return f"às competências de {razao_social} no exercício do controle externo e fiscalização"
    elif any(x in razao_lower for x in ['secretaria', 'ministério', 'prefeitura', 'governo']):
        return f"às atribuições de {razao_social} na execução de políticas públicas"
    elif any(x in razao_lower for x in ['receita', 'fazenda']):
        return f"às atividades de {razao_social} relacionadas à arrecadação e fiscalização tributária"
    elif any(x in razao_lower for x in ['banco', 'caixa', 'financeira']):
        return f"aos serviços prestados por {razao_social} no sistema financeiro nacional"
    elif any(x in razao_lower for x in ['conselho', 'ordem', 'sindicato']):
        return f"às funções de {razao_social} na regulação e fiscalização profissional"
    else:
        return f"às atividades desenvolvidas por {razao_social}"

def gerar_plano_trabalho(objeto: str, razao_social: str) -> str:
    """Gera um plano de trabalho sintético baseado no objeto e razão social"""
    tema = extrair_tema_principal(objeto, razao_social)
    contexto = criar_contexto_razao_social(razao_social, objeto)
    
    # Escolher template aleatório
    template = random.choice(TEMPLATES)
    
    # Preencher template
    plano = template.format(
        tema_principal=tema,
        contexto_razao_social=contexto
    )
    
    return plano

def main():
    """Popula o campo plano_de_trabalho para todos os registros"""
    db = SessionLocal()
    
    try:
        # Buscar todas as parcerias sem plano de trabalho
        query = text("""
            SELECT id, objeto, razao_social 
            FROM instrumentos_parceria 
            WHERE plano_de_trabalho IS NULL
            ORDER BY id
        """)
        
        result = db.execute(query)
        parcerias = result.mappings().all()
        
        print(f"🚀 Gerando planos de trabalho para {len(parcerias)} parcerias...")
        print()
        
        contador = 0
        for parceria in parcerias:
            try:
                plano = gerar_plano_trabalho(
                    parceria['objeto'] or '',
                    parceria['razao_social'] or ''
                )
                
                update_query = text("""
                    UPDATE instrumentos_parceria 
                    SET plano_de_trabalho = :plano 
                    WHERE id = :id
                """)
                
                db.execute(update_query, {
                    'id': parceria['id'],
                    'plano': plano
                })
                
                contador += 1
                
                # Commit a cada 10 registros
                if contador % 10 == 0:
                    db.commit()
                    print(f"✅ Processados {contador}/{len(parcerias)} registros...")
                
            except Exception as e:
                print(f"⚠️ Erro ao processar parceria {parceria['id']}: {e}")
                continue
        
        # Commit final
        db.commit()
        
        print()
        print(f"✅ Concluído! {contador} planos de trabalho gerados com sucesso.")
        print()
        
        # Mostrar alguns exemplos
        print("📄 Exemplos gerados:")
        print("=" * 80)
        
        exemplos_query = text("""
            SELECT id, razao_social, objeto, LEFT(plano_de_trabalho, 200) as plano_preview
            FROM instrumentos_parceria 
            WHERE plano_de_trabalho IS NOT NULL
            ORDER BY id
            LIMIT 3
        """)
        
        exemplos = db.execute(exemplos_query).mappings().all()
        
        for i, ex in enumerate(exemplos, 1):
            print(f"\n📋 Exemplo {i}:")
            print(f"   ID: {ex['id']}")
            print(f"   Razão Social: {ex['razao_social']}")
            print(f"   Objeto: {ex['objeto'][:100]}...")
            print(f"   Plano (preview): {ex['plano_preview']}...")
            print()
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao popular planos de trabalho: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        db.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
