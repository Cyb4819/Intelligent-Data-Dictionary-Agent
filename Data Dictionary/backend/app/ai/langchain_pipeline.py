from __future__ import annotations

import os
from typing import Any

from app.ai.groq_client import GroqClient
from app.config import settings

# avoid importing langchain at all; we handle text composition ourselves



class LangChainPipeline:
    def __init__(self, groq_client: GroqClient | None = None):
        # allow caller to inject a client for testing; otherwise create default
        self.groq = groq_client or GroqClient()

    async def summarize_table(self, table_schema: dict) -> str:
        """Compose a payload of schema and sample data and send to Groq."""

        # gather text (schema plus sample file)
        text = str(table_schema)
        sample_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            "sample.json",
        )
        sample_path = os.path.normpath(sample_path)
        if os.path.exists(sample_path):
            try:
                with open(sample_path, "r", encoding="utf-8") as f:
                    sample_text = f.read()
                text += "\n\nSAMPLE_EMPLOYEES:\n" + sample_text
            except Exception:
                pass

        # call groq client directly
        return await self.groq.generate_summary(text)

