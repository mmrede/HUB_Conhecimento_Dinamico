import { Box, Typography, Button, Paper, Divider } from '@mui/material';
import PlanoTrabalho from './PlanoTrabalho';

// Interface que espelha o seu modelo Pydantic 'Parceria'
interface ParceriaDetalhada {
  id: number;
  numero_do_termo: string | null;
  ano_do_termo: number | null;
  cpf_cnpj: string | null;
  razao_social: string | null;
  objeto: string | null;
  plano_de_trabalho: string | null;
  data_da_assinatura: string | null; 
  data_de_publicacao: string | null;
  vigencia: string | null;
  situacao: string | null;
  similarity_score?: number | null;
}

// Propriedades do componente: a parceria e a função para voltar
interface DetalheParceriaProps {
  parceria: ParceriaDetalhada;
  onVoltar: () => void;
}

const DetalheParceria = ({ parceria, onVoltar }: DetalheParceriaProps) => {
  // Função para formatar datas (ex: 2024-10-27 -> 27/10/2024)
  const formatarData = (data: string | null) => {
    if (!data) return 'Não informada';
    // Adiciona 'T00:00:00' para evitar problemas de fuso horário
    return new Date(`${data}T00:00:00`).toLocaleDateString('pt-BR');
  };

  const fixEncoding = (s: string | null | undefined): string | null => {
    if (!s) return null;
    try {
      // Mesma técnica usada no ListaResultados para mitigar mojibake
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore
      return decodeURIComponent(escape(s));
    } catch (e) {
      return s;
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 4, mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        {fixEncoding(parceria.razao_social) || 'Detalhes da Parceria'}
      </Typography>
      <Typography variant="subtitle1" color="text.secondary">
        Termo Nº: {parceria.numero_do_termo || 'N/A'}{parceria.ano_do_termo ? `/${parceria.ano_do_termo}` : ''}
      </Typography>
      
      <Divider sx={{ my: 2 }} />

      <Box sx={{ my: 2 }}>
        <Typography variant="h6">Objeto do Acordo</Typography>
        <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>{fixEncoding(parceria.objeto) || 'Não informado.'}</Typography>
      </Box>

      <PlanoTrabalho planoDeTrabalho={fixEncoding(parceria.plano_de_trabalho)} />

      {parceria.similarity_score && (
        <Box sx={{ my: 2 }}>
          <Typography variant="body2" color="text.secondary">
            <strong>Score de Similaridade:</strong> {(parceria.similarity_score * 100).toFixed(2)}%
          </Typography>
        </Box>
      )}

      <Box sx={{ my: 2 }}>
        <Typography variant="h6">Detalhes Administrativos</Typography>
        <Typography variant="body2"><strong>CPF/CNPJ:</strong> {parceria.cpf_cnpj || 'Não informado'}</Typography>
        <Typography variant="body2"><strong>Ano do Termo:</strong> {parceria.ano_do_termo || 'Não informado'}</Typography>
        <Typography variant="body2"><strong>Situação:</strong> {parceria.situacao || 'Não informada'}</Typography>
        <Typography variant="body2"><strong>Data de Assinatura:</strong> {formatarData(parceria.data_da_assinatura)}</Typography>
        <Typography variant="body2"><strong>Data de Publicação:</strong> {formatarData(parceria.data_de_publicacao)}</Typography>
        <Typography variant="body2"><strong>Vigência:</strong> {formatarData(parceria.vigencia)}</Typography>
      </Box>

      <Button variant="contained" onClick={onVoltar} sx={{ mt: 3 }}>
        Voltar para a Busca
      </Button>
    </Paper>
  );
};

export default DetalheParceria;