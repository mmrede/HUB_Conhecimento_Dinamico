"""
Gerador de PDF do Dashboard de Qualidade Semântica
"""
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime

def create_dashboard_pdf():
    """Cria PDF do dashboard de qualidade semântica"""
    
    filename = "c:/Users/manoe/hub_aura/Dashboard_Qualidade_Semantica.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4,
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    # Container para os elementos
    story = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilo customizado para título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#764ba2'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )
    
    normal_style = styles['Normal']
    
    # CABEÇALHO
    story.append(Paragraph("📊 DASHBOARD DE QUALIDADE SEMÂNTICA", title_style))
    story.append(Paragraph("Análise Comparativa de Busca com IA - HUB AURA TCE", subtitle_style))
    story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", subtitle_style))
    story.append(Spacer(1, 0.5*cm))
    
    # RESUMO EXECUTIVO
    story.append(Paragraph("🏆 RESUMO EXECUTIVO", heading2_style))
    
    summary_data = [
        ['Métrica', 'Valor', 'Avaliação'],
        ['Performance Média', '177ms', 'Excelente'],
        ['Score Médio Global', '50.30%', 'Bom'],
        ['Consistência', 'σ=0.019', 'Alta'],
        ['Descoberta Semântica', '47%', 'Boa'],
    ]
    
    summary_table = Table(summary_data, colWidths=[6*cm, 4*cm, 4*cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 0.8*cm))
    
    # RANKING
    story.append(Paragraph("🏅 RANKING DE QUALIDADE SEMÂNTICA", heading2_style))
    
    ranking_data = [
        ['Posição', 'Query', 'Score Geral', 'Score Médio', 'Performance'],
        ['🥇 1º', 'cooperação técnica com universidades', '53.78', '66.66%', '111ms'],
        ['🥈 2º', 'capacitação em inteligência', '46.15', '63.42%', '326ms'],
        ['🥉 3º', 'estágio em belo horizonte', '24.66', '20.82%', '94ms'],
    ]
    
    ranking_table = Table(ranking_data, colWidths=[2*cm, 6*cm, 2.5*cm, 2.5*cm, 2*cm])
    ranking_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#FFD700')),  # Ouro
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#C0C0C0')),  # Prata
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#CD7F32')),  # Bronze
    ]))
    
    story.append(ranking_table)
    story.append(Spacer(1, 0.8*cm))
    
    # ANÁLISE DETALHADA DO VENCEDOR
    story.append(Paragraph("🔍 ANÁLISE DETALHADA DO VENCEDOR", heading2_style))
    story.append(Paragraph("<b>Query Vencedora:</b> 'cooperação técnica com universidades'", normal_style))
    story.append(Spacer(1, 0.3*cm))
    
    winner_text = """
    <b>Por que venceu?</b><br/>
    • Score máximo de 70.40% - Único a ultrapassar 70%<br/>
    • 100% de resultados relevantes - Todos os 10 resultados acima de 50%<br/>
    • Consistência excepcional - Desvio padrão de apenas 2.54%<br/>
    • Performance rápida - 111ms de latência total<br/>
    • Equilíbrio semântico - 40% de descoberta por semântica pura
    """
    story.append(Paragraph(winner_text, normal_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Top 3 Resultados
    story.append(Paragraph("<b>Top 3 Resultados Encontrados:</b>", normal_style))
    story.append(Spacer(1, 0.3*cm))
    
    results_data = [
        ['#', 'Termo', 'Score', 'Objeto'],
        ['1', '0/2017', '70.40%', 'Adesão ao Termo de Cooperação Técnica da REDE SUSTENTA MINAS'],
        ['2', '61/2006', '69.49%', 'Fornecimento de informações cadastrais de pessoas físicas e jurídicas'],
        ['3', '0/2017', '69.34%', 'Adesão ao Termo de Cooperação Técnica da REDE SUSTENTA MINAS'],
    ]
    
    results_table = Table(results_data, colWidths=[1*cm, 2*cm, 2*cm, 10*cm])
    results_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (2, -1), 'CENTER'),
        ('ALIGN', (3, 0), (3, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    story.append(results_table)
    story.append(PageBreak())
    
    # COMPARAÇÃO DE PERFORMANCE
    story.append(Paragraph("⚡ COMPARAÇÃO DE PERFORMANCE", heading2_style))
    
    perf_data = [
        ['Query', 'Embedding', 'Busca DB', 'Total', 'Avaliação'],
        ['cooperação técnica...', '34ms', '77ms', '111ms', 'Excelente'],
        ['capacitação em inteligência', '169ms', '157ms', '326ms', 'Boa'],
        ['estágio em belo horizonte', '22ms', '72ms', '94ms', 'Excelente'],
    ]
    
    perf_table = Table(perf_data, colWidths=[5.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2*cm])
    perf_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    story.append(perf_table)
    story.append(Spacer(1, 0.8*cm))
    
    # SEMÂNTICA vs KEYWORDS
    story.append(Paragraph("🔤 ANÁLISE: SEMÂNTICA vs KEYWORDS", heading2_style))
    
    semantic_data = [
        ['Query', 'Matches Keywords', 'Semântica Pura', 'Tipo'],
        ['capacitação em inteligência', '1.5 palavras', '1/10 (10%)', 'Baseada em Keywords'],
        ['cooperação técnica...', '1.2 palavras', '4/10 (40%)', 'Híbrida Equilibrada'],
        ['estágio em belo horizonte', '0.2 palavras', '9/10 (90%)', 'Semântica Pura'],
    ]
    
    semantic_table = Table(semantic_data, colWidths=[5*cm, 3*cm, 3*cm, 4*cm])
    semantic_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    story.append(semantic_table)
    story.append(Spacer(1, 0.5*cm))
    
    interpretation = """
    <b>Interpretação:</b><br/>
    • <b>10% semântica</b>: Busca funciona principalmente por match de palavras<br/>
    • <b>40% semântica</b>: Equilíbrio ideal - usa keywords + compreensão contextual<br/>
    • <b>90% semântica</b>: IA em modo discovery (ótimo para exploração)
    """
    story.append(Paragraph(interpretation, normal_style))
    story.append(Spacer(1, 0.8*cm))
    
    # ANÁLISE TÉCNICA
    story.append(Paragraph("🤖 ANÁLISE TÉCNICA: PLN & IA", heading2_style))
    
    tech_text = """
    <b>Processamento de Linguagem Natural (PLN):</b><br/>
    • Arquitetura: Transformer-based (BERT)<br/>
    • Modelo: paraphrase-multilingual-MiniLM-L12-v2<br/>
    • Dimensões: 384 (otimizado)<br/>
    • Tokenização: WordPiece (multilíngue)<br/>
    <br/>
    <b>Capacidades de IA Demonstradas:</b><br/>
    ✓ Compreensão Semântica: Entende significado além de palavras<br/>
    ✓ Transferência de Conhecimento: Pré-treinado em milhões de textos<br/>
    ✓ Representação Contextual: Embeddings capturam contexto<br/>
    ✓ Similaridade Vetorial: Métrica de cosseno para ranking<br/>
    ✓ Multilinguismo: Suporte nativo para português
    """
    story.append(Paragraph(tech_text, normal_style))
    story.append(Spacer(1, 0.8*cm))
    
    # MÉTRICAS DE AVALIAÇÃO
    metrics_data = [
        ['Métrica', 'Resultado', 'Classificação'],
        ['Consistência dos Scores', 'σ=0.019', 'Alta'],
        ['Poder de Discriminação', 'range=0.053', 'Moderada'],
        ['Cobertura Semântica', '4.7/10 sem keywords', 'Boa'],
        ['Performance Geral', '177ms', 'Excelente'],
    ]
    
    metrics_table = Table(metrics_data, colWidths=[6*cm, 4*cm, 4*cm])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    story.append(metrics_table)
    story.append(PageBreak())
    
    # CONCLUSÕES
    story.append(Paragraph("💡 CONCLUSÕES E INSIGHTS", heading2_style))
    
    conclusions = """
    <b>✓ Pontos Fortes do Sistema:</b><br/>
    1. <b>Consistência</b>: Todas as queries retornam resultados (mesmo específicas)<br/>
    2. <b>Performance</b>: Latência média de 177ms (excelente para produção)<br/>
    3. <b>Descoberta Semântica</b>: 47% dos resultados encontrados por semântica pura<br/>
    4. <b>Qualidade</b>: Score médio de 50.30% (aceitável para base pequena)<br/>
    <br/>
    <b>⚡ Diferencial da IA:</b><br/>
    • Query complexa vs específica: A IA performa bem em ambos os casos<br/>
    • Sinônimos e variações: Captura automaticamente sem configuração<br/>
    • Contexto semântico: Vai além de match exato de palavras<br/>
    • Robustez: Encontra resultados mesmo para queries desafiadoras<br/>
    <br/>
    <b>🚀 Recomendações de Melhoria:</b><br/>
    • <b>Fine-tuning</b>: Treinar modelo com documentos do TCE<br/>
    • <b>Enriquecimento</b>: Adicionar metadados aos embeddings<br/>
    • <b>Base de dados</b>: Expandir quantidade de documentos indexados<br/>
    • <b>Cache</b>: Implementar cache para queries frequentes
    """
    story.append(Paragraph(conclusions, normal_style))
    story.append(Spacer(1, 1*cm))
    
    # AVALIAÇÃO FINAL
    final_box_style = ParagraphStyle(
        'FinalBox',
        parent=styles['Normal'],
        fontSize=14,
        alignment=TA_CENTER,
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    story.append(Paragraph("🎓 AVALIAÇÃO FINAL", heading2_style))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("<font size=36 color='#667eea'><b>B</b></font>", final_box_style))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("<font size=14 color='#28a745'><b>✓ BOM - Pronto para Produção</b></font>", final_box_style))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "Sistema operacional e eficaz para queries bem formuladas.<br/>Melhorias opcionais podem aumentar ainda mais a precisão.",
        ParagraphStyle('Center', parent=normal_style, alignment=TA_CENTER)
    ))
    
    # Gerar PDF
    doc.build(story)
    
    return filename

if __name__ == "__main__":
    print("\n🚀 Gerando PDF do Dashboard de Qualidade Semântica...\n")
    filename = create_dashboard_pdf()
    print(f"✅ PDF gerado com sucesso!")
    print(f"📄 Arquivo: {filename}\n")
