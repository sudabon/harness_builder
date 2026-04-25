from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.questionnaire import answer_value_as_list as _answer_value_as_list
from app.db.models import Project, QuestionnaireAnswer


def serialize_answer(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def deserialize_answer(raw: str) -> Any:
    return json.loads(raw)


def answer_value_as_list(value: Any) -> list[str]:
    return _answer_value_as_list(value)


def get_project_answers(session: Session, project: Project) -> dict[str, Any]:
    rows: Sequence[QuestionnaireAnswer]
    if "answers" in project.__dict__:
        rows = project.answers
    else:
        rows = session.scalars(
            select(QuestionnaireAnswer).where(
                QuestionnaireAnswer.project_id == project.id
            )
        ).all()
    return {row.question_key: deserialize_answer(row.answer_value) for row in rows}


def upsert_project_answers(
    session: Session, project: Project, answers: dict[str, Any]
) -> dict[str, Any]:
    current_rows = {
        row.question_key: row
        for row in session.scalars(
            select(QuestionnaireAnswer).where(
                QuestionnaireAnswer.project_id == project.id
            )
        ).all()
    }

    for key, value in answers.items():
        serialized = serialize_answer(value)
        if key in current_rows:
            current_rows[key].answer_value = serialized
        else:
            session.add(
                QuestionnaireAnswer(
                    project_id=project.id,
                    question_key=key,
                    answer_value=serialized,
                )
            )

    session.flush()
    session.refresh(project)
    return get_project_answers(session, project)
