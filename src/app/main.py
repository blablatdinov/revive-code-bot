import time
from contextlib import asynccontextmanager

import psycopg2
from litestar import Litestar, get
from litestar.datastructures import State
from litestar.di import Provide
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    pgsql_dsn: PostgresDsn

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


settings = Settings()


@asynccontextmanager
async def db_connection(app: Litestar):
    engine = getattr(app, 'db_conn', None)
    if not engine:
        with psycopg2.connect(str(settings.pgsql_dsn)) as conn:
            app.state.db_conn = conn
    yield


@get("/healthcheck")
def healthcheck(state: State) -> dict:
    start = time.time()
    with state.db_conn.cursor() as curr:
        curr.execute('SELECT 1')
        db_query_time = time.time() - start
    return {
        'app': 'ok',
        'db': round(db_query_time, 3)
    }


app = Litestar([healthcheck], lifespan=[db_connection])
