# airflow/tasks/load_gold.py
import pandas as pd
import io, sys, os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
sys.path.insert(0, os.path.dirname(__file__))
from utils import read_parquet, write_run_log

import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s %(message)s',
)
log = logging.getLogger(__name__)

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

# تصحيح أسماء الأعمدة المختلفة بين ملفات الـ Parquet وجداول SQL Server
COLUMN_RENAME_MAP = {
    'Days_to_Make_Sale': 'Days_to_Sale',
    'Rain_Y_N':           'Is_Rain',
    'Snow_Y_N':           'Is_Snow',
}

def load_gold():
    start = datetime.now()
    log.info('START load_gold')

    engine = create_engine(SQL_CONN)
    row_counts = {}
    total_rows = 0

    for blob_name, sql_table in TABLES.items():
        log.info(f'Loading {blob_name} -> gold.{sql_table}...')
        df = read_parquet(blob_name)

        df.columns = (
        df.columns.str.strip().str.replace(' ', '_')
        )

        # إعادة تسمية الأعمدة المختلفة (يتجاهل أي عمود مش موجود أصلاً)
        df = df.rename(columns=COLUMN_RENAME_MAP)

        df.to_sql(
            name      = sql_table,
            con       = engine,
            schema    = 'gold',
            if_exists = 'append',
            index     = False,
            chunksize = 5000,
        )
        log.info(f'  Loaded {len(df):,} rows into gold.{sql_table}')
        row_counts[sql_table] = len(df)
        total_rows += len(df)

    # Run the views SQL after tables are loaded
    log.info('Creating analytical views...')
    views_sql = open('sql/create_views.sql').read()
    with engine.connect() as conn:
        for statement in views_sql.split('GO'):
            stmt = statement.strip()
            if stmt:
                conn.execute(text(stmt))
        conn.commit()

    elapsed = (datetime.now() - start).seconds
    log.info(f'END load_gold total_rows={total_rows:,} elapsed={elapsed}s')

    write_run_log({
        'task':   'load_gold',
        **row_counts,
        'status': 'SUCCESS',
    })


if __name__ == '__main__':
    load_gold()