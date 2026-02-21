"""Postgres connector with graceful fallback when `asyncpg` is not installed.

Importing heavy DB drivers at module import time can crash the whole app
if the package isn't available in the environment. We try to import
`asyncpg` and expose a connector class that raises a descriptive
`ConnectorError` if used when the driver is missing.
"""

try:
    import asyncpg  # type: ignore
except Exception:  # pragma: no cover - environment dependent
    asyncpg = None

from app.connectors.base import BaseConnector
from app.core.errors import ConnectorError
from app.config import settings


class PostgresConnector(BaseConnector):
    def __init__(self, dsn: str = None):
        self.dsn = dsn or settings.DATABASE_URL
        self.pool = None
        self._available = asyncpg is not None

    async def connect(self):
        if not self._available:
            raise ConnectorError("asyncpg is not installed in the environment. Install asyncpg to use PostgresConnector")
        try:
            self.pool = await asyncpg.create_pool(dsn=self.dsn)
        except Exception as e:
            raise ConnectorError(str(e))

    async def get_tables(self):
        if not self._available or not self.pool:
            raise ConnectorError("PostgresConnector not connected")
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT table_schema, table_name
                FROM information_schema.tables
                WHERE table_type='BASE TABLE' AND table_schema NOT IN ('pg_catalog','information_schema');
            """)
            return [dict(r) for r in rows]

    async def get_table_schema(self, table_name: str):
        if not self._available or not self.pool:
            raise ConnectorError("PostgresConnector not connected")
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = $1
            """, table_name)
            return {"columns": [dict(r) for r in rows]}

    async def fetch_rows(self, table_name: str, limit: int = 1000):
        if not self._available or not self.pool:
            raise ConnectorError("PostgresConnector not connected")
        async with self.pool.acquire() as conn:
            # Simple select; warning: not safe for very large tables without filters
            q = f"SELECT * FROM {table_name} LIMIT $1"
            rows = await conn.fetch(q, limit)
            # convert to list of dicts
            return [dict(r) for r in rows]
