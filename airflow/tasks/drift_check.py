# airflow/tasks/drift_check.py
import json, io
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils import read_parquet, get_client, CONTAINER

import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s %(message)s',
)
log = logging.getLogger(__name__)

# Expected ranges based on historical Bronze data
EXPECTED = {
    'daily_sales_min_rows':  40000,  # alert if fewer than this arrive
    'daily_sales_max_rows':  70000,  # alert if more than this arrive
    'null_car_id_max_pct':   0.03,   # alert if null Car ID > 3%
    'dup_sales_id_max_pct':  0.02,   # alert if duplicate Sales ID > 2%
}


def drift_check():
    start = datetime.now()
    log.info('START drift_check')

    ds = read_parquet('bronze/daily_sales.parquet')
    n_rows = len(ds)
    alerts = []

    # ── Row count drift ───────────────────────────────────────────
    if n_rows < EXPECTED['daily_sales_min_rows']:
        alerts.append(f'ROW COUNT LOW: {n_rows:,} rows (expected >= {EXPECTED["daily_sales_min_rows"]:,})')

    if n_rows > EXPECTED['daily_sales_max_rows']:
        alerts.append(f'ROW COUNT HIGH: {n_rows:,} rows (expected <= {EXPECTED["daily_sales_max_rows"]:,})')

    # ── Null rate drift ───────────────────────────────────────────
    null_pct = ds['Car ID'].isna().sum() / n_rows
    if null_pct > EXPECTED['null_car_id_max_pct']:
        alerts.append(f'NULL RATE HIGH: Car ID null={null_pct:.1%} (expected <= {EXPECTED["null_car_id_max_pct"]:.1%})')

    # ── Duplicate rate drift ──────────────────────────────────────
    dup_pct = ds.duplicated(subset=['Sales ID']).sum() / n_rows
    if dup_pct > EXPECTED['dup_sales_id_max_pct']:
        alerts.append(f'DUPLICATE RATE HIGH: {dup_pct:.1%} (expected <= {EXPECTED["dup_sales_id_max_pct"]:.1%})')

    # ── Log results ─────────────────────────────────────────────
    log.info(f'  Rows: {n_rows:,}')
    log.info(f'  Null Car ID: {null_pct:.2%}')
    log.info(f'  Dup Sales ID: {dup_pct:.2%}')

    elapsed = (datetime.now() - start).seconds

    if alerts:
        log.error('DATA DRIFT DETECTED:\n' + '\n'.join(alerts))
        raise ValueError('DATA DRIFT DETECTED:\n' + '\n'.join(alerts))

    log.info(f'END drift_check total_rows={n_rows:,} elapsed={elapsed}s')
    log.info('No drift detected.')


if __name__ == '__main__':
    drift_check()