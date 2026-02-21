import os
import json
import httpx
from app.config import settings
from app.core.logging import logger

class GroqClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.GROQ_API_KEY
        # groq model name from settings
        self.model = getattr(settings, "MODEL_NAME", "groq-small")

    async def generate_summary(self, text: str) -> str:
        """Send the supplied text to Groq API and return the model output.

        Expects the Groq API to accept JSON in the form {"model":...,"input":...}
        and return a JSON with an `output` list containing strings.
        """
        logger.debug("GroqClient.generate_summary called")
        if not self.api_key:
            # Local/dev fallback: return a simple deterministic summary so
            # the AI endpoints remain usable without an external API key.
            logger.warning("GROQ_API_KEY not configured — using local stub summary")
            # If the input includes a SAMPLE_EMPLOYEES JSON block, try to parse
            # and produce a concise summary (count, keys, and a few examples).
            try:
                marker = "SAMPLE_EMPLOYEES:"
                if marker in text:
                    payload = text.split(marker, 1)[1].strip()
                    # payload may include trailing text; attempt to find JSON
                    # first try to parse entire payload
                    try:
                        data = json.loads(payload)
                    except Exception:
                        # fallback: try to extract first JSON object/array substring
                        start = payload.find("{")
                        if start == -1:
                            start = payload.find("[")
                        if start != -1:
                            # crude attempt to get JSON substring
                            substring = payload[start:]
                            try:
                                data = json.loads(substring)
                            except Exception:
                                data = None
                        else:
                            data = None

                    if isinstance(data, list):
                        count = len(data)
                        keys = sorted(list({k for item in data if isinstance(item, dict) for k in item.keys()}))
                        examples = json.dumps(data[:3], ensure_ascii=False)
                        return (
                            f"[LOCAL STUB SUMMARY] employees={count} | columns={keys} | examples={examples}"
                        )
                    elif isinstance(data, dict):
                        # single object
                        keys = sorted(list(data.keys()))
                        return f"[LOCAL STUB SUMMARY] object_keys={keys} | sample={json.dumps(data, ensure_ascii=False)[:400]}"

                # generic fallback preview
                preview = text if len(text) < 1000 else text[:1000] + "..."
                return f"[LOCAL STUB SUMMARY] preview={preview[:200]} | length={len(text)}"
            except Exception:
                return "[LOCAL STUB SUMMARY] (unable to summarize input)"

        # Use chat completions endpoint for Groq
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        # Use messages format for chat completion
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": text}
            ],
            "temperature": 0.7
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
                try:
                    resp.raise_for_status()
                except httpx.HTTPStatusError:
                    logger.error("Groq API error: %s %s", resp.status_code, resp.text)
                    # propagate so caller can see status code
                    raise
                data = resp.json()
                # Chat completions response format
                choices = data.get("choices")
                if isinstance(choices, list) and choices:
                    message = choices[0].get("message")
                    if message:
                        return message.get("content", "")
                # fallback to raw text
                return data.get("text", "")
        except (httpx.RequestError, OSError) as e:
            # network problem (DNS, no connection, etc.)
            logger.error("Groq network error: %s", str(e))
            try:
                sample_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data", "sample.json"))
                if os.path.exists(sample_path):
                    with open(sample_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if isinstance(data, list):
                        count = len(data)
                        keys = sorted(list({k for item in data if isinstance(item, dict) for k in item.keys()}))
                        examples = json.dumps(data[:3], ensure_ascii=False)
                        return f"[LOCAL STUB SUMMARY] employees={count} | columns={keys} | examples={examples}"
                    elif isinstance(data, dict):
                        keys = sorted(list(data.keys()))
                        return f"[LOCAL STUB SUMMARY] object_keys={keys} | sample={json.dumps(data, ensure_ascii=False)[:400]}"
            except Exception:
                logger.exception("Failed to load local sample for fallback")

            # final fallback: return a simple preview string
            return f"[LOCAL STUB SUMMARY due to network error: {str(e)}]"

