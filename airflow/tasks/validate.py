# airflow/tasks/validate.py

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from utils import read_parquet

import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s %(message)s',
)
log = logging.getLogger(__name__)


def validate_bronze():
    start = datetime.now()
    log.info('START validate_bronze')

    errors = []
    warnings = []

    ds = read_parquet("bronze/daily_sales.parquet")
    sbm = read_parquet("bronze/sales_by_model.parquet")
    rec = read_parquet("bronze/recalls.parquet")
    mod = read_parquet("bronze/car_models.parquet")

    # -----------------------------
    # Critical Checks
    # -----------------------------
    for name, df in [
        ("daily_sales", ds),
        ("sales_by_model", sbm),
        ("recalls", rec),
        ("car_models", mod),
    ]:
        if len(df) == 0:
            errors.append(f"EMPTY TABLE: {name}")

    # -----------------------------
    # Warning Checks
    # -----------------------------
    dup_sales = ds.duplicated(subset=["Sales ID"]).sum()
    if dup_sales > 0:
        warnings.append(f"daily_sales: {dup_sales} duplicate Sales IDs")

    null_car = ds["Car ID"].isna().sum()
    if null_car > 0:
        warnings.append(f"daily_sales: {null_car} null Car IDs (FK missing)")

    valid_ids = set(mod["Car_ID"].tolist())
    orphans = (~rec["Car_ID"].isin(valid_ids)).sum()
    if orphans > 0:
        warnings.append(f"recalls: {orphans} Car_IDs not in car_models")

    null_profit = sbm["Profit"].isna().sum()
    if null_profit > 0:
        warnings.append(f"sales_by_model: {null_profit} null Profit rows")

    neg_qty = (sbm["Quantity Sold"] < 0).sum()
    if neg_qty > 0:
        warnings.append(f"sales_by_model: {neg_qty} negative Quantity Sold")

    null_weather = ds["Weather Condition"].isna().sum()
    if null_weather > 0:
        warnings.append(f"daily_sales: {null_weather} null Weather rows")

    # -----------------------------
    # Log Summary
    # -----------------------------
    total_rows = len(ds) + len(sbm) + len(rec) + len(mod)
    log.info(f"  daily_sales:    {len(ds):>8,}")
    log.info(f"  sales_by_model: {len(sbm):>8,}")
    log.info(f"  recalls:        {len(rec):>8,}")
    log.info(f"  car_models:     {len(mod):>8,}")

    if warnings:
        for w in warnings:
            log.info(f"[WARN] {w}")

    if errors:
        raise ValueError("\n".join(["[CRITICAL] Validation failed:"] + errors))

    elapsed = (datetime.now() - start).seconds
    log.info(f'END validate_bronze total_rows={total_rows:,} elapsed={elapsed}s')


if __name__ == "__main__":
    validate_bronze()