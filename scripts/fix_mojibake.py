import psycopg2
import csv
import os

# Configurações de conexão
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    user="postgres",
    password="rx1800",
    dbname="hub_aura_db"
)

# Caminho do CSV original (ajuste se necessário)
CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'Instrumento_Parceria_XLSX_csv.csv')

# Lê o CSV em UTF-8 (convertido previamente, se necessário)
def load_csv_utf8():
    with open(CSV_PATH, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = [row for row in reader]
    return data

# Atualiza registros no banco com dados do CSV
with conn.cursor() as cur:
    csv_data = load_csv_utf8()
    count = 0
    for row in csv_data:
        razao_social = row.get('razao_social')
        objeto = row.get('objeto')
        cnpj = row.get('cnpj')
        # Atualiza pelo CNPJ (ajuste se necessário para chave única)
        cur.execute("""
            UPDATE instrumentos_parceria
            SET razao_social = %s, objeto = %s
            WHERE cnpj = %s
        """, (razao_social, objeto, cnpj))
        if cur.rowcount:
            print(f"Atualizado: CNPJ {cnpj} | Razao: {razao_social} | Objeto: {objeto}")
            count += 1
    conn.commit()
print(f"Total de registros atualizados: {count}")
