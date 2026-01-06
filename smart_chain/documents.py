from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class Document:
    page_content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: Optional[None] = None
    embedding_value: Optional[None] = None
