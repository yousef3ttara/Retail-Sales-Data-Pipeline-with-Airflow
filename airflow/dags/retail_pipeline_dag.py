"""
airflow/dags/retail_pipeline_dag.py
"""

import os
import sys
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
# from airflow.operators.email import EmailOperator

# Add tasks folder to Python path
TASKS_DIR = os.path.join(os.path.dirname(__file__), "..", "tasks")
sys.path.insert(0, os.path.abspath(TASKS_DIR))

from ingest import ingest_bronze
from validate import validate_bronze
from transform import transform_silver
from load_gold import load_gold
from drift_check import drift_check


def on_failure(context):
    ti = context["task_instance"]
    print(
        f"[ALERT] Task FAILED: {ti.task_id} | "
        f"DAG={context['dag'].dag_id} | "
        f"Execution={context['execution_date']}"
    )


default_args = {
    "owner": "data-team",
    "retries": 1,
    "retry_delay": 300,
    "email_on_failure": False,
    "email_on_retry": False,
    "email": ["your-team-email@example.com"],
    "on_failure_callback": on_failure,
}


with DAG(
    dag_id="retail_pipeline",
    description="Retail Data Pipeline",
    schedule="@monthly",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args=default_args,
    tags=["retail", "etl", "milestone3"],
) as dag:

    t1 = PythonOperator(
        task_id="ingest_bronze",
        python_callable=ingest_bronze,
    )

    t2 = PythonOperator(
        task_id="validate_bronze",
        python_callable=validate_bronze,
    )

    t2b = PythonOperator(
        task_id="drift_check",
        python_callable=drift_check,
    )

    t3 = PythonOperator(
        task_id="transform_silver",
        python_callable=transform_silver,
    )

    t4 = PythonOperator(
        task_id="load_gold",
        python_callable=load_gold,
    )

    # ترتيب تنفيذ التاسكات (drift_check اتحط بعد validate وقبل transform)
    t1 >> t2 >> t2b >> t3 >> t4