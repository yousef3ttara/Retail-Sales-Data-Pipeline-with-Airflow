# airflow/tasks/load_gold.py
import pandas as pd
import io, sys, os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
sys.path.insert(0, os.path.dirname(__file__))
from utils import read_parquet

load_dotenv()

SQL_CONN = (
    f"mssql+pyodbc://{os.getenv('SQL_USER')}:{os.getenv('SQL_PASSWORD')}"
    f"@{os.getenv('SQL_SERVER')}/{os.getenv('SQL_DATABASE')}"
    f"?driver=ODBC+Driver+17+for+SQL+Server"
)

# Silver blob name -> Gold SQL table name
TABLES = {
    'silver/daily_sales.parquet':    'fact_daily_sales',
    'silver/car_models.parquet':     'dim_car_models',
    'silver/dealers.parquet':        'dim_dealers',
    'silver/sentiment.parquet':      'dim_sentiment',
    'silver/recalls.parquet':        'fact_recalls',
}

def load_gold():
    print('=' * 55)
    print('TASK: load_gold  ->  Silver Parquet to SQL Server')
    print('=' * 55)

    engine = create_engine(SQL_CONN)

    for blob_name, sql_table in TABLES.items():
        print(f'\nLoading {blob_name} -> gold.{sql_table}...')
        df = read_parquet(blob_name)

        df.columns = (
        df.columns.str.strip().str.replace(' ', '_')
        )

        df.to_sql(
            name      = sql_table,
            con       = engine,
            schema    = 'gold',
            if_exists = 'append',
            index     = False,
            chunksize = 5000,
        )
        print(f'  Loaded {len(df):,} rows into gold.{sql_table}')

    # Run the views SQL after tables are loaded
    print('\nCreating analytical views...')
    views_sql = open('sql/create_views.sql').read()
    with engine.connect() as conn:
        for statement in views_sql.split('GO'):
            stmt = statement.strip()
            if stmt:
                conn.execute(text(stmt))
        conn.commit()

    print('\n[DONE] Gold layer loaded successfully.')


if __name__ == '__main__':
    load_gold()
