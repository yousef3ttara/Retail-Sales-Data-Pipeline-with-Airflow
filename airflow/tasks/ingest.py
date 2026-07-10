import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils import write_parquet

import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s %(message)s',
)
log = logging.getLogger(__name__)

SOURCES = {
    'bronze/daily_sales.parquet':      'data/raw/AU_Daily_Sales.csv',
    'bronze/sales_by_model.parquet':   'data/raw/AU_Sales_By_Model.csv',
    'bronze/car_models.parquet':       'data/raw/AU_Car_Models.csv',
    'bronze/dealers.parquet':          'data/raw/AU_Dealers.csv',
    'bronze/recalls.parquet':          'data/raw/AU_Car_Recalls.csv',
    'bronze/sentiment.parquet':        'data/raw/AU_Sentiment.csv',
}

def ingest_bronze():
    start = datetime.now()
    log.info('START ingest_bronze')

    total_rows = 0
    for blob_name, csv_path in SOURCES.items():
        df = pd.read_csv(csv_path)
        write_parquet(df, blob_name)
        log.info(f'  Uploaded {blob_name} rows={len(df):,}')
        total_rows += len(df)

    elapsed = (datetime.now() - start).seconds
    log.info(f'END ingest_bronze total_rows={total_rows:,} elapsed={elapsed}s')

if __name__ == '__main__':
    ingest_bronze()