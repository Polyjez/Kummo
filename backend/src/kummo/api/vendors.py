from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import orm
from ..db import get_session
from ..models import Vendor

router = APIRouter(tags=["vendors"])


@router.get("/vendors", response_model=list[Vendor])
async def list_vendors(session: AsyncSession = Depends(get_session)) -> list[Vendor]:
    rows = await session.scalars(select(orm.Vendor).order_by(orm.Vendor.name))
    return [Vendor.model_validate(row) for row in rows]
