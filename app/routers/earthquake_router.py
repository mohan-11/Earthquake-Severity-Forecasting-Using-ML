from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.earthquake import Earthquake
from app.schemas.earthquake_schema import EarthquakeListResponse, EarthquakeOut
from app.services.earthquake_service import process_and_store_earthquakes

# Router-level prefix/tag so endpoints become:
#   /earthquakes/live, /earthquakes/history, /earthquakes/latest
router = APIRouter(prefix="/earthquakes", tags=["Earthquakes"])


@router.get("/live", response_model=EarthquakeOut)
async def live_earthquakes(
    db: AsyncSession = Depends(get_db),
    max_items: Annotated[int, Query(ge=1, le=1000)] = 50,
) -> EarthquakeOut:
    """
    Fetch fresh USGS data, process/classify it, store into DB, then return
    the latest stored earthquake record.
    """
    await process_and_store_earthquakes(db, max_items=max_items)

    stmt = select(Earthquake).order_by(desc(Earthquake.time)).limit(1)
    result = await db.execute(stmt)
    item = result.scalars().first()
    if item is None:
        # This can happen if USGS returned nothing or parsing skipped everything.
        raise HTTPException(status_code=404, detail="No earthquake records available.")
    return item


@router.get("/history", response_model=EarthquakeListResponse)
async def history_earthquakes(
    db: AsyncSession = Depends(get_db),
) -> EarthquakeListResponse:
    """
    Return stored earthquake data ordered by latest first.
    """
    stmt = select(Earthquake).order_by(desc(Earthquake.time))
    result = await db.execute(stmt)
    items = list(result.scalars().all())

    if not items:
        raise HTTPException(status_code=404, detail="No earthquake history in database yet.")
    return EarthquakeListResponse(count=len(items), items=items)


@router.get("/latest", response_model=EarthquakeOut)
async def latest_earthquake(db: AsyncSession = Depends(get_db)) -> EarthquakeOut:
    """Return the most recent earthquake record from the database."""
    stmt = select(Earthquake).order_by(desc(Earthquake.time)).limit(1)
    result = await db.execute(stmt)
    item = result.scalars().first()
    if item is None:
        raise HTTPException(status_code=404, detail="No earthquake records in database yet.")
    return item

