"""Testa e compara busca semântica v2 vs v3"""
import requests

TERMO = "cooperação técnica com universidades para pesquisa"

print("=" * 80)
print(f"COMPARAÇÃO: Busca Semântica V2 vs V3")
print(f"Termo: '{TERMO}'")
print("=" * 80)
print()

# Teste V2 (apenas objeto)
print("🔍 BUSCA V2 (apenas campo 'objeto'):")
print("-" * 80)
r2 = requests.get('http://127.0.0.1:8001/api/v1/parcerias/semantic-busca', params={
    'termo': TERMO,
    'limit': 3,
    'version': 'v2'
})

if r2.status_code == 200:
    data2 = r2.json()
    for i, item in enumerate(data2['items'], 1):
        print(f"\n{i}. ID {item['id']} - Score: {item.get('similarity_score', 'N/A')}")
        print(f"   Razão: {item['razao_social']}")
        print(f"   Objeto: {item['objeto'][:150]}...")
else:
    print(f"❌ Erro: {r2.status_code} - {r2.text}")

print()
print()

# Teste V3 (objeto + plano_de_trabalho)
print("🔍 BUSCA V3 (campo 'objeto' + 'plano_de_trabalho'):")
print("-" * 80)
r3 = requests.get('http://127.0.0.1:8001/api/v1/parcerias/semantic-busca', params={
    'termo': TERMO,
    'limit': 3,
    'version': 'v3'
})

if r3.status_code == 200:
    data3 = r3.json()
    for i, item in enumerate(data3['items'], 1):
        print(f"\n{i}. ID {item['id']} - Score: {item.get('similarity_score', 'N/A')}")
        print(f"   Razão: {item['razao_social']}")
        print(f"   Objeto: {item['objeto'][:150]}...")
        if item.get('plano_de_trabalho'):
            print(f"   Plano: {item['plano_de_trabalho'][:150]}...")
else:
    print(f"❌ Erro: {r3.status_code} - {r3.text}")

print()
print("=" * 80)
print("📊 ANÁLISE:")
print("   V2: Busca apenas no campo 'objeto' (mais específico)")
print("   V3: Busca em 'objeto' + 'plano_de_trabalho' (contexto enriquecido)")
print("=" * 80)
