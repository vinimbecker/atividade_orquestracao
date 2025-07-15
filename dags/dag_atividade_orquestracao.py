from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'depends_on_past': False,
    'retries': 1,
}

with DAG(
    dag_id='pipeline_dados_airbnb',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    description='Pipeline de ingestão, transformação e geração de tabela final com Spark',
    tags=['pyspark', 'airbnb'],
) as dag:
    scripts_path = "/opt/airflow/scripts"
    
    ingestao = SparkSubmitOperator(
        task_id='ingestao_dados',
        application=f'{scripts_path}/01_ingestao_dados.py',
        conn_id='spark_default',
        dag=dag,
    )

    transformacao = SparkSubmitOperator(
        task_id='transformacao_dados',
        application=f'{scripts_path}/02_transformacao_dados.py',
        conn_id='spark_default',
        dag=dag,
    )

    geracao_tabela = SparkSubmitOperator(
        task_id='geracao_tabela_final',
        application=f'{scripts_path}/03_geracao_tabela.py',
        conn_id='spark_default',
        dag=dag,
    )

    ingestao >> transformacao >> geracao_tabela
