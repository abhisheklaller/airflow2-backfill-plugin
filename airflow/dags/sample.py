from datetime import datetime
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from time import sleep

dag = DAG('hello_world', description='Hello World DAG',
          schedule_interval='0 12 * * *',
          start_date=datetime(2017, 3, 20), catchup=False)

hello_operator = DummyOperator(task_id='hello_task', dag=dag)
