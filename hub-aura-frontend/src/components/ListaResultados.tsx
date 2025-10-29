import { List, ListItemButton, ListItemText, Divider, Typography, Box } from '@mui/material';

interface Parceria {
  id: number;
  razao_social: string | null;
  objeto: string | null;
  ano_do_termo: number | null;
}

interface ListaResultadosProps {
  resultados: Parceria[];
  // Nova propriedade: uma função que será chamada com o ID do item clicado.
  onItemClick: (id: number) => void;
}

// Corrige casos de "mojibake" quando strings vindas do backend foram codificadas em latin1
const fixEncoding = (s: string | null | undefined) => {
  if (!s) return s;
  try {
    // decodeURIComponent(escape(...)) é uma técnica compatível em browsers para converter
    // strings que deveriam estar em latin1 mas foram interpretadas como UTF-8.
    // Não é perfeita, mas resolve casos comuns de 'CooperaÃ§Ã£o' -> 'Cooperação'.
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    return decodeURIComponent(escape(s));
  } catch (e) {
    return s;
  }
};

const ListaResultados = ({ resultados, onItemClick }: ListaResultadosProps) => {
  if (resultados.length === 0) {
    return null;
  }

  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h6">Resultados da Busca</Typography>
      <List>
        {resultados.map((item, index) => (
          <div key={item.id}>
            {/* Usamos ListItemButton para dar o efeito de clique */}
            <ListItemButton alignItems="flex-start" onClick={() => onItemClick(item.id)}>
              <ListItemText
                primary={fixEncoding(item.razao_social) || 'Razão Social não informada'}
                secondary={
                  <>
                    <Typography component="span" variant="body2" color="text.primary">
                      Ano: {item.ano_do_termo || 'N/A'}
                    </Typography>
                    {` — ${fixEncoding(item.objeto)?.substring(0, 200) ?? 'Objeto não informado.'}...`}
                  </>
                }
              />
            </ListItemButton>
            {index < resultados.length - 1 && <Divider component="li" />}
          </div>
        ))}
      </List>
    </Box>
  );
};

export default ListaResultados;