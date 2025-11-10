"""
Analytics and Insights Module
Módulo de Análise e Insights

Generates analytics and insights from knowledge documents.
"""

from typing import List, Dict, Any
from collections import Counter
from datetime import datetime, timedelta

from ..core.models import KnowledgeDocument


class KnowledgeAnalytics:
    """
    Generates analytics and insights from knowledge repository.
    Gera análises e insights do repositório de conhecimento.
    """
    
    def __init__(self):
        """Initialize analytics engine."""
        self.documents: List[KnowledgeDocument] = []
    
    def add_document(self, document: KnowledgeDocument):
        """Add document to analytics."""
        self.documents.append(document)
    
    def generate_insights(self) -> Dict[str, Any]:
        """
        Generate comprehensive insights from knowledge repository.
        
        Returns:
            Dictionary containing various insights
        """
        insights = {
            'total_documents': len(self.documents),
            'categories_distribution': self._get_category_distribution(),
            'top_tags': self._get_top_tags(),
            'top_concepts': self._get_top_concepts(),
            'document_types_distribution': self._get_document_types(),
            'temporal_distribution': self._get_temporal_distribution(),
            'department_distribution': self._get_department_distribution(),
            'knowledge_coverage': self._assess_knowledge_coverage(),
            'recommendations': self._generate_recommendations()
        }
        
        return insights
    
    def _get_category_distribution(self) -> Dict[str, int]:
        """Get distribution of documents by category."""
        categories = [doc.category for doc in self.documents]
        return dict(Counter(categories))
    
    def _get_top_tags(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Get most common tags across all documents.
        
        Args:
            top_n: Number of top tags to return
            
        Returns:
            List of top tags with counts
        """
        all_tags = []
        for doc in self.documents:
            all_tags.extend(doc.tags)
        
        tag_counts = Counter(all_tags)
        return [
            {'tag': tag, 'count': count}
            for tag, count in tag_counts.most_common(top_n)
        ]
    
    def _get_top_concepts(self, top_n: int = 15) -> List[Dict[str, Any]]:
        """
        Get most common key concepts across all documents.
        
        Args:
            top_n: Number of top concepts to return
            
        Returns:
            List of top concepts with counts
        """
        all_concepts = []
        for doc in self.documents:
            all_concepts.extend(doc.key_concepts)
        
        concept_counts = Counter(all_concepts)
        return [
            {'concept': concept, 'count': count}
            for concept, count in concept_counts.most_common(top_n)
        ]
    
    def _get_document_types(self) -> Dict[str, int]:
        """Get distribution of document types."""
        types = [doc.document_type.value for doc in self.documents]
        return dict(Counter(types))
    
    def _get_temporal_distribution(self) -> Dict[str, Any]:
        """Analyze temporal distribution of documents."""
        if not self.documents:
            return {}
        
        dates = [doc.created_at for doc in self.documents]
        
        # Get date range
        min_date = min(dates)
        max_date = max(dates)
        
        # Count by month
        monthly_counts = {}
        for doc in self.documents:
            month_key = doc.created_at.strftime('%Y-%m')
            monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1
        
        return {
            'earliest_document': min_date.isoformat(),
            'latest_document': max_date.isoformat(),
            'monthly_distribution': monthly_counts
        }
    
    def _get_department_distribution(self) -> Dict[str, int]:
        """Get distribution of documents by department."""
        departments = [doc.department for doc in self.documents if doc.department]
        return dict(Counter(departments))
    
    def _assess_knowledge_coverage(self) -> Dict[str, Any]:
        """
        Assess coverage of knowledge across different dimensions.
        
        Returns:
            Knowledge coverage assessment
        """
        total_docs = len(self.documents)
        
        # Category coverage
        categories = set(doc.category for doc in self.documents)
        
        # Tag diversity
        all_tags = set()
        for doc in self.documents:
            all_tags.update(doc.tags)
        
        # Average confidence
        avg_confidence = sum(doc.confidence_score for doc in self.documents) / total_docs if total_docs > 0 else 0
        
        return {
            'unique_categories': len(categories),
            'unique_tags': len(all_tags),
            'average_confidence_score': round(avg_confidence, 2),
            'documents_with_high_confidence': sum(
                1 for doc in self.documents if doc.confidence_score >= 0.7
            ),
            'coverage_score': self._calculate_coverage_score()
        }
    
    def _calculate_coverage_score(self) -> float:
        """
        Calculate overall knowledge coverage score.
        
        Returns:
            Coverage score between 0 and 1
        """
        if not self.documents:
            return 0.0
        
        score = 0.0
        
        # Category diversity (max 0.3)
        unique_categories = len(set(doc.category for doc in self.documents))
        score += min(unique_categories / 10, 0.3)
        
        # Tag richness (max 0.3)
        avg_tags_per_doc = sum(len(doc.tags) for doc in self.documents) / len(self.documents)
        score += min(avg_tags_per_doc / 10, 0.3)
        
        # Concept richness (max 0.2)
        avg_concepts_per_doc = sum(len(doc.key_concepts) for doc in self.documents) / len(self.documents)
        score += min(avg_concepts_per_doc / 10, 0.2)
        
        # Average confidence (max 0.2)
        avg_confidence = sum(doc.confidence_score for doc in self.documents) / len(self.documents)
        score += avg_confidence * 0.2
        
        return round(score, 2)
    
    def _generate_recommendations(self) -> List[str]:
        """
        Generate recommendations based on knowledge analysis.
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if not self.documents:
            return ["Adicione documentos ao repositório para começar a gerar insights."]
        
        # Check for low confidence documents
        low_confidence = sum(1 for doc in self.documents if doc.confidence_score < 0.5)
        if low_confidence > len(self.documents) * 0.2:
            recommendations.append(
                f"Revisar {low_confidence} documentos com baixa confiabilidade para melhorar a qualidade do conhecimento."
            )
        
        # Check for category balance
        category_dist = self._get_category_distribution()
        if len(category_dist) < 3:
            recommendations.append(
                "Expandir a cobertura de categorias para diversificar o conhecimento organizacional."
            )
        
        # Check for recent updates
        recent_docs = sum(
            1 for doc in self.documents 
            if doc.created_at > datetime.now() - timedelta(days=30)
        )
        if recent_docs < len(self.documents) * 0.1:
            recommendations.append(
                "Adicionar documentos recentes para manter o conhecimento atualizado."
            )
        
        # Check for tag usage
        avg_tags = sum(len(doc.tags) for doc in self.documents) / len(self.documents)
        if avg_tags < 2:
            recommendations.append(
                "Aumentar o uso de tags para melhorar a descoberta e organização do conhecimento."
            )
        
        return recommendations if recommendations else [
            "Repositório de conhecimento em bom estado. Continue adicionando e atualizando documentos."
        ]
