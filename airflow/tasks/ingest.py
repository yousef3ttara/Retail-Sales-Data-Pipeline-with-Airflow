import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils import write_parquet

SOURCES = {
    'bronze/daily_sales.parquet':      'data/raw/AU_Daily_Sales.csv',
    'bronze/sales_by_model.parquet':   'data/raw/AU_Sales_By_Model.csv',
    'bronze/car_models.parquet':       'data/raw/AU_Car_Models.csv',
    'bronze/dealers.parquet':          'data/raw/AU_Dealers.csv',
    'bronze/recalls.parquet':          'data/raw/AU_Car_Recalls.csv',
    'bronze/sentiment.parquet':        'data/raw/AU_Sentiment.csv',
}

def ingest_bronze():
    print('=' * 55)
    print('TASK: ingest_bronze -> CSV to Azure Blob (Bronze)')
    print('=' * 55)
    
    for blob_name, csv_path in SOURCES.items():
        df = pd.read_csv(csv_path)
        write_parquet(df, blob_name)
    print('\n[DONE] Bronze ingestion complete.')

if __name__ == '__main__':
    ingest_bronze()