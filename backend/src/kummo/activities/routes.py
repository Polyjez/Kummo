import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.dependencies import get_current_vendor
from ..auth.profiles import Profile
from ..db import get_session
from . import data_model
from .api_model import Activity, ActivityCreate

logger = logging.getLogger(__name__)

router = APIRouter(tags=["activities"])


@router.get("/activities", response_model=list[Activity])
async def list_activities(
    vendor_id: UUID | None = Query(None),
    age_group: str | None = Query(None),
    session: AsyncSession = Depends(get_session),
) -> list[Activity]:
    query = select(data_model.Activity).order_by(data_model.Activity.title)
    if vendor_id:
        query = query.where(data_model.Activity.vendor_id == vendor_id)
    if age_group:
        query = query.where(data_model.Activity.age_group == age_group)
    rows = await session.scalars(query)
    return [Activity.model_validate(row) for row in rows]


@router.post("/activities", response_model=Activity, status_code=201)
async def create_activity(
    body: ActivityCreate,
    vendor: Profile = Depends(get_current_vendor),
    session: AsyncSession = Depends(get_session),
) -> Activity:
    """Create an activity for the signed-in vendor.

    The owner is taken from the session rather than the body, so the route cannot be
    used to file an activity under another vendor.
    """
    activity = data_model.Activity(**body.model_dump(), vendor_id=vendor.id)
    session.add(activity)
    await session.commit()
    await session.refresh(activity)
    logger.info("Vendor %s created activity %s", vendor.id, activity.id)
    return Activity.model_validate(activity)


@router.get("/activities/{activity_id}", response_model=Activity)
async def get_activity(
    activity_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> Activity:
    activity = await session.get(data_model.Activity, activity_id)
    if activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    return Activity.model_validate(activity)
