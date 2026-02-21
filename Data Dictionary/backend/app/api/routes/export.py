from fastapi import APIRouter, HTTPException
from app.connectors.postgresql import PostgresConnector
from app.storage.artifact_manager import save_markdown_for_table
from app.config import settings

router = APIRouter()

@router.get("/markdown/{table_name}")
async def export_markdown(table_name: str):
    dsn = settings.DATABASE_URL
    connector = PostgresConnector(dsn=dsn)
    try:
        await connector.connect()
        schema = await connector.get_table_schema(table_name)
        md_path = save_markdown_for_table(table_name, schema)
        return {"status": "ok", "path": md_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
