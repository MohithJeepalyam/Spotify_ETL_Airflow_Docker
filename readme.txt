This is a Spotify ETL pipeline with Airflow, Postgres and Docker.

Requirements:


How to download Airflow with docker:
1. go to Airflow docs and go to Quick start.
2. There you can find "Running Airflow with docker".
3. Go there and follow the instructions to install airflow.
4. curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.3.3/docker-compose.yaml'
5. Run the above command to get the docker-compose.yaml file.
6. In the file convert the celeryExecutor to the local LocalExecutor for simplicity.
7. Delete the redis, worker and flower related content.
