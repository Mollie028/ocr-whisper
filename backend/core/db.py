import psycopg2
import os
from psycopg2.extras import RealDictCursor
import urllib.parse as up

def get_conn():
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        raise Exception("❌ DATABASE_URL 未設定")

    up.uses_netloc.append("postgres")
    url = up.urlparse(dsn)

    return psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port,
        cursor_factory=RealDictCursor,
        sslmode="require"
    )
