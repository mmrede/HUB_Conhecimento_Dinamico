import { useState } from 'react';
import { Container, Typography } from '@mui/material';
import axios from 'axios';
import { API_BASE_URL } from './config/api';
import Busca from './components/Busca';
import ListaResultados from './components/ListaResultados';
import { useNavigate } from 'react-router-dom';

// Interface para definir a estrutura de uma parceria
interface Parceria {
  id: number;
  razao_social: string | null;
  objeto: string | null;
  ano_do_termo: number | null;
  plano_de_trabalho?: string | null;
  similarity_score?: number | null;
}

const PaginaBusca = () => {
    const [resultados, setResultados] = useState<Parceria[]>([]);
    const [mensagem, setMensagem] = useState('Digite um termo para iniciar a busca.');
    const [loading, setLoading] = useState(false);

  const handleSearch = async (termo: string, semantica: boolean = true) => {
        if (!termo.trim()) {
          setResultados([]);
          setMensagem('Digite um termo para iniciar a busca.');
          return;
        }

        try {
          setLoading(true);
          setMensagem('Buscando...');
          
          // Escolhe o endpoint baseado no tipo de busca
          const endpoint = semantica ? '/api/v1/parcerias/semantic-busca' : '/api/v1/parcerias/busca';

          const doRequest = async (ep: string) => axios.get(`${API_BASE_URL}${ep}`, { params: { termo } });

          let response = await doRequest(endpoint);
          let items = response.data?.items ?? [];
          let total = response.data?.total_items ?? 0;

          // Fallback inteligente: se a busca textual não encontrar nada,
          // tentar automaticamente a busca semântica sem exigir outra ação do usuário.
          if (!semantica && total === 0) {
            response = await doRequest('/api/v1/parcerias/semantic-busca');
            items = response.data?.items ?? [];
            total = response.data?.total_items ?? 0;
            setMensagem(total === 0 ? 'Nenhum resultado encontrado.' : 'Mostrando resultados por similaridade (IA).');
          } else {
            setMensagem(total === 0 ? 'Nenhum resultado encontrado.' : '');
          }

          setResultados(items);

        } catch (error) {
          console.error("Erro ao buscar dados da API:", error);
          setMensagem('Falha ao conectar com o servidor. Verifique se a API está no ar.');
          setResultados([]);
        } finally {
          setLoading(false);
        }
    };

    const navigate = useNavigate();

    const handleItemClick = (id: number) => {
      // Navega para a página de detalhe da parceria
      navigate(`/parcerias/${id}`);
    };

    return (
      <Container maxWidth="md">
        <Typography variant="h3" component="h1" align="center" sx={{ my: 4 }}>
          HUB Aura - Conhecimento Dinâmico
        </Typography>
        <Busca onSearch={handleSearch} loading={loading} />
  {mensagem && <Typography color="text.secondary" sx={{ mt: 4, textAlign: 'center' }}>{mensagem}</Typography>}
  <ListaResultados resultados={resultados} onItemClick={handleItemClick} />
      </Container>
    );
}

export default PaginaBusca;