# INSTRUÇÕES PARA EXECUTAR TESTE DE BUSCA SEMÂNTICA

## Passo 1: Abrir dois terminais PowerShell

Abra dois terminais PowerShell **separados** (fora do VS Code):
- Pressione Win+R, digite `powershell` e pressione Enter
- Faça isso duas vezes para ter dois terminais

## Passo 2: Iniciar o Backend (Terminal 1)

No primeiro terminal PowerShell, execute:

```powershell
cd C:\Users\manoe\hub_aura
C:/Users/manoe/hub_aura/venv/Scripts/python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8002
```

Aguarde até ver as mensagens:
- "Modelo de IA (spaCy) carregado com sucesso."
- "Modelo sentence-transformers carregado com sucesso (384 dims)."
- "Application startup complete."

## Passo 3: Executar o Teste (Terminal 2)

No segundo terminal PowerShell, aguarde 10 segundos após o backend iniciar e execute:

```powershell
cd C:\Users\manoe\hub_aura
C:/Users/manoe/hub_aura/venv/Scripts/python.exe simple_test.py
```

Este script irá:
- Executar a busca semântica com a query: "quais os melhores parceiros para uma capacitação em inteligência"
- Retornar os 10 primeiros resultados
- Mostrar os scores de similaridade
- Calcular estatísticas

## Passo 4: Relatório Completo (Opcional)

Para o relatório detalhado completo, execute:

```powershell
C:/Users/manoe/hub_aura/venv/Scripts/python.exe test_semantic_search.py
```

Este script gera análise mais completa com:
- Análise de performance da IA
- Detalhamento de cada resultado
- Análise de relevância por keywords
- Estatísticas agregadas
- Recomendações

## Alternativa: Usar o Frontend

Se preferir testar pela interface web:

1. Certifique-se que o backend está rodando (Passo 2)
2. Inicie o frontend em outro terminal:
   ```powershell
   cd C:\Users\manoe\hub_aura\hub-aura-frontend
   npm run dev
   ```
3. Abra http://localhost:5173 no navegador
4. Digite a query na busca e clique em "Buscar Parcerias"

## Observações

- O backend precisa estar rodando para os testes funcionarem
- A inicialização dos modelos (spaCy + sentence-transformers) pode levar 5-10 segundos
- Os terminais devem ficar abertos durante o teste
- Para parar o backend, pressione Ctrl+C no terminal onde ele está rodando
