from typing import Any, Dict, List

class BaseConnector:
    """Abstract connector. Implementations must provide async connect and metadata methods."""

    async def connect(self) -> Any:
        raise NotImplementedError()

    async def get_tables(self) -> List[Dict[str, Any]]:
        raise NotImplementedError()

    async def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        raise NotImplementedError()
