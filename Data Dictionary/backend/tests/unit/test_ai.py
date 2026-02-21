import pytest
from app.ai.groq_client import GroqClient
from app.ai.langchain_pipeline import LangChainPipeline


class DummyClient(GroqClient):
    async def generate_summary(self, text: str) -> str:
        return "dummy_response for: " + text


@pytest.mark.asyncio
async def test_pipeline_summarize():
    # pipeline should accept an injected client or default to one
    client = DummyClient(api_key="test")
    pipeline = LangChainPipeline(groq_client=client)
    schema = {"table": "users", "columns": ["id", "name"]}
    result = await pipeline.summarize_table(schema)
    # dummy client echoes the text it received; ensure sample file text is included
    assert result.startswith("dummy_response for:")
    assert "SAMPLE_EMPLOYEES" in result or "employees" in result.lower()
