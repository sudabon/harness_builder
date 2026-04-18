from typing import Any

from pydantic import BaseModel


class PresetResponse(BaseModel):
    id: str
    name: str
    description: str
    answers: dict[str, Any]
