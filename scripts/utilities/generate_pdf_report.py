"""
Script para converter o relatório de análise para PDF
"""
import os
from pathlib import Path

try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    print("⚠️ weasyprint não disponível. Tentando alternativas...")

try:
    import markdown
    from xhtml2pdf import pisa
    MARKDOWN_PDF_AVAILABLE = True
except ImportError:
    MARKDOWN_PDF_AVAILABLE = False
    print("⚠️ markdown + xhtml2pdf não disponíveis.")

def convert_markdown_to_html(md_file: str) -> str:
    """Converte markdown para HTML com estilo"""
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    if not MARKDOWN_PDF_AVAILABLE:
        import markdown2
        html_content = markdown2.markdown(md_content, extras=['tables', 'fenced-code-blocks'])
    else:
        html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code_blocks'])
    
    # Template HTML com estilo
    html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page {{
            size: A4;
            margin: 2cm;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
        }}
        h1 {{
            color: #667eea;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-top: 30px;
        }}
        h2 {{
            color: #764ba2;
            border-bottom: 2px solid #764ba2;
            padding-bottom: 8px;
            margin-top: 25px;
        }}
        h3 {{
            color: #667eea;
            margin-top: 20px;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #667eea;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        blockquote {{
            border-left: 4px solid #667eea;
            padding-left: 20px;
            margin: 20px 0;
            font-style: italic;
            color: #666;
        }}
        .header {{
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .footer {{
            text-align: center;
            margin-top: 50px;
            padding: 20px;
            border-top: 2px solid #667eea;
            font-size: 0.9em;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1 style="border: none; color: white; margin: 0;">📊 Relatório de Análise de Qualidade</h1>
        <p style="margin: 10px 0 0 0;">Busca Semântica - Hub Aura</p>
    </div>
    
    {html_content}
    
    <div class="footer">
        <p>Gerado automaticamente pelo Sistema de Análise de Qualidade</p>
        <p>Hub Aura - Tribunal de Contas do Estado de Minas Gerais</p>
    </div>
</body>
</html>
"""
    return html_template

def generate_pdf_weasyprint(md_file: str, pdf_file: str):
    """Gera PDF usando WeasyPrint"""
    html_content = convert_markdown_to_html(md_file)
    HTML(string=html_content).write_pdf(pdf_file)
    print(f"✅ PDF gerado com WeasyPrint: {pdf_file}")

def generate_pdf_xhtml2pdf(md_file: str, pdf_file: str):
    """Gera PDF usando xhtml2pdf"""
    html_content = convert_markdown_to_html(md_file)
    
    with open(pdf_file, 'wb') as pdf:
        pisa_status = pisa.CreatePDF(html_content, dest=pdf)
    
    if pisa_status.err:
        print(f"❌ Erro ao gerar PDF: {pisa_status.err}")
    else:
        print(f"✅ PDF gerado com xhtml2pdf: {pdf_file}")

def generate_html_only(md_file: str, html_file: str):
    """Gera apenas HTML (fallback)"""
    html_content = convert_markdown_to_html(md_file)
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML gerado: {html_file}")
    print(f"   Use seu navegador para imprimir como PDF: Ctrl+P → Salvar como PDF")

def main():
    """Gera o PDF do relatório"""
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    
    md_file = project_dir / "SEMANTIC_SEARCH_ANALYSIS.md"
    pdf_file = project_dir / "SEMANTIC_SEARCH_ANALYSIS.pdf"
    html_file = project_dir / "SEMANTIC_SEARCH_ANALYSIS.html"
    
    if not md_file.exists():
        print(f"❌ Arquivo não encontrado: {md_file}")
        return
    
    print("🚀 Gerando relatório em PDF...")
    print(f"   Origem: {md_file}")
    print(f"   Destino: {pdf_file}")
    print()
    
    # Tentar diferentes métodos
    if WEASYPRINT_AVAILABLE:
        try:
            generate_pdf_weasyprint(str(md_file), str(pdf_file))
            return
        except Exception as e:
            print(f"⚠️ Erro com WeasyPrint: {e}")
    
    if MARKDOWN_PDF_AVAILABLE:
        try:
            generate_pdf_xhtml2pdf(str(md_file), str(pdf_file))
            return
        except Exception as e:
            print(f"⚠️ Erro com xhtml2pdf: {e}")
    
    # Fallback: gerar HTML
    print("📄 Gerando HTML para conversão manual...")
    generate_html_only(str(md_file), str(html_file))
    print()
    print("💡 Para converter para PDF:")
    print(f"   1. Abra o arquivo: {html_file}")
    print("   2. Pressione Ctrl+P (ou Cmd+P no Mac)")
    print("   3. Selecione 'Salvar como PDF'")
    print(f"   4. Salve como: {pdf_file}")

if __name__ == "__main__":
    main()
