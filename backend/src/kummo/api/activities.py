from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from ..config import Settings, get_settings
from ..db import get_supabase
from ..models import Activity, ActivityCreate

router = APIRouter(tags=["activities"])


@router.get("/activities", response_model=list[Activity])
def list_activities(
    shop_id: UUID | None = Query(None),
    age_group: str | None = Query(None),
    settings: Settings = Depends(get_settings),
) -> list[Activity]:
    client = get_supabase(settings)
    q = client.from_("activities").select("*")
    if shop_id:
        q = q.eq("shop_id", str(shop_id))
    if age_group:
        q = q.eq("age_group", age_group)
    result = q.execute()
    return result.data


@router.post("/activities", response_model=Activity, status_code=201)
def create_activity(
    body: ActivityCreate,
    settings: Settings = Depends(get_settings),
) -> Activity:
    client = get_supabase(settings)
    result = (
        client.from_("activities").insert(body.model_dump(mode="json")).execute()
    )
    return result.data[0]


@router.get("/activities/{activity_id}", response_model=Activity)
def get_activity(
    activity_id: UUID,
    settings: Settings = Depends(get_settings),
) -> Activity:
    client = get_supabase(settings)
    result = (
        client.from_("activities").select("*").eq("id", str(activity_id)).maybe_single().execute()
    )
    if result.data is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    return result.data
