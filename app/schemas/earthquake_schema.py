from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class EarthquakeBase(BaseModel):
    magnitude: float
    depth: float
    latitude: float
    longitude: float
    location: str
    time: datetime
    alert_level: str = Field(..., description="SAFE, WARNING, or DANGER")


class EarthquakeOut(EarthquakeBase):
    model_config = ConfigDict(from_attributes=True)

    # For "live" data we haven't persisted yet, so id may be unknown.
    id: int | None = None


class EarthquakeListResponse(BaseModel):
    count: int
    items: list[EarthquakeOut]


class EarthquakeLiveResponse(BaseModel):
    source: str = "usgs"
    count: int
    items: list[EarthquakeOut]


class HealthResponse(BaseModel):
    status: str = "ok"
    database: str

