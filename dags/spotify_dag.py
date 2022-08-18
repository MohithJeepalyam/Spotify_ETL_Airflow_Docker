from airflow import DAG
from datetime import datetime
from datetime import timedelta
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago


default_args = {
    "owner" : "airflow",
    "retries" : 1,
    "retry_delay" : timedelta(minutes= 5)
}

def test_call():
    print("Test check!!")


with DAG(
    default_args= default_args,
    dag_id= "spotify_etl_dag",
    description= "Spotify ETL DAG",
    start_date= days_ago(18),
    schedule_interval= "0 3 * * *"
) as dag:
    task1 = PythonOperator(
        task_id = "test",
        python_callable= test_call
    )

    task1