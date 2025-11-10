import { List, ListItemButton, ListItemText, Divider, Typography, Box, Chip, Stack } from '@mui/material';
import DescriptionIcon from '@mui/icons-material/Description';

interface Parceria {
  id: number;
  razao_social: string | null;
  objeto: string | null;
  ano_do_termo: number | null;
  plano_de_trabalho?: string | null;
  similarity_score?: number | null;
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

const getSimilarityColor = (score: number): 'success' | 'warning' | 'default' => {
  if (score >= 0.6) return 'success';
  if (score >= 0.4) return 'warning';
  return 'default';
};

const ListaResultados = ({ resultados, onItemClick }: ListaResultadosProps) => {
  if (resultados.length === 0) {
    return null;
  }

  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        Resultados da Busca ({resultados.length})
      </Typography>
      <List>
        {resultados.map((item, index) => (
          <div key={item.id}>
            {/* Usamos ListItemButton para dar o efeito de clique */}
            <ListItemButton 
              alignItems="flex-start" 
              onClick={() => onItemClick(item.id)}
              sx={{ 
                py: 2,
                '&:hover': {
                  backgroundColor: 'action.hover',
                }
              }}
            >
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                    <Typography variant="h6" component="span">
                      {fixEncoding(item.razao_social) || 'Razão Social não informada'}
                    </Typography>
                    {item.similarity_score !== undefined && item.similarity_score !== null && (
                      <Chip 
                        label={`${(item.similarity_score * 100).toFixed(1)}% similar`} 
                        size="small" 
                        color={getSimilarityColor(item.similarity_score)}
                        sx={{ fontWeight: 'bold' }}
                      />
                    )}
                  </Box>
                }
                secondary={
                  <Stack spacing={1} sx={{ mt: 1 }}>
                    <Typography component="div" variant="body2" color="text.secondary">
                      <strong>Ano:</strong> {item.ano_do_termo || 'N/A'}
                    </Typography>
                    
                    <Typography component="div" variant="body2" color="text.primary">
                      <strong>Objeto:</strong> {fixEncoding(item.objeto)?.substring(0, 200) ?? 'Objeto não informado.'}
                      {item.objeto && item.objeto.length > 200 && '...'}
                    </Typography>
                    
                    {item.plano_de_trabalho && (
                      <Box 
                        sx={{ 
                          display: 'flex', 
                          alignItems: 'flex-start', 
                          gap: 0.5,
                          p: 1, 
                          bgcolor: 'action.hover', 
                          borderRadius: 1,
                          borderLeft: 3,
                          borderColor: 'primary.main'
                        }}
                      >
                        <DescriptionIcon sx={{ fontSize: 18, color: 'primary.main', mt: 0.2 }} />
                        <Box>
                          <Typography variant="caption" color="primary" sx={{ fontWeight: 'bold', display: 'block' }}>
                            Plano de Trabalho
                          </Typography>
                          <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.875rem' }}>
                            {fixEncoding(item.plano_de_trabalho)?.substring(0, 150) ?? ''}
                            {item.plano_de_trabalho.length > 150 && '... (clique para ver completo)'}
                          </Typography>
                        </Box>
                      </Box>
                    )}
                  </Stack>
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