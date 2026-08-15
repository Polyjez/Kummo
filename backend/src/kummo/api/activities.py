from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import orm
from ..db import get_session
from ..models import Activity, ActivityCreate

router = APIRouter(tags=["activities"])


@router.get("/activities", response_model=list[Activity])
async def list_activities(
    vendor_id: UUID | None = Query(None),
    age_group: str | None = Query(None),
    session: AsyncSession = Depends(get_session),
) -> list[Activity]:
    query = select(orm.Activity).order_by(orm.Activity.title)
    if vendor_id:
        query = query.where(orm.Activity.vendor_id == vendor_id)
    if age_group:
        query = query.where(orm.Activity.age_group == age_group)
    rows = await session.scalars(query)
    return [Activity.model_validate(row) for row in rows]


@router.post("/activities", response_model=Activity, status_code=201)
async def create_activity(
    body: ActivityCreate,
    session: AsyncSession = Depends(get_session),
) -> Activity:
    activity = orm.Activity(**body.model_dump())
    session.add(activity)
    await session.commit()
    await session.refresh(activity)
    return Activity.model_validate(activity)


@router.get("/activities/{activity_id}", response_model=Activity)
async def get_activity(
    activity_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> Activity:
    activity = await session.get(orm.Activity, activity_id)
    if activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    return Activity.model_validate(activity)
