import { useState } from 'react';
import { Container, Typography, Box, Pagination, Button, ButtonGroup, AppBar, Toolbar } from '@mui/material';
import axios from 'axios';
import { API_BASE_URL } from './config/api';
import logoAura from './assets/aura-tce-logo.png';

// Importe todos os seus componentes
import Busca from './components/Busca';
import ListaResultados from './components/ListaResultados';
import DetalheParceria from './components/DetalheParceria';
import PaginaUpload from './components/PaginaUpload'; // 1. Importa o novo componente

// ... (suas interfaces ParceriaResumida e ParceriaDetalhada permanecem as mesmas) ...
interface ParceriaResumida { id: number; razao_social: string | null; objeto: string | null; ano_do_termo: number | null; }
interface ParceriaDetalhada { id: number; numero_do_termo: string | null; ano_do_termo: number | null; cpf_cnpj: string | null; razao_social: string | null; objeto: string | null; plano_de_trabalho: string | null; data_da_assinatura: string | null; data_de_publicacao: string | null; vigencia: string | null; situacao: string | null; similarity_score?: number | null; }

const ITENS_POR_PAGINA = 10;

function App() {
  // 2. Novo estado para controlar a visão atual
  const [view, setView] = useState<'busca' | 'upload'>('busca'); 
  
  // ... (todos os outros estados de 'busca' que você já tem) ...
  const [resultados, setResultados] = useState<ParceriaResumida[]>([]);
  const [mensagem, setMensagem] = useState('');
  const [loading, setLoading] = useState(false);
  const [parceriaSelecionada, setParceriaSelecionada] = useState<ParceriaDetalhada | null>(null);
  const [termoBusca, setTermoBusca] = useState("");
  const [paginaAtual, setPaginaAtual] = useState(1);
  const [totalDeItens, setTotalDeItens] = useState(0);

  const [usarBuscaSemantica, setUsarBuscaSemantica] = useState(true);

  const executarBusca = async (termo: string, pagina: number, semantica: boolean = true) => {
    setLoading(true);
    setMensagem('');
    if (pagina === 1) {
      setResultados([]);
    }
    setParceriaSelecionada(null);
    const skip = (pagina - 1) * ITENS_POR_PAGINA;
    
    try {
      const endpoint = semantica ? '/api/v1/parcerias/semantic-busca' : '/api/v1/parcerias/busca';
      const response = await axios.get(`${API_BASE_URL}${endpoint}`, {
        params: { termo: termo, skip: skip, limit: ITENS_POR_PAGINA }
      });
      
      setResultados(response.data.items);
      setTotalDeItens(response.data.total_items);
      
      if (response.data.total_items === 0) {
        setMensagem('Nenhum resultado encontrado.');
      }
    } catch (error) {
      console.error("Erro ao buscar dados:", error);
      setMensagem('Falha ao conectar com o servidor.');
      setTotalDeItens(0);
      setResultados([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (termo: string, semantica?: boolean) => {
    if (!termo.trim()) {
      setResultados([]);
      setMensagem('');
      setTotalDeItens(0);
      return;
    }
    const usarSemantica = semantica !== undefined ? semantica : usarBuscaSemantica;
    setUsarBuscaSemantica(usarSemantica);
    setTermoBusca(termo);
    setPaginaAtual(1);
    executarBusca(termo, 1, usarSemantica);
  };

  const handlePageChange = (_event: React.ChangeEvent<unknown>, value: number) => {
    setPaginaAtual(value);
    executarBusca(termoBusca, value, usarBuscaSemantica);
  };

  const handleSelectItem = async (id: number) => {
    setLoading(true);
    setMensagem('');
    try {
      const response = await axios.get(`${API_BASE_URL}/api/v1/parcerias/${id}`);
      setParceriaSelecionada(response.data);
    } catch (error) {
      console.error("Erro ao buscar detalhes:", error);
      setMensagem('Não foi possível carregar os detalhes.');
    } finally {
      setLoading(false);
    }
  };

  const handleVoltar = () => {
    setParceriaSelecionada(null);
    setMensagem('');
  };

  const totalPaginas = Math.ceil(totalDeItens / ITENS_POR_PAGINA);


  return (
    <>
      {/* Header com logo AURA TCE */}
      <AppBar position="static" sx={{ bgcolor: '#8B0000', mb: 2 }}>
        <Toolbar sx={{ justifyContent: 'center', py: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <img src={logoAura} alt="AURA TCE" style={{ height: '80px' }} />
          </Box>
        </Toolbar>
      </AppBar>

      <Container maxWidth="md">
        <Typography 
          variant="h4" 
          component="h1" 
          align="center" 
          sx={{ 
            my: 3,
            color: '#003366',
            fontWeight: 600
          }}
        >
          Hub de Conhecimento - Instrumentos de Parceria
        </Typography>

      {/* 3. Botões para alternar a visão */}
      <Box sx={{ display: 'flex', justifyContent: 'center', mb: 4 }}>
        <ButtonGroup variant="outlined" aria-label="outlined button group">
          <Button onClick={() => setView('busca')} variant={view === 'busca' ? 'contained' : 'outlined'}>Buscar Acordos</Button>
          <Button onClick={() => setView('upload')} variant={view === 'upload' ? 'contained' : 'outlined'}>Adicionar Novo Acordo</Button>
        </ButtonGroup>
      </Box>

      {/* 4. Renderização condicional da visão */}
      {view === 'busca' ? (
        <>
          {parceriaSelecionada ? (
            <DetalheParceria parceria={parceriaSelecionada} onVoltar={handleVoltar} />
          ) : (
            <>
              <Busca onSearch={handleSearch} loading={loading} />
              {/* ... (resto da sua lógica de loading, mensagem e resultados da busca) ... */}
              {!loading && mensagem && <Typography color="text.secondary" align="center" sx={{mt:4}}>{mensagem}</Typography>}
              <ListaResultados resultados={resultados} onItemClick={handleSelectItem} />
              {totalPaginas > 1 && !loading && (
                <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
                  <Pagination count={totalPaginas} page={paginaAtual} onChange={handlePageChange} color="primary" />
                </Box>
              )}
            </>
          )}
        </>
      ) : (
        <PaginaUpload />
      )}
      </Container>
    </>
  );
}

export default App;