import { useState } from 'react';
import { Box, Typography, Button } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';

interface PlanoTrabalhoProps {
  planoDeTrabalho: string | null;
}

const PlanoTrabalho = ({ planoDeTrabalho }: PlanoTrabalhoProps) => {
  const [expanded, setExpanded] = useState(false);

  if (!planoDeTrabalho) {
    return null;
  }

  const handleToggle = () => {
    setExpanded(!expanded);
  };

  // Limitar preview a 200 caracteres
  const preview = planoDeTrabalho.substring(0, 200);
  const needsExpansion = planoDeTrabalho.length > 200;

  return (
    <Box sx={{ my: 2 }}>
      <Typography variant="h6" gutterBottom>
        📋 Plano de Trabalho
      </Typography>
      
      <Box 
        sx={{ 
          p: 2, 
          bgcolor: 'grey.50', 
          borderRadius: 1,
          borderLeft: 4,
          borderColor: 'primary.main'
        }}
      >
        <Typography 
          variant="body1" 
          sx={{ 
            whiteSpace: 'pre-wrap', 
            textAlign: 'justify',
            lineHeight: 1.7
          }}
        >
          {expanded ? planoDeTrabalho : preview}
          {!expanded && needsExpansion && '...'}
        </Typography>

        {needsExpansion && (
          <Button
            onClick={handleToggle}
            startIcon={expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            sx={{ mt: 1 }}
            size="small"
          >
            {expanded ? 'Mostrar menos' : 'Ler mais'}
          </Button>
        )}
      </Box>
    </Box>
  );
};

export default PlanoTrabalho;
