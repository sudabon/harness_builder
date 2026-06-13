from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ProjectCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    preset_id: str | None = None


class AnswersUpdateRequest(BaseModel):
    answers: dict[str, Any]


class GeneratedFileResponse(BaseModel):
    id: str
    file_path: str
    content: str
    is_edited: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GeneratedFileSummaryResponse(BaseModel):
    id: str
    file_path: str
    is_edited: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GeneratedFilesListResponse(BaseModel):
    items: list[GeneratedFileSummaryResponse]


class FileUpdateRequest(BaseModel):
    content: str


class GenerateFilesRequest(BaseModel):
    force: bool = False


class ProjectResponse(BaseModel):
    id: str
    name: str
    preset_id: str | None
    answers: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
