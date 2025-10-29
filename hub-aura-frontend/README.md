# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:


## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

## Execução do frontend (desenvolvimento)

Instruções rápidas para rodar o servidor de desenvolvimento do frontend de forma que ele fique acessível em `http://localhost:5173` e, se necessário, por outras máquinas na rede.

- Rodar em modo desenvolvimento (bind em todas as interfaces):

```powershell
cd hub-aura-frontend
npm run dev
# ou, se quiser forçar no momento da execução:
npm run dev -- --host
```

Observações:
- O script `dev` já foi alterado para usar `vite --host`, então `npm run dev` por padrão já expõe para `0.0.0.0` (ou pelo menos abre para localhost/IPv6). Se preferir garantir explicitamente, use `npm run dev -- --host`.
- Em Windows, se você precisa que o servidor seja acessível a partir de outra máquina (ou de um container diferente), confirme as regras do Firewall do Windows para permitir conexões na porta `5173`. Normalmente não é necessário se você só acessar do mesmo host.

Exemplo (verificar status via curl):

```powershell
curl.exe -I http://localhost:5173
curl.exe -I http://[::1]:5173
```

Se o navegador continuar mostrando o app como "fora do ar":
- Verifique se o processo do Vite está rodando (procure `node.exe`).
- Rode `npm run dev` em um terminal em foreground para ver logs (build, erros, HMR). Isso facilita descobrir problemas de bundling ou crashes.
- Para expor em ambientes de desenvolvimento mais controlados (docker/VM), considere rodar com `--host 0.0.0.0` e ajustar firewall/rotas de NAT conforme aplicável.

Se quiser, eu posso também commitar essa mudança em uma branch dedicada e criar uma mensagem de commit explicativa.
