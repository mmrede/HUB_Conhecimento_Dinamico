#!/usr/bin/env python3
"""
Importador simples do CSV `Instrumento_Parceria_XLSX_csv.csv` para a tabela `instrumentos_parceria`.

Regras:
- Lê o CSV com encoding cp1252 (Windows-1252) e delimiter ';'.
- Normaliza datas com dateutil.parser (quando possível).
- Insere apenas linhas que não existam já na tabela (checagem por `razao_social` + `objeto`).

Uso:
  .\venv\Scripts\python.exe scripts\import_csv.py

"""
import csv
import os
import sys
from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor
from dateutil import parser as dateparser

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
CSV_PATH = os.path.join(PROJECT_ROOT, 'Instrumento_Parceria_XLSX_csv.csv')
DB_URL = os.environ.get('DATABASE_URL') or 'postgresql://postgres:rx1800@localhost:5433/hub_aura_db'


def parse_date(s):
    if not s or s.strip() == '':
        return None
    try:
        # Alguns valores têm formato 'dd/mm/yyyy hh:MM:SS' ou somente 'dd/mm/yyyy'
        dt = dateparser.parse(s, dayfirst=True)
        return dt.date()
    except Exception:
        return None


def main():
    print('Abrindo CSV:', CSV_PATH)
    if not os.path.exists(CSV_PATH):
        print('Arquivo não encontrado:', CSV_PATH)
        sys.exit(1)

    conn = psycopg2.connect(DB_URL)
    conn.autocommit = True
    cur = conn.cursor(cursor_factory=RealDictCursor)

    inserted = 0
    skipped = 0

    with open(CSV_PATH, 'r', encoding='cp1252', errors='replace') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            numero = row.get('N�MERO DO TERMO') or row.get('NUMERO DO TERMO') or row.get('NÚMERO DO TERMO') or ''
            ano = row.get('ANO DO TERMO') or row.get('ANO_DO_TERMO') or ''
            cpf = row.get('CPF/CNPJ') or row.get('CPF_CNPJ') or ''
            razao = (row.get('RAZ�O SOCIAL') or row.get('RAZAO SOCIAL') or row.get('RAZÃO SOCIAL') or '').strip()
            objeto = (row.get('OBJETO') or '').strip()
            data_ass = parse_date(row.get('DATA DA ASSINATURA') or row.get('DATA_DA_ASSINATURA') or '')
            data_pub = parse_date(row.get('DATA DE PUBLICA��O') or row.get('DATA DE PUBLICAÇÃO') or row.get('DATA_DE_PUBLICACAO') or '')
            vigencia = (row.get('VIG�NCIA') or row.get('VIGENCIA') or '')
            situacao = (row.get('SITUA��O') or row.get('SITUACAO') or row.get('SITUAÇÃO') or '')

            # Skip empty meaningful rows
            if not razao and not objeto:
                skipped += 1
                continue

            # Check existence by razao + objeto
            cur.execute(
                "SELECT id FROM instrumentos_parceria WHERE razao_social = %s AND objeto = %s LIMIT 1",
                (razao, objeto),
            )
            if cur.fetchone():
                skipped += 1
                continue

            cur.execute(
                "INSERT INTO instrumentos_parceria (numero_do_termo, ano_do_termo, cpf_cnpj, razao_social, objeto, data_da_assinatura, data_de_publicacao, vigencia, situacao) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                (numero or None, ano or None, cpf or None, razao or None, objeto or None, data_ass, data_pub, vigencia or None, situacao or None),
            )
            _id = cur.fetchone()['id']
            inserted += 1

    cur.close()
    conn.close()
    print(f'Inseridas: {inserted}, Puladas: {skipped}')


if __name__ == '__main__':
    main()
