import { useState } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config/api';
import { Box, Button, TextField, Typography, CircularProgress, Alert, Grid } from '@mui/material';

// Interface para os dados do formulário atualizada
interface FormData {
  razao_social: string;
  objeto: string;
  plano_de_trabalho: string;
  cpf_cnpj: string; // Corresponde ao nome da coluna no DB
  ano_do_termo: string; // Mantemos como string no form para facilitar a edição
}

const PaginaUpload = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [formData, setFormData] = useState<FormData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<{type: 'success' | 'error', text: string} | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setSelectedFile(event.target.files[0]);
      setFormData(null);
      setMessage(null);
    }
  };

  const handleProcess = async () => {
    if (!selectedFile) {
      setMessage({ type: 'error', text: 'Por favor, selecione um arquivo PDF.' });
      return;
    }
    const uploadData = new FormData();
    uploadData.append('file', selectedFile);
    setIsLoading(true);
    setMessage(null);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/v1/processar-documento`, uploadData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      // Preenche o formulário com as novas sugestões da IA
      setFormData({
        razao_social: response.data.razao_social_sugerida,
        objeto: response.data.objeto_sugerido,
        plano_de_trabalho: '', // Inicia vazio, usuário pode preencher manualmente
        cpf_cnpj: response.data.cnpj_sugerido,
        ano_do_termo: response.data.ano_do_termo_sugerido,
      });
    } catch (error) {
      console.error("Erro ao processar o documento:", error);
      setMessage({ type: 'error', text: 'Falha ao processar o documento.' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleFormChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (formData) {
      setFormData({
        ...formData,
        [event.target.name]: event.target.value,
      });
    }
  };

  const handleSave = async () => {
    if (!formData) return;
    setIsLoading(true);
    setMessage(null);
    try {
      // Prepara os dados para envio, convertendo ano para número
      const payload = {
        ...formData,
        ano_do_termo: formData.ano_do_termo ? parseInt(formData.ano_do_termo, 10) : null,
      };
      await axios.post(`${API_BASE_URL}/api/v1/parcerias`, payload);
      setMessage({ type: 'success', text: 'Parceria salva com sucesso!' });
      setFormData(null);
      setSelectedFile(null);
    } catch (error) {
      console.error("Erro ao salvar a parceria:", error);
      setMessage({ type: 'error', text: 'Falha ao salvar a parceria.' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box sx={{ mt: 4, p: 2, border: '1px dashed grey', borderRadius: '4px' }}>
      <Typography variant="h5" gutterBottom> Adicionar Novo Acordo via IA </Typography>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <Button variant="contained" component="label"> Selecionar PDF
          <input type="file" hidden accept=".pdf" onChange={handleFileChange} />
        </Button>
        {selectedFile && <Typography variant="body2">{selectedFile.name}</Typography>}
        <Button onClick={handleProcess} disabled={!selectedFile || isLoading}> Processar com IA </Button>
      </Box>
      {isLoading && <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}><CircularProgress /></Box>}
      {message && <Alert severity={message.type} sx={{ my: 2 }}>{message.text}</Alert>}

      {formData && (
        <Box component="form" sx={{ mt: 4 }}>
          <Typography variant="h6" gutterBottom>Valide os Dados Extraídos</Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={8}>
              <TextField fullWidth margin="normal" label="Razão Social do Parceiro" name="razao_social" value={formData.razao_social} onChange={handleFormChange}/>
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField fullWidth margin="normal" label="CNPJ" name="cpf_cnpj" value={formData.cpf_cnpj} onChange={handleFormChange} />
            </Grid>
            <Grid item xs={12} sm={4}>
               <TextField fullWidth margin="normal" label="Ano do Termo" name="ano_do_termo" value={formData.ano_do_termo} onChange={handleFormChange} />
            </Grid>
          </Grid>
          <TextField fullWidth margin="normal" label="Objeto do Acordo" name="objeto" multiline rows={10} value={formData.objeto} onChange={handleFormChange} />
          
          <TextField 
            fullWidth 
            margin="normal" 
            label="Plano de Trabalho" 
            name="plano_de_trabalho" 
            multiline 
            rows={8} 
            value={formData.plano_de_trabalho} 
            onChange={handleFormChange}
            placeholder="Descreva o plano de trabalho detalhado da parceria, incluindo objetivos, atividades previstas, metodologias e resultados esperados..."
            helperText="Campo opcional. Enriquece a busca semântica do sistema."
          />
          
          <Button variant="contained" color="primary" onClick={handleSave} disabled={isLoading} sx={{ mt: 2 }}> Salvar Parceria </Button>
        </Box>
      )}
    </Box>
  );
};

export default PaginaUpload;