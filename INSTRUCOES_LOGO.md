# Instruções para Adicionar a Logo AURA TCE

## Passos para Salvar a Imagem

A logo AURA TCE que você forneceu precisa ser salva em 2 locais:

### 1. Para uso no código React (src/assets/)
- Salve a imagem como: `hub-aura-frontend/src/assets/aura-tce-logo.png`
- Este arquivo será importado no App.tsx

### 2. Para uso como favicon (public/)
- Salve a imagem como: `hub-aura-frontend/public/aura-tce-logo.png`
- Este arquivo será usado como ícone da aba do navegador

## Como Salvar no Windows

### Opção 1: Copiar/Colar via Explorador de Arquivos
1. Baixe ou tenha a imagem AURA TCE salva em algum local
2. Renomeie para `aura-tce-logo.png`
3. Copie para:
   - `C:\Users\manoe\hub_aura\hub-aura-frontend\src\assets\aura-tce-logo.png`
   - `C:\Users\manoe\hub_aura\hub-aura-frontend\public\aura-tce-logo.png`

### Opção 2: Via PowerShell
```powershell
# Supondo que a imagem está em C:\Downloads\aura-tce.png
Copy-Item "C:\Downloads\aura-tce.png" "C:\Users\manoe\hub_aura\hub-aura-frontend\src\assets\aura-tce-logo.png"
Copy-Item "C:\Downloads\aura-tce.png" "C:\Users\manoe\hub_aura\hub-aura-frontend\public\aura-tce-logo.png"
```

## Mudanças Já Aplicadas no Código

✅ `index.html`: Título atualizado para "AURA TCE - Hub de Conhecimento" e favicon apontando para a logo
✅ `App.tsx`: Header com AppBar contendo a logo, cores personalizadas (vermelho #8B0000 e azul #003366)
✅ Import da logo adicionado: `import logoAura from './assets/aura-tce-logo.png';`

## Depois de Salvar as Imagens

Reinicie o frontend para ver as mudanças:
```powershell
cd hub-aura-frontend
npm run dev
```

Você verá:
- Header vermelho com a logo AURA TCE centralizada
- Título "Hub de Conhecimento - Instrumentos de Parceria" em azul marinho
- Favicon da logo na aba do navegador
