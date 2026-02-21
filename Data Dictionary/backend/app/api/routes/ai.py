import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
from app.ai.groq_client import GroqClient
from app.ai.langchain_pipeline import LangChainPipeline
from app.config import settings

router = APIRouter()

class SummarizeRequest(BaseModel):
    schema: Dict[str, Any]

class QueryRequest(BaseModel):
    data: Dict[str, Any]

class JsonMetadataRequest(BaseModel):
    json_data: Dict[str, Any]
    table_name: str = "data"

# Prompt template for generating metadata from JSON
METADATA_PROMPT = """You are a data dictionary generator. Analyze the following JSON data and generate a metadata description in this exact JSON format:

{
  "tableType": "TABLE",
  "tableName": "<table_name>",
  "description": "<brief description of what this data represents>",
  "primaryKeys": ["<if there's an obvious primary key field>"],
  "foreignKeys": [],
  "columns": [
    {
      "columnName": "<field_name>",
      "dataType": "<inferred data type like VARCHAR, INTEGER, DATE, JSON, etc.>",
      "description": "<what this field represents>",
      "nullable": <true/false>,
      "isUnique": <true/false if field appears to have unique values>,
      "sampleValues": ["<2-3 example values from the data>"]
    }
  ]
}

Generate this metadata for the following JSON data:
"""

@router.post("/summarize")
async def summarize(req: SummarizeRequest):
    # create pipeline; pass explicit None for compatibility with older signatures
    pipeline = LangChainPipeline(groq_client=None)
    try:
        summary = await pipeline.summarize_table(req.schema)
        return {"status": "ok", "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query")
async def query(req: QueryRequest):
    """Accept arbitrary JSON data and return a Groq-generated response."""
    pipeline = LangChainPipeline(groq_client=None)
    try:
        # Reuse pipeline but convert data to string
        summary = await pipeline.summarize_table(req.data)
        return {"status": "ok", "output": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/json-metadata")
async def generate_json_metadata(req: JsonMetadataRequest):
    """Generate metadata descriptions for JSON data."""
    groq_client = GroqClient()
    
    try:
        # Format the prompt with the JSON data
        json_str = json.dumps(req.json_data, indent=2)
        prompt = f"{METADATA_PROMPT}\n\nTable Name: {req.table_name}\n\nData:\n{json_str}"
        
        # Call Groq to generate metadata
        result = await groq_client.generate_summary(prompt)
        
        return {"status": "ok", "metadata": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
