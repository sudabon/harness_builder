from fastapi import APIRouter

from app.core.presets import PRESETS
from app.schemas.preset import PresetResponse

router = APIRouter(prefix="/presets", tags=["presets"])


@router.get("", response_model=list[PresetResponse])
def list_presets() -> list[PresetResponse]:
    return [PresetResponse.model_validate(item) for item in PRESETS]
