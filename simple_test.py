"""
Script simplificado para teste de busca semântica
Executar em um terminal PowerShell separado após iniciar o backend
"""
import requests
import json
import time

def test_search():
    query = "quais os melhores parceiros para uma capacitação em inteligência"
    url = "http://127.0.0.1:8002/api/v1/parcerias/semantic-busca"
    
    print("Executando busca semântica...")
    print(f"Query: {query}\n")
    
    start = time.time()
    
    try:
        # Fazendo GET request (conforme o endpoint espera)
        response = requests.get(
            url,
            params={'termo': query, 'limit': 10, 'skip': 0},
            timeout=30
        )
        
        elapsed = time.time() - start
        
        print(f"Status: {response.status_code}")
        print(f"Tempo: {elapsed:.3f}s\n")
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('items', [])
            
            print(f"Total de resultados: {len(results)}\n")
            print("=" * 80)
            
            for idx, item in enumerate(results, 1):
                print(f"\nRESULTADO #{idx}")
                print("-" * 80)
                print(f"Termo: {item.get('numero_do_termo')}/{item.get('ano_do_termo')}")
                print(f"Parceiro: {item.get('nome_parceiro')}")
                print(f"Similaridade: {item.get('similarity_score', 0):.4f} ({item.get('similarity_score', 0)*100:.2f}%)")
                print(f"Data: {item.get('data_assinatura')}")
                
                objeto = item.get('objeto', '')
                if objeto:
                    print(f"Objeto: {objeto[:150]}..." if len(objeto) > 150 else f"Objeto: {objeto}")
            
            print("\n" + "=" * 80)
            scores = [r.get('similarity_score', 0) for r in results]
            if scores:
                print(f"\nEstatísticas:")
                print(f"  Máximo: {max(scores):.4f}")
                print(f"  Mínimo: {min(scores):.4f}")  
                print(f"  Média: {sum(scores)/len(scores):.4f}")
        else:
            print(f"Erro: {response.text}")
            
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    test_search()
