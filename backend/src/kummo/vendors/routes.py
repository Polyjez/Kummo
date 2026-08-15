from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from . import data_model
from .api_model import Vendor

router = APIRouter(tags=["vendors"])


@router.get("/vendors", response_model=list[Vendor])
async def list_vendors(session: AsyncSession = Depends(get_session)) -> list[Vendor]:
    rows = await session.scalars(
        select(data_model.Vendor).order_by(data_model.Vendor.name)
    )
    return [Vendor.model_validate(row) for row in rows]
