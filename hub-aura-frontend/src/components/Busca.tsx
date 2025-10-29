import { useState } from 'react';
import { TextField, Button, Box, FormControlLabel, Switch, Tooltip, Typography } from '@mui/material';

// Adicionamos a propriedade 'loading' para controlar o estado de desabilitado.
interface BuscaProps {
  onSearch: (termo: string, semantica?: boolean) => void;
  loading: boolean; 
}

const Busca = ({ onSearch, loading }: BuscaProps) => {
  const [termo, setTermo] = useState('');
  const [buscaSemantica, setBuscaSemantica] = useState(true);

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    onSearch(termo, buscaSemantica);
  };

  return (
    <Box 
      component="form" 
      onSubmit={handleSubmit} 
      sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}
    >
      <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
        <TextField
          fullWidth
          variant="outlined"
          label="Buscar por termo, objeto ou parceiro..."
          value={termo}
          onChange={(e) => setTermo(e.target.value)}
          // Desabilita o campo se 'loading' for verdadeiro.
          disabled={loading} 
        />
        <Button 
          type="submit" 
          variant="contained" 
          size="large"
          // Desabilita o botão se 'loading' for verdadeiro.
          disabled={loading}
        >
          Buscar
        </Button>
      </Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          Dica: frases funcionam melhor com a Busca Semântica (IA)
        </Typography>
        <Tooltip title="Busca semântica usa IA para encontrar resultados por significado, não apenas palavras-chave exatas">
          <FormControlLabel
            control={
              <Switch
                checked={buscaSemantica}
                onChange={(e) => setBuscaSemantica(e.target.checked)}
                disabled={loading}
              />
            }
            label="Busca Semântica (IA)"
          />
        </Tooltip>
      </Box>
    </Box>
  );
};

export default Busca;