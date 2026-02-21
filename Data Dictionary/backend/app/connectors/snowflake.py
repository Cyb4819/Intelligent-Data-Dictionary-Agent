import snowflake.connector
from app.connectors.base import BaseConnector
from app.core.errors import ConnectorError
from app.config import settings

class SnowflakeConnector(BaseConnector):
    def __init__(self, account=None, user=None, password=None, warehouse=None, database=None, schema=None):
        self.account = account
        self.user = user
        self.password = password
        self.warehouse = warehouse
        self.database = database
        self.schema = schema
        self.conn = None

    async def connect(self):
        # snowflake.connector is synchronous; this is a thin wrapper
        try:
            self.conn = snowflake.connector.connect(
                user=self.user or settings.POSTGRES_USER,
                password=self.password or settings.POSTGRES_PASSWORD,
                account=self.account,
                warehouse=self.warehouse,
                database=self.database,
                schema=self.schema,
            )
        except Exception as e:
            raise ConnectorError(str(e))

    async def get_tables(self):
        cs = self.conn.cursor()
        try:
            cs.execute("SHOW TABLES")
            return [dict(row) for row in cs.fetchall()]
        finally:
            cs.close()

    async def get_table_schema(self, table_name: str):
        cs = self.conn.cursor()
        try:
            cs.execute(f"DESCRIBE TABLE {table_name}")
            cols = cs.fetchall()
            return {"columns": cols}
        finally:
            cs.close()
