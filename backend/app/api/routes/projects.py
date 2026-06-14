from __future__ import annotations

from io import BytesIO

from fastapi import APIRouter, HTTPException, Response, status
from fastapi.responses import StreamingResponse

from app.api.deps import CurrentUser, DbSession, OwnedProject
from app.core.questionnaire import (
    missing_required_answer_keys,
    normalize_answers_payload_for_storage,
    validate_answers_payload,
)
from app.db.models import Project
from app.schemas.project import (
    AnswersUpdateRequest,
    FileUpdateRequest,
    GenerateFilesRequest,
    GeneratedFileResponse,
    GeneratedFilesListResponse,
    GeneratedFileSummaryResponse,
    ProjectCreateRequest,
    ProjectResponse,
)
from app.services.answers import get_project_answers, upsert_project_answers
from app.services.export import build_project_zip
from app.services.generator import generate_project_change

router = APIRouter(prefix="/projects", tags=["projects"])


def _project_response(db: DbSession, project: Project) -> ProjectResponse:
    return ProjectResponse(
        id=project.id,
        name=project.name,
        preset_id=project.preset_id,
        answers=get_project_answers(db, project),
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreateRequest, db: DbSession, user: CurrentUser
) -> ProjectResponse:
    project = Project(user_id=user.id, name=payload.name, preset_id=payload.preset_id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return _project_response(db, project)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project: OwnedProject, db: DbSession) -> ProjectResponse:
    return _project_response(db, project)


@router.put("/{project_id}/answers", response_model=ProjectResponse)
def update_answers(
    payload: AnswersUpdateRequest,
    project: OwnedProject,
    db: DbSession,
) -> ProjectResponse:
    errors = validate_answers_payload(payload.answers)
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid answers: {'; '.join(errors)}",
        )

    upsert_project_answers(
        db, project, normalize_answers_payload_for_storage(payload.answers)
    )
    db.commit()
    db.refresh(project)
    return _project_response(db, project)


@router.post("/{project_id}/generate", response_model=GeneratedFilesListResponse)
def generate_files(
    project: OwnedProject,
    db: DbSession,
    payload: GenerateFilesRequest | None = None,
) -> GeneratedFilesListResponse:
    answers = get_project_answers(db, project)
    missing = missing_required_answer_keys(answers)
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required answers: {', '.join(missing)}",
        )

    force = payload.force if payload is not None else False
    generated = generate_project_change(db, project, force=force)
    db.commit()
    ordered = sorted(generated, key=lambda item: item.file_path)
    return GeneratedFilesListResponse(
        items=[GeneratedFileSummaryResponse.model_validate(item) for item in ordered]
    )


@router.get("/{project_id}/files", response_model=GeneratedFilesListResponse)
def list_files(project: OwnedProject) -> GeneratedFilesListResponse:
    ordered = sorted(project.generated_files, key=lambda item: item.file_path)
    return GeneratedFilesListResponse(
        items=[GeneratedFileSummaryResponse.model_validate(item) for item in ordered]
    )


@router.get("/{project_id}/files/{file_id}", response_model=GeneratedFileResponse)
def get_file(project: OwnedProject, file_id: str) -> GeneratedFileResponse:
    file = next((item for item in project.generated_files if item.id == file_id), None)
    if file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )
    return GeneratedFileResponse.model_validate(file)


@router.put("/{project_id}/files/{file_id}", response_model=GeneratedFileResponse)
def update_file(
    payload: FileUpdateRequest,
    project: OwnedProject,
    file_id: str,
    db: DbSession,
) -> GeneratedFileResponse:
    file = next((item for item in project.generated_files if item.id == file_id), None)
    if file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )

    if file.content != payload.content:
        file.content = payload.content
        file.is_edited = True
        db.commit()
    db.refresh(file)
    return GeneratedFileResponse.model_validate(file)


@router.get("/{project_id}/export")
def export_project(project: OwnedProject, db: DbSession) -> Response:
    result = build_project_zip(db, project)
    filename = f"{project.name.replace(' ', '-').lower() or 'project'}-harness.zip"
    return StreamingResponse(
        BytesIO(result),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
