import { useState } from 'react';
import { TextField, Button, Box, FormControlLabel, Switch, Tooltip, Typography, CircularProgress } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';

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
          disabled={loading}
          InputProps={{
            endAdornment: loading ? (
              <CircularProgress size={20} />
            ) : null,
          }}
        />
        <Button 
          type="submit" 
          variant="contained" 
          size="large"
          disabled={loading}
          startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <SearchIcon />}
          sx={{ minWidth: '120px' }}
        >
          {loading ? 'Buscando...' : 'Buscar'}
        </Button>
      </Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          {buscaSemantica 
            ? "✨ Busca enriquecida: analisa objeto + plano de trabalho para resultados mais precisos" 
            : "Busca tradicional por palavras-chave"}
        </Typography>
        <Tooltip title="Busca semântica V3 usa IA para analisar objeto e plano de trabalho, encontrando resultados por significado e contexto completo">
          <FormControlLabel
            control={
              <Switch
                checked={buscaSemantica}
                onChange={(e) => setBuscaSemantica(e.target.checked)}
                disabled={loading}
              />
            }
            label="Busca Semântica V3 (IA)"
          />
        </Tooltip>
      </Box>
    </Box>
  );
};

export default Busca;