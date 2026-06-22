# airflow/tasks/validate.py
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils import read_parquet

def validate_bronze():
    print('=' * 55)
    print('TASK: validate_bronze  ->  Quality checks on Bronze')
    print('=' * 55)

    errors   = []
    warnings = []

    ds  = read_parquet('bronze/daily_sales.parquet')
    sbm = read_parquet('bronze/sales_by_model.parquet')
    rec = read_parquet('bronze/recalls.parquet')
    mod = read_parquet('bronze/car_models.parquet')

    # ── Row count checks (CRITICAL) ──────────────────────────────────
    for name, df in [('daily_sales', ds), ('sales_by_model', sbm),
                     ('recalls', rec), ('car_models', mod)]:
        if len(df) == 0:
            errors.append(f'EMPTY TABLE: {name}')

    # ── Duplicate checks (CRITICAL) ──────────────────────────────────
    dup_sales = ds.duplicated(subset=['Sales ID']).sum()
    if dup_sales > 0:
        errors.append(f'daily_sales: {dup_sales} duplicate Sales IDs')

    # ── Null FK checks (CRITICAL) ─────────────────────────────────────
    null_car = ds['Car ID'].isna().sum()
    if null_car > 0:
        errors.append(f'daily_sales: {null_car} null Car IDs (FK missing)')

    # ── Orphan FK check (CRITICAL) ────────────────────────────────────
    valid_ids = set(mod['Car_ID'].tolist())
    orphans   = (~rec['Car_ID'].isin(valid_ids)).sum()
    if orphans > 0:
        errors.append(f'recalls: {orphans} Car_IDs not in car_models')

    # ── Warning checks ────────────────────────────────────────────────
    null_profit = sbm['Profit'].isna().sum()
    if null_profit > 0:
        warnings.append(f'sales_by_model: {null_profit} null Profit rows')

    neg_qty = (sbm['Quantity Sold'] < 0).sum()
    if neg_qty > 0:
        warnings.append(f'sales_by_model: {neg_qty} negative Quantity Sold')

    null_weather = ds['Weather Condition'].isna().sum()
    if null_weather > 0:
        warnings.append(f'daily_sales: {null_weather} null Weather rows')

    # ── Print results ─────────────────────────────────────────────────
    print(f'\nRow counts:')
    print(f'  daily_sales:    {len(ds):>8,}')
    print(f'  sales_by_model: {len(sbm):>8,}')
    print(f'  recalls:        {len(rec):>8,}')
    print(f'  car_models:     {len(mod):>8,}')

    for w in warnings:
        print(f'[WARN]  {w}')

    if errors:
        raise ValueError('\n'.join(['[CRITICAL] Validation failed:'] + errors))

    print('\n[DONE] All critical checks passed.')


if __name__ == '__main__':
    validate_bronze()
