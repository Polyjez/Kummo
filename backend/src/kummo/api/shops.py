from fastapi import APIRouter, Depends
from ..config import Settings, get_settings
from ..db import get_supabase
from ..models import Shop

router = APIRouter(tags=["shops"])


@router.get("/shops", response_model=list[Shop])
def list_shops(settings: Settings = Depends(get_settings)) -> list[Shop]:
    client = get_supabase(settings)
    result = client.from_("shops").select("*").execute()
    return result.data
