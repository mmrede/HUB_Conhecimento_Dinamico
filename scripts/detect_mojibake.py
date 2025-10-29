import psycopg2
import re

# Configurações de conexão
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    user="postgres",
    password="rx1800",
    dbname="hub_aura_db"
)

# Heurística simples: busca por padrões típicos de mojibake (ex: 'Ã', '�', 'Ã§', 'Ã³', 'Ã£', 'Ãº', 'Ã©', 'Ãª', 'Ã­', 'Ã³', 'Ã´', 'Ã§', 'Ã¼', 'Ã¶', 'Ã¤', 'Ã€', 'Ã‰', 'Ã¨', 'Ãª', 'Ã«', 'Ã¯', 'Ã´', 'Ã¶', 'Ã¹', 'Ã¼', 'Ã¿', 'Ã')
MOJIBAKE_PATTERNS = re.compile(r'[Ã�]{1,2}[a-zA-Z]|Ã|�')

with conn.cursor() as cur:
    cur.execute("SELECT id, razao_social, objeto FROM instrumentos_parceria")
    rows = cur.fetchall()

print("Registros suspeitos de mojibake:")
count = 0
for row in rows:
    id, razao_social, objeto = row
    for campo in [razao_social, objeto]:
        if campo and MOJIBAKE_PATTERNS.search(campo):
            print(f"ID: {id} | Campo: {campo}")
            count += 1
            break
print(f"Total de registros suspeitos: {count}")
