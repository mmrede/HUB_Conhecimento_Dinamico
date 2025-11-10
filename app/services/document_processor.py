import io
import re
import spacy
from typing import Optional, Dict, List
from fastapi import HTTPException
import logging
from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)

class DocumentProcessor:
    TRIBUNAL_CNPJ = "21.154.877/0001-07"
    
    def __init__(self, nlp_model: spacy.language.Language):
        self.nlp = nlp_model
        
    async def process_pdf(self, file_content: bytes) -> Dict[str, str]:
        """
        Process a PDF file and extract relevant information.
        
        Args:
            file_content: Raw bytes of the PDF file
            
        Returns:
            Dictionary containing extracted information
        """
        try:
            # Extract text from PDF
            pdf_stream = io.BytesIO(file_content)
            reader = PdfReader(pdf_stream)
            texto_completo = self._extract_text(reader)
            
            if not texto_completo.strip():
                raise HTTPException(status_code=400, detail="Não foi possível extrair texto do PDF.")
                
            texto_limpo = self._clean_text(texto_completo)
            
            # Extract information
            return {
                "razao_social_sugerida": self._extract_razao_social(texto_limpo),
                "objeto_sugerido": self._extract_objeto(texto_completo),
                "cnpj_sugerido": self._extract_cnpj(texto_limpo),
                "ano_do_termo_sugerido": self._extract_ano(texto_limpo)
            }
            
        except Exception as e:
            logger.error(f"Erro no processamento do documento: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")
    
    def _extract_text(self, reader: PdfReader) -> str:
        """Extract text from PDF pages"""
        return "".join([page.extract_text() or "" for page in reader.pages])
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        return re.sub(r'\s+', ' ', text.replace('\n', ' '))
    
    def _extract_razao_social(self, texto: str) -> str:
        """
        Extract organization name using a sophisticated approach:
        1. Look for organizations near CNPJs
        2. Use regex patterns for formal names
        3. Apply NLP for entity recognition
        4. Score and rank candidates
        """
        cnpjs = self._extract_cnpj_list(texto)
        candidates = []
        
        for cnpj in cnpjs:
            if cnpj == self.TRIBUNAL_CNPJ:
                continue
                
            # Find text window around CNPJ
            pos = texto.find(cnpj)
            window = texto[max(0, pos - 500):min(len(texto), pos + 200)]
            
            # Try different extraction methods
            candidates.extend(self._find_uppercase_orgs(window, pos))
            candidates.extend(self._find_formal_names(window, pos))
            candidates.extend(self._find_spacy_orgs(window, pos))
        
        # Score and select best candidate
        if candidates:
            return max(candidates, key=lambda x: x[1])[0]
        return ""
    
    def _find_uppercase_orgs(self, text: str, cnpj_pos: int) -> List[tuple]:
        """Find organization names in uppercase"""
        pattern = r"([A-ZÀ-Ú]{2,}(?:\s+[A-ZÀ-Ú]{2,}){1,})"
        matches = re.finditer(pattern, text)
        results = []
        
        for match in matches:
            if not self._is_junk(match.group()):
                score = self._calculate_score(match.group(), match.start(), cnpj_pos)
                results.append((match.group(), score))
                
        return results
    
    def _find_formal_names(self, text: str, cnpj_pos: int) -> List[tuple]:
        """Find organization names using formal patterns"""
        patterns = [
            r'(?:instituto|universidade|fundação|fundacao|empresa|companhia)\s+(?:[\w\s]+(?:\s+(?:de|do|da|dos|das)\s+[\w\s]+)*)',
            r'(?:[\w\s]+(?:\s+(?:de|do|da|dos|das)\s+[\w\s]+)*(?:\s+(?:ltda|s\.?/?a|sociedade|instituto|empresa)))'
        ]
        
        results = []
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                name = self._normalize_name(match.group())
                if not self._is_junk(name):
                    score = self._calculate_score(name, match.start(), cnpj_pos)
                    results.append((name, score))
                    
        return results
    
    def _find_spacy_orgs(self, text: str, cnpj_pos: int) -> List[tuple]:
        """Find organizations using spaCy NER"""
        doc = self.nlp(text)
        results = []
        
        for ent in doc.ents:
            if ent.label_ == 'ORG':
                name = ent.text.strip()
                if not self._is_junk(name):
                    score = self._calculate_score(name, ent.start_char, cnpj_pos)
                    results.append((name, score))
                    
        return results
    
    def _normalize_name(self, name: str) -> str:
        """Normalize organization name capitalization"""
        words = name.strip().split()
        normalized = []
        
        for word in words:
            if word.lower() in {'de', 'do', 'da', 'dos', 'das'}:
                normalized.append(word.lower())
            else:
                normalized.append(word.capitalize())
                
        return ' '.join(normalized)
    
    def _is_junk(self, text: str) -> bool:
        """Check if text is a generic term or header"""
        junk_terms = {
            "UNIÃO", "ESTADO", "MUNICÍPIO", "GOVERNO", "PREFEITURA",
            "TERMO", "ADITIVO", "ACORDO", "COOPERAÇÃO", "COOPERACAO",
            "PRORROGAÇÃO", "PRORROGACAO", "OBJETO"
        }
        
        upper = text.upper()
        return (
            any(term in upper for term in junk_terms) or
            len(text.split()) < 2
        )
    
    def _calculate_score(self, name: str, pos: int, cnpj_pos: int) -> float:
        """Calculate candidate score based on position and characteristics"""
        distance_score = 1.0 / (1 + abs(pos - cnpj_pos))
        length_score = len(name.split()) / 10.0
        caps_score = 0.2 if sum(1 for c in name if c.isupper()) / len(name) > 0.4 else 0
        
        return distance_score + length_score + caps_score
    
    def _extract_cnpj(self, texto: str) -> str:
        """Extract CNPJ from text"""
        cnpjs = self._extract_cnpj_list(texto)
        return ", ".join(cnpj for cnpj in cnpjs if cnpj != self.TRIBUNAL_CNPJ)
    
    def _extract_cnpj_list(self, texto: str) -> List[str]:
        """Extract all CNPJs from text"""
        return re.findall(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}', texto)
    
    def _extract_objeto(self, texto: str) -> str:
        """Extract object description from text"""
        match = re.search(
            r'CLÁUSULA\s*PRIMEIRA\s*–\s*DO\s*OBJETO\s*(.*?)(?=\s*CLÁUSULA\s*SEGUNDA|\Z)',
            texto,
            re.DOTALL | re.IGNORECASE
        )
        return match.group(1).strip() if match else texto[:1000]
    
    def _extract_ano(self, texto: str) -> str:
        """Extract year from text"""
        match = re.search(r'Nº\s*\d+/(\d{4})', texto, re.IGNORECASE)
        return match.group(1) if match else ""