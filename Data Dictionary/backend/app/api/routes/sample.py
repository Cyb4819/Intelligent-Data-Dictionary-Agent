from fastapi import APIRouter, HTTPException, Request
import json
import os

router = APIRouter()

@router.post("/extract")
async def extract_metadata(request: Request):
    try:
        sources = await request.json()
        
        # Get the path to sample.json
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sample_json_path = os.path.join(current_dir, "..", "data", "sample.json")
        
        # Read and return the sample.json content
        with open(sample_json_path, "r") as f:
            data = json.load(f)
        
        return data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="sample.json not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
