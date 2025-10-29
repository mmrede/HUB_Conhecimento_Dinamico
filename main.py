# 1. Primeiro, os imports
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from typing import List
import pydantic
from datetime import date
from fastapi.middleware.cors import CORSMiddleware
import logging
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
import spacy
from sqlalchemy import text
import PyPDF2
import io
import numpy as np
from numpy.linalg import norm
import re
from typing import List, Dict, Tuple

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Modelos Pydantic ---
class Parceria(pydantic.BaseModel):
    id: int
    numero_do_termo: str | None
    ano_do_termo: int | None
    cpf_cnpj: str | None
    razao_social: str | None
    objeto: str | None
    data_da_assinatura: date | None
    data_de_publicacao: date | None
    vigencia: date | None
    situacao: str | None

    class Config:
        from_attributes = True

class ParceriasPorAno(pydantic.BaseModel):
    ano_do_termo: int
    total: int

    class Config:
        from_attributes = True

class ParceriasPorSituacao(pydantic.BaseModel):
    situacao: str | None
    quantidade: int

# ADICIONE ESTE NOVO MODELO
class BuscaResponse(pydantic.BaseModel):
    total_items: int
    items: List[Parceria]

    class Config:
        from_attributes = True

class DocumentoSimilar(pydantic.BaseModel):
    parceria: Parceria
    score: float

    class Config:
        from_attributes = True

class SimilaridadeResponse(pydantic.BaseModel):
    parceria_base: Parceria
    documentos_similares: List[DocumentoSimilar]

    class Config:
        from_attributes = True

# --- Configuração do Banco de Dados ---
DB_CONNECTION_STRING = "postgresql://postgres:rx1800@localhost:5433/hub_aura_db"
engine = create_engine(DB_CONNECTION_STRING)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 2. Em seguida, a criação e definição da variável 'app'
app = FastAPI(
    title="HUB Aura API",
    description="API para acessar e consultar os Instrumentos de Parceria.",
    version="1.0.0"
)

# ... (seu código Pydantic, config do banco, etc.)

#app = FastAPI(...) # Esta linha você já tem

# ADICIONE ESTE BLOCO ABAIXO DA LINHA ACIMA
origins = [
    "http://localhost:5173",        # Frontend local (Vite)
    "http://127.0.0.1:5173",        # Loopback explícito
    "http://192.168.1.206:5173",    # IP da rede local do Vite (ajuste se mudar)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Carrega o modelo de IA na inicialização da API
nlp = spacy.load("pt_core_news_lg")
logger.info("Modelo de IA (spaCy) carregado com sucesso.")

# Carrega sentence-transformers para embeddings v2 (usado na busca semântica)
sentence_model = None
try:
    from sentence_transformers import SentenceTransformer
    sentence_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    logger.info("Modelo sentence-transformers carregado com sucesso (384 dims).")
except Exception as e:
    logger.warning(f"sentence-transformers não disponível, usando spaCy como fallback: {e}")

# ... (resto do seu código com os @app.get)

# 3. Agora, você pode usar 'app' para definir suas rotas (endpoints)
@app.get("/")
def read_root():
    return {"status": "HUB Aura API está no ar!", "docs": "/docs"}

# --- 4. ENDPOINTS DA API ---

@app.get("/api/v1/parcerias", response_model=List[Parceria])
def listar_parcerias(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """
    Lista todos os instrumentos de parceria armazenados no banco de dados.
    """
    try:
        query = text("SELECT * FROM instrumentos_parceria ORDER BY id LIMIT :limit OFFSET :skip")
        result = db.execute(query, {"limit": limit, "skip": skip})
        return result.mappings().all()

    except Exception as e:
        logger.error(f"Erro ao listar parcerias: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao consultar o banco de dados")

@app.get("/api/v1/estatisticas/parcerias_por_ano", response_model=List[ParceriasPorAno])
def obter_parcerias_por_ano(db: Session = Depends(get_db)):
    """
    Retorna a contagem de parcerias agrupadas por ano.
    """
    try:
        query = text("""
            SELECT ano_do_termo, COUNT(id) AS total
            FROM instrumentos_parceria
            WHERE ano_do_termo IS NOT NULL
            GROUP BY ano_do_termo
            ORDER BY ano_do_termo DESC;
        """)
        result = db.execute(query)
        return result.mappings().all()

    except Exception as e:
        logger.error(f"Erro ao calcular estatísticas por ano: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Ocorreu um erro interno ao processar sua solicitação.")

# VERSÃO CORRETA E ATUALIZADA
@app.get("/api/v1/parcerias/busca", response_model=BuscaResponse)
def buscar_parcerias(termo: str, db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    """
    Pesquisa parcerias por termo em vários campos com paginação.
    Retorna a lista de itens da página e o total de itens encontrados.
    """
    try:
        termo_busca = f"%{termo}%"
        
        # --- PRIMEIRA CONSULTA: Contar o total de itens ---
        # Usamos unaccent + lower para permitir buscas sem acentos (ex: "inteligencia" encontra "inteligência")
        count_query = text("""
            SELECT COUNT(*) FROM instrumentos_parceria 
            WHERE 
                unaccent(lower(coalesce(numero_do_termo, ''))) ILIKE unaccent(lower(:termo)) OR
                unaccent(lower(coalesce(razao_social, ''))) ILIKE unaccent(lower(:termo)) OR
                unaccent(lower(coalesce(objeto, ''))) ILIKE unaccent(lower(:termo))
        """)
        total_items = db.execute(count_query, {"termo": termo_busca}).scalar_one()

        # --- SEGUNDA CONSULTA: Buscar os itens da página atual ---
        data_query = text("""
            SELECT * FROM instrumentos_parceria 
            WHERE 
                unaccent(lower(coalesce(numero_do_termo, ''))) ILIKE unaccent(lower(:termo)) OR
                unaccent(lower(coalesce(razao_social, ''))) ILIKE unaccent(lower(:termo)) OR
                unaccent(lower(coalesce(objeto, ''))) ILIKE unaccent(lower(:termo))
            ORDER BY id 
            LIMIT :limit OFFSET :skip
        """)
        params = {"termo": termo_busca, "limit": limit, "skip": skip}
        result = db.execute(data_query, params)
        items = result.mappings().all()
        
        # Retorna o objeto completo, conforme o modelo BuscaResponse
        return {"total_items": total_items, "items": items}

    except Exception as e:
        logger.error(f"Erro ao buscar parcerias: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao realizar a busca no banco de dados")

@app.get("/api/v1/estatisticas/situacao", response_model=List[ParceriasPorSituacao])
def obter_parcerias_por_situacao(db: Session = Depends(get_db)):
    """
    Retorna a contagem de parcerias agrupadas por situação.
    """
    try:
        query = text("""
            SELECT situacao, COUNT(*) as quantidade
            FROM instrumentos_parceria 
            GROUP BY situacao 
            ORDER BY quantidade DESC
        """)
        result = db.execute(query)
        return result.mappings().all()
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas por situação: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao consultar o banco de dados")

# BUSCA SEMÂNTICA (deve vir ANTES de rotas com path parameters como {parceria_id})
@app.get("/api/v1/parcerias/semantic-busca", response_model=BuscaResponse)
def busca_semantica(termo: str, db: Session = Depends(get_db), skip: int = 0, limit: int = 10, ano: int | None = None):
    """
    Busca semântica que utiliza embeddings v2 (sentence-transformers, 384 dims) para retornar parcerias ordenadas por similaridade.
    Funciona bem com palavras isoladas E com frases de contexto.
    """
    try:
        # Gerar embedding do termo usando o modelo global cacheado
        if sentence_model is not None:
            qvec = sentence_model.encode(termo).tolist()
            logger.info(f"Usando sentence-transformers para gerar embedding da query: '{termo}' ({len(qvec)} dims)")
        else:
            # Fallback para spaCy (já carregado) - mas isso gerará incompatibilidade de dimensões!
            qvec = nlp(termo).vector.tolist()
            logger.warning(f"sentence-transformers não disponível; usando spaCy para embedding (fallback). Dimensões podem não coincidir!")

        # Pré-calcular a norma do vetor de consulta (para cosseno)
        q_norm = float(np.sqrt(np.sum(np.square(np.array(qvec, dtype=np.float64))))) if qvec else 1.0

        params = {"query_vector": qvec, "q_norm": q_norm, "limit": limit, "skip": skip}
        p_filters = []
        if ano:
            p_filters.append("p.ano_do_termo = :ano")
            params["ano"] = ano
        p_where_sql = ("WHERE " + " AND ".join(p_filters)) if p_filters else ""

        # Filtro para a tabela de vetores
        dv_where_sql = "WHERE dv.objeto_vetor_v2 IS NOT NULL"

        # IMPORTANTE: A coluna objeto_vetor_v2 é FLOAT[]; portanto não podemos usar operador <=> do pgvector.
        # Calculamos a similaridade do cosseno via unnest das arrays e ordenamos pela maior similaridade.
        sql = text(f"""
            WITH q AS (
                SELECT CAST(:query_vector AS float8[]) AS v, CAST(:q_norm AS float8) AS qn
            ),
            agg AS (
                SELECT 
                    dv.parceria_id,
                    SUM(dv_elt.dv_v * q_elt.q_v) AS dot,
                    sqrt(SUM(dv_elt.dv_v * dv_elt.dv_v)) AS dn
                FROM documento_vetores dv
                JOIN q ON TRUE
                JOIN LATERAL unnest(dv.objeto_vetor_v2) WITH ORDINALITY AS dv_elt(dv_v, idx) ON TRUE
                JOIN LATERAL unnest((SELECT v FROM q)) WITH ORDINALITY AS q_elt(q_v, idx2) ON idx = idx2
                {dv_where_sql}
                GROUP BY dv.parceria_id
            )
            SELECT p.*, (dot / NULLIF(dn * (SELECT qn FROM q), 0)) AS score
            FROM agg a
            JOIN instrumentos_parceria p ON p.id = a.parceria_id
            {p_where_sql}
            ORDER BY score DESC NULLS LAST
            LIMIT :limit OFFSET :skip
        """)

        result = db.execute(sql, params)
        rows = result.mappings().all()

        # Extrai apenas os campos de parceria para o cliente (descarta 'score' do mapeamento se presente)
        items = []
        for r in rows:
            item = {k: v for k, v in r.items() if k != 'score'}
            items.append(item)

        total_items = len(items)
        return {"total_items": total_items, "items": items}

    except Exception as e:
        logger.error(f"Erro na busca semântica: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro ao executar busca semântica: {str(e)}")

# NOVO ENDPOINT PARA VISUALIZAÇÃO DETALHADA
@app.get("/api/v1/parcerias/{parceria_id}", response_model=Parceria)
def obter_parceria_por_id(parceria_id: int, db: Session = Depends(get_db)):
    """
    Obtém os detalhes de um instrumento de parceria específico pelo seu ID.
    """
    try:
        query = text("SELECT * FROM instrumentos_parceria WHERE id = :id")
        result = db.execute(query, {"id": parceria_id})
        parceria = result.mappings().first() # .first() para pegar apenas um resultado

        if not parceria:
            # Se nenhum resultado for encontrado, lança um erro 404
            raise HTTPException(status_code=404, detail="Parceria não encontrada")
        
        return parceria

    except HTTPException:
        # Re-lança a exceção HTTP 404 para que o FastAPI a capture
        raise
    except Exception as e:
        logger.error(f"Erro ao obter parceria por ID ({parceria_id}): {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao consultar o banco de dados")
    
# Cole este novo endpoint processar-documento

# ... (seus imports, incluindo 'import re')

@app.post("/api/v1/processar-documento")
async def processar_documento(file: UploadFile = File(...)):
    """
    Recebe um PDF e usa IA com lógica de proximidade para extrair
    o rascunho mais preciso possível.
    """
    logger.info(f"Recebido arquivo para análise final por proximidade: {file.filename}")

    TRIBUNAL_CNPJ = "21.154.877/0001-07"

    try:
        # --- ETAPA 1: Extração e Limpeza (sem alterações) ---
        conteudo_arquivo = await file.read()
        pdf_stream = io.BytesIO(conteudo_arquivo)
        reader = PyPDF2.PdfReader(pdf_stream)
        texto_completo_original = "".join([page.extract_text() or "" for page in reader.pages])

        if not texto_completo_original.strip():
            raise HTTPException(status_code=400, detail="Não foi possível extrair texto do PDF.")

        texto_limpo_para_analise = re.sub(r'\s+', ' ', texto_completo_original.replace('\n', ' '))

        # --- ETAPA 2: LÓGICA DE EXTRAÇÃO FINAL ---

        # 2.1 - Extração do OBJETO (sem alterações)
        match_objeto = re.search(
            r'CLÁUSULA\s*PRIMEIRA\s*–\s*DO\s*OBJETO\s*(.*?)(?=\s*CLÁUSULA\s*SEGUNDA|\Z)',
            texto_completo_original,
            re.DOTALL | re.IGNORECASE
        )
        objeto_sugerido = match_objeto.group(1).strip() if match_objeto else texto_completo_original[:1000]

        # 2.2 - Extração de CNPJ do Parceiro (sem alterações)
        todos_cnpjs = re.findall(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}', texto_limpo_para_analise)
        cnpjs_parceiros = [cnpj for cnpj in todos_cnpjs if cnpj != TRIBUNAL_CNPJ]
        cnpj_sugerido = ", ".join(list(set(cnpjs_parceiros)))

        # 2.3 - Extração da RAZÃO SOCIAL (centrada no CNPJ do parceiro)
        # Estratégia:
        # - Para cada CNPJ de parceiro encontrado, construir uma janela ao redor do CNPJ
        # - Procurar primeiro por blocos em MAIÚSCULAS imediatamente anteriores ao CNPJ
        # - Se não encontrar, usar spaCy para localizar entidades ORG na janela e escolher a mais próxima ao CNPJ
        # - Escolher o candidato com menor distância ao CNPJ e que não pareça um título de documento
        razao_social_sugerida = ""
        regex_upper = re.compile(r"([A-ZÀ-Ú]{2,}(?:\s+[A-ZÀ-Ú]{2,}){1,})")

        def is_junk(c: str) -> bool:
            up = c.upper()
            # termos genéricos ou típicos de cabeçalho/título
            junk = {"UNIÃO", "ESTADO", "MUNICÍPIO", "GOVERNO", "PREFEITURA", "TERMO", "ADITIVO", "ACORDO", "COOPERAÇÃO", "COOPERACAO", "PRORROGAÇÃO", "PRORROGACAO", "OBJETO", "CELEBRAM"}
            if any(j in up for j in junk):
                return True
            if len(c.split()) < 2:
                return True
            return False

        best_global = None
        best_global_dist = float('inf')
        best_global_score = 0.0

        for parceiro_cnpj in cnpjs_parceiros:
            posicao = texto_limpo_para_analise.find(parceiro_cnpj)
            if posicao == -1:
                continue

            # janela única para análise (antes e um pouco depois do CNPJ)
            left = max(0, posicao - 500)
            right = min(len(texto_limpo_para_analise), posicao + 200)
            window = texto_limpo_para_analise[left:right]

            # 1) buscar nomes de organizações antes do CNPJ
            chosen = None
            chosen_dist = float('inf')
            
            # 1.a) primeiro tentar matches em MAIÚSCULAS (mais confiável em docs oficiais)
            upper_matches = regex_upper.findall(window)
            if upper_matches:
                for m in upper_matches:
                    idx = window.rfind(m)
                    if idx >= 0:
                        end_idx = idx + len(m)
                        dist = posicao - (left + end_idx)
                        if dist >= 0 and dist < chosen_dist:
                            candidate = m.strip()
                            if not is_junk(candidate):
                                chosen = candidate
                                chosen_dist = dist

            # 1.b) se não achou em MAIÚSCULAS, procurar padrões em minúsculas
            if not chosen:
                # regex para nomes com conectores típicos (de, do, da, etc.)
                org_patterns = [
                    r'(?:instituto|universidade|fundação|fundacao|empresa|companhia|hospital|secretaria|faculdade|centro|associação|associacao)\s+(?:[\w\s]+(?:\s+(?:de|do|da|dos|das)\s+[\w\s]+)*)',
                    r'(?:[\w\s]+(?:\s+(?:de|do|da|dos|das)\s+[\w\s]+)*(?:\s+(?:ltda|s\.?/?a|sociedade|instituto|empresa)))'
                ]
                for pattern in org_patterns:
                    matches = re.finditer(pattern, window, re.IGNORECASE)
                    for m in matches:
                        idx = m.start()
                        end_idx = m.end()
                        dist = posicao - (left + end_idx)
                        if dist >= 0 and dist < chosen_dist:
                            candidate = m.group().strip()
                            # normaliza capitalização para nomes próprios
                            candidate = ' '.join(word.capitalize() if not word in ['de', 'do', 'da', 'dos', 'das'] else word.lower() 
                                            for word in candidate.split())
                            if not is_junk(candidate):
                                chosen = candidate
                                chosen_dist = dist

            # 2) se não encontrou nome válido ainda, usar spaCy
            if not chosen:
                doc = nlp(window)
                for ent in doc.ents:
                    if ent.label_ == 'ORG':
                        ent_text = ent.text.strip()
                        # posição absoluta aproximada
                        ent_start_abs = left + ent.start_char
                        ent_end_abs = left + ent.end_char
                        dist = min(abs(ent_start_abs - posicao), abs(ent_end_abs - posicao))
                        if not is_junk(ent_text):
                            # prefer closer entities
                            if dist < chosen_dist:
                                chosen = ent_text
                                chosen_dist = dist

            # scoring: prefer closer and longer
            if chosen:
                score = (1.0 / (1 + chosen_dist)) + (len(chosen.split()) / 10.0)
                # uppercase bonus (but not too strong)
                if sum(1 for ch in chosen if ch.isupper()) / max(1, len(chosen)) > 0.4:
                    score += 0.2

                # keep best by distance primarily
                if chosen_dist < best_global_dist or (chosen_dist == best_global_dist and score > best_global_score):
                    best_global = chosen
                    best_global_dist = chosen_dist
                    best_global_score = score

        if best_global:
            razao_social_sugerida = best_global

        # 2.4 - Extração do ANO DO TERMO (sem alterações)
        match_ano = re.search(r'Nº\s*\d+/(\d{4})', texto_limpo_para_analise, re.IGNORECASE)
        ano_do_termo_sugerido = match_ano.group(1) if match_ano else ""
        
        return {
            "razao_social_sugerida": razao_social_sugerida,
            "objeto_sugerido": objeto_sugerido,
            "cnpj_sugerido": cnpj_sugerido,
            "ano_do_termo_sugerido": ano_do_termo_sugerido
        }

    except Exception as e:
        logger.error(f"Erro na análise final do arquivo {file.filename}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro interno ao processar o arquivo: {str(e)}")
    
    # Crie um novo modelo Pydantic para receber os dados do formulário

class ParceriaCreate(pydantic.BaseModel):
    razao_social: str
    objeto: str
    # Adicionando os novos campos (que podem ser nulos ou vazios)
    cpf_cnpj: str | None = None
    ano_do_termo: int | None = None

    # Adicione outros campos aqui conforme seu formulário evoluir

@app.get("/api/v1/parcerias/{parceria_id}/similares", response_model=SimilaridadeResponse)
def obter_documentos_similares(
    parceria_id: int, 
    limite: int = 5, 
    ef_search: int = None,
    db: Session = Depends(get_db)
):
    """
    Retorna os documentos mais similares a uma parceria específica usando pgvector/HNSW.
    
    Args:
        parceria_id: ID da parceria base
        limite: Número máximo de documentos similares a retornar
        ef_search: Parâmetro ef_search do HNSW (trade-off precisão/velocidade)
    """
    try:
        # 1. Buscar a parceria base
        parceria_base = db.execute(
            text("SELECT * FROM instrumentos_parceria WHERE id = :id"),
            {"id": parceria_id}
        ).mappings().first()
        
        if not parceria_base:
            raise HTTPException(status_code=404, detail="Parceria não encontrada")
        
        # 2. Se ef_search fornecido, tentar configurar (ignora erro se não suportado)
        if ef_search:
            try:
                db.execute(text("SET LOCAL pgvector.ef_search = :ef"), {"ef": ef_search})
            except Exception as e:
                logger.warning(f"Aviso: não foi possível definir ef_search={ef_search}. Erro: {str(e)}")
            
        # 3. Buscar documentos similares usando diretamente o operador cosine_similarity
        # Nota: pgvector vai usar o índice HNSW automaticamente se apropriado
        similares = db.execute(text("""
            WITH base_vector AS (
                SELECT objeto_vetor 
                FROM documento_vetores 
                WHERE parceria_id = :id
            )
            SELECT 
                p.*,
                (dv.objeto_vetor <=> (SELECT objeto_vetor FROM base_vector)) as score
            FROM documento_vetores dv
            JOIN instrumentos_parceria p ON p.id = dv.parceria_id
            WHERE dv.parceria_id != :id
            ORDER BY dv.objeto_vetor <=> (SELECT objeto_vetor FROM base_vector)
            LIMIT :limite
        """), {
            "id": parceria_id,
            "limite": limite
        }).mappings().all()
        
        # 4. Formatar resposta
        docs_similares = [
            DocumentoSimilar(parceria=similar, score=similar["score"])
            for similar in similares
        ]
        
        return SimilaridadeResponse(
            parceria_base=parceria_base,
            documentos_similares=docs_similares
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar documentos similares: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao consultar similaridades")


def criar_parceria(parceria: ParceriaCreate, db: Session = Depends(get_db)):
    """
    Cria um novo registro de parceria com os dados validados e calcula similaridades usando pgvector.
    """
    try:
        # 1. Inserir a parceria
        query = text("""
            INSERT INTO instrumentos_parceria (razao_social, objeto, cpf_cnpj, ano_do_termo, situacao)
            VALUES (:razao_social, :objeto, :cpf_cnpj, :ano_do_termo, :situacao)
            RETURNING *;
        """)
        params = {
            "razao_social": parceria.razao_social,
            "objeto": parceria.objeto,
            "cpf_cnpj": parceria.cpf_cnpj,
            "ano_do_termo": parceria.ano_do_termo,
            "situacao": "Cadastrado via IA"
        }
        result = db.execute(query, params)
        novo_registro = result.mappings().first()
        
        # 2. Gerar e salvar vetor do documento usando o tipo nativo vector do pgvector
        if parceria.objeto:
            doc_vetor = nlp(parceria.objeto).vector.tolist()
            vetor_query = text("""
                INSERT INTO documento_vetores (parceria_id, objeto_vetor)
                VALUES (:parceria_id, :vetor::vector);
            """)
            db.execute(vetor_query, {
                "parceria_id": novo_registro["id"],
                "vetor": doc_vetor
            })
            
            # 3. Calcular similaridades com documentos existentes usando operador cosine_similarity do pgvector
            sim_query = text("""
                INSERT INTO similaridades (parceria_id_1, parceria_id_2, score)
                SELECT 
                    :novo_id as parceria_id_1,
                    p.id as parceria_id_2,
                    (dv.objeto_vetor <=> (SELECT objeto_vetor FROM documento_vetores WHERE parceria_id = :novo_id)) as score
                FROM instrumentos_parceria p
                JOIN documento_vetores dv ON p.id = dv.parceria_id
                WHERE p.id != :novo_id;
            """)
            db.execute(sim_query, {"novo_id": novo_registro["id"]})
            
            # Inserir os scores inversos também (A->B e B->A)
            sim_inverso_query = text("""
                INSERT INTO similaridades (parceria_id_1, parceria_id_2, score)
                SELECT parceria_id_2, parceria_id_1, score
                FROM similaridades
                WHERE parceria_id_1 = :novo_id;
            """)
            db.execute(sim_inverso_query, {"novo_id": novo_registro["id"]})
        
        db.commit()
        return novo_registro
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao criar parceria: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao salvar no banco de dados.")