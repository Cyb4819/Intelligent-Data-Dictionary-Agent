from fastapi import APIRouter, HTTPException
from app.extractors.quality_analyzer import QualityAnalyzer
from app.config import settings
from app.models.schemas import QualityResponse, TableQueryRequest
from app.api.middleware import limiter
from app.core.logging import logger

router = APIRouter()

@router.get("/table/{table_name}", response_model=QualityResponse)
@limiter.limit(f"{settings.RATE_LIMIT_UNAUTHENTICATED}/minute")
async def analyze_table(request, table_name: str, sample: int = 500):
    try:
        # Validate inputs
        if not table_name or len(table_name) > 255:
            raise HTTPException(status_code=400, detail="Invalid table name")
        if sample < 1 or sample > 10000:
            sample = 500
        
        logger.info(f"Quality analysis started for table: {table_name}")
        dsn = settings.DATABASE_URL
        from app.connectors.postgresql import PostgresConnector
        connector = PostgresConnector(dsn=dsn)
        await connector.connect()
        analyzer = QualityAnalyzer(connector)
        
        # fetch rows for sampling
        rows = await connector.fetch_rows(table_name, limit=sample)
        import pandas as pd
        df = pd.DataFrame(rows)
        completeness = analyzer.compute_completeness(df)
        
        result = {
            "status": "ok",
            "table": table_name,
            "metrics": {
                "completeness": completeness,
                "rows_sampled": len(df),
                "columns_analyzed": len(df.columns)
            }
        }
        logger.info(f"Quality analysis completed for {table_name}")
        return result
    except Exception as e:
        logger.error(f"Quality analysis error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze", response_model=QualityResponse)
@limiter.limit(f"{settings.RATE_LIMIT_UNAUTHENTICATED}/minute")
async def analyze_table_advanced(request, query: TableQueryRequest):
    try:
        logger.info(f"Advanced quality analysis for {query.table_name}")
        dsn = settings.DATABASE_URL
        from app.connectors.postgresql import PostgresConnector
        connector = PostgresConnector(dsn=dsn)
        await connector.connect()
        analyzer = QualityAnalyzer(connector)
        
        rows = await connector.fetch_rows(query.table_name, limit=query.limit)
        import pandas as pd
        df = pd.DataFrame(rows)
        completeness = analyzer.compute_completeness(df)
        
        return {
            "status": "ok",
            "table": query.table_name,
            "metrics": {
                "completeness": completeness,
                "rows_sampled": len(df),
                "columns_analyzed": len(df.columns)
            }
        }
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
