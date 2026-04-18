from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db.models import Project, User
from app.db.session import get_db


DbSession = Annotated[Session, Depends(get_db)]


def require_user(request: Request, db: DbSession) -> User:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )

    user = db.get(User, user_id)
    if user is None:
        request.session.clear()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )
    return user


CurrentUser = Annotated[User, Depends(require_user)]


def get_owned_project(project_id: str, db: DbSession, user: CurrentUser) -> Project:
    project = db.get(Project, project_id)
    if project is None or project.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    return project


OwnedProject = Annotated[Project, Depends(get_owned_project)]
