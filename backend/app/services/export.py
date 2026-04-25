from __future__ import annotations

from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

from sqlalchemy.orm import Session

from app.db.models import GeneratedFile, Project


def _write_generated_file(archive: ZipFile, generated_file: GeneratedFile) -> None:
    archive.writestr(generated_file.file_path, generated_file.content)


def build_project_zip(session: Session, project: Project) -> bytes:
    buffer = BytesIO()
    with ZipFile(buffer, "w", compression=ZIP_DEFLATED) as archive:
        for generated_file in project.generated_files:
            _write_generated_file(archive, generated_file)
    return buffer.getvalue()
