# airflow/tasks/transform.py
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils import read_parquet, write_parquet

def transform_silver():
    print('=' * 55)
    print('TASK: transform_silver  ->  Bronze to Silver cleaning')
    print('=' * 55)

    # ── 1. daily_sales (Fact — main) ─────────────────────────────────
    print('\nCleaning daily_sales...')
    ds = read_parquet('bronze/daily_sales.parquet')
    before = len(ds)

    ds = ds.drop_duplicates(subset=['Sales ID'], keep='first')
    ds = ds.dropna(subset=['Car ID'])
    ds = ds.dropna(subset=['Temperature (F)', 'Weather Condition'])
    ds['Open Date'] = pd.to_datetime(ds['Open Date'],
                                     format='%d-%b-%Y', errors='coerce')
    ds = ds.dropna(subset=['Open Date'])
    ds['Month']       = ds['Open Date'].dt.strftime('%b')
    ds['Month Order'] = ds['Open Date'].dt.month
    ds['Year']        = ds['Open Date'].dt.year
    ds['Car ID']      = ds['Car ID'].astype('Int64')
    for col in ['Fog (Y/N)', 'Rain (Y/N)', 'Snow (Y/N)']:
        ds[col] = ds[col].map({'Y': True, 'N': False})
    ds.columns = [c.replace(' ','_').replace('(','').replace(')','').replace('/','_')
                  for c in ds.columns]
    print(f'  Rows: {before:,} -> {len(ds):,}  (removed {before-len(ds):,})')
    write_parquet(ds, 'silver/daily_sales.parquet')

    # ── 2. sales_by_model (Fact — monthly summary) ───────────────────
    print('\nCleaning sales_by_model...')
    sbm = read_parquet('bronze/sales_by_model.parquet')
    before = len(sbm)

    sbm = sbm.drop_duplicates(subset=['Year','Month','Model','Dealer ID'])
    sbm = sbm.dropna(subset=['Profit'])
    sbm = sbm[sbm['Quantity Sold'] > 0]
    sbm['Model'] = sbm['Model'].str.title()
    sbm['Date']  = pd.to_datetime(sbm['Date'], errors='coerce')
    print(f'  Rows: {before:,} -> {len(sbm):,}  (removed {before-len(sbm):,})')
    write_parquet(sbm, 'silver/sales_by_model.parquet')

    # ── 3. recalls (Satellite Fact) ───────────────────────────────────
    print('\nCleaning recalls...')
    rec = read_parquet('bronze/recalls.parquet')
    before = len(rec)

    rec = rec.drop_duplicates()
    rec = rec.dropna(subset=['Date'])
    rec = rec[rec['Units'] > 0]
    valid_ids = read_parquet('bronze/car_models.parquet')['Car_ID'].tolist()
    rec = rec[rec['Car_ID'].isin(valid_ids)]
    print(f'  Rows: {before:,} -> {len(rec):,}  (removed {before-len(rec):,})')
    write_parquet(rec, 'silver/recalls.parquet')

    # ── 4. Dimension tables (pass-through — already clean) ────────────
    print('\nPassing through dimension tables (no cleaning needed)...')
    for name in ['car_models', 'dealers', 'sentiment']:
        df = read_parquet(f'bronze/{name}.parquet')
        write_parquet(df, f'silver/{name}.parquet')

    print('\n[DONE] Silver transformation complete.')


if __name__ == '__main__':
    transform_silver()
