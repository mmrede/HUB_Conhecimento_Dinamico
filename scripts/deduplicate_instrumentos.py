import psycopg2
from collections import defaultdict

# Configurações de conexão
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    user="postgres",
    password="rx1800",
    dbname="hub_aura_db"
)

# Critério de deduplicação: razao_social + objeto
with conn.cursor() as cur:
    cur.execute("SELECT id, razao_social, objeto, cnpj FROM instrumentos_parceria")
    rows = cur.fetchall()

# Agrupa por chave canônica
dupes = defaultdict(list)
for row in rows:
    id, razao_social, objeto, cnpj = row
    key = (razao_social.strip().lower(), objeto.strip().lower())
    dupes[key].append((id, cnpj))

dedup_count = 0
print("Duplicatas encontradas (razão_social + objeto):")
for key, items in dupes.items():
    if len(items) > 1:
        print(f"Chave: {key}")
        for id, cnpj in items:
            print(f"  ID: {id} | CNPJ: {cnpj}")
        dedup_count += len(items) - 1
print(f"Total de registros duplicados: {dedup_count}")

# Para aplicar a deduplicação (remover duplicatas mantendo o menor ID):
APPLY = True  # Altere para True para aplicar
if APPLY:
    with conn.cursor() as cur:
        for key, items in dupes.items():
            if len(items) > 1:
                # Mantém o menor ID, remove os outros
                items_sorted = sorted(items)
                keep_id = items_sorted[0][0]
                remove_ids = [id for id, _ in items_sorted[1:]]
                for rid in remove_ids:
                    cur.execute("DELETE FROM instrumentos_parceria WHERE id = %s", (rid,))
        conn.commit()
    print("Deduplicação aplicada.")
else:
    print("Deduplicação NÃO aplicada (modo dry-run). Para aplicar, altere APPLY=True no script.")
