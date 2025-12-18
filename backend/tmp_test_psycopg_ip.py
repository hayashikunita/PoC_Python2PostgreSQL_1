import psycopg
import os
ip = os.environ.get('DBIP')
try:
    with psycopg.connect(f'postgresql://postgres:postgres@{ip}:5432/appdb') as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT 1')
            print('psycopg connection: OK')
except Exception as e:
    print('psycopg connection: FAILED', type(e).__name__, e)
