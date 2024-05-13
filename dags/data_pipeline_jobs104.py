# dags/data_pipeline_jobs104.py
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

# test operator !!!
from app import say_hello
# build opperators !!!




with DAG(
    dag_id = 'data_pipeline_jobs104',
    start_date = datetime(2024, 5, 1),
    schedule_interval=None
) as dag:
    task1 = PythonOperator(
    task_id='say_hello',
    python_callable=say_hello
    )

    task1