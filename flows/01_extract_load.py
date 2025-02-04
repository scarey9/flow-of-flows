
import pandas as pd
import prefect
from prefect import task, Flow
from prefect.executors import LocalDaskExecutor
from prefect.run_configs import LocalRun
from prefect.storage import GitHub
from prefect.client import Secret
from prefect.tasks.secrets import PrefectSecret
from sqlalchemy import create_engine


def get_db_connection_string() -> str:
    user = Secret("POSTGRES_USER").get()
    pwd = Secret("POSTGRES_PASS").get()
    return f"postgresql://{user}:{pwd}@localhost:5432/postgres"


def get_df_from_sql_query(table_or_query: str) -> pd.DataFrame:
    db = get_db_connection_string()
    engine = create_engine(db)
    return pd.read_sql(table_or_query, engine) 


def load_df_to_db(df: pd.DataFrame, table_name: str, schema: str = "jaffle_shop") -> None:
    conn_string = get_db_connection_string()
    db_engine = create_engine(conn_string)
    conn = db_engine.connect()
    conn.execute("CREATE SCHEMA IF NOT EXISTS jaffle_shop;")
    conn.execute(f"DROP TABLE IF EXISTS {schema}.{table_name} CASCADE;")
    df.to_sql(table_name, schema=schema, con=db_engine, index=False)
    conn.close()


FLOW_NAME = "01_extract_load"




STORAGE = GitHub(
    repo="scarey9/flow-of-flows",
    path=f"flows/{FLOW_NAME}.py",
    access_token_secret="GITHUB_TOKEN",
)


@task
def extract_and_load(dataset: str) -> None:
    logger = prefect.context.get("logger")
    file = f"https://raw.githubusercontent.com/anna-geller/jaffle_shop/main/data/{dataset}.csv"
    df = pd.read_csv(file)
    load_df_to_db(df, dataset)
    logger.info("Dataset %s with %d rows loaded to DB", dataset, len(df))


with Flow(
    FLOW_NAME,
    executor=LocalDaskExecutor(),
    storage=STORAGE,
    run_config=LocalRun(labels=["dev"]),
) as flow:
    datasets = [ "raw_customers", "raw_orders", "raw_payments"]
    dataframes = extract_and_load.map(datasets)  
