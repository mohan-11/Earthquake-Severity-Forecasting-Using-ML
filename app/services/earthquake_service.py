from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable

import httpx
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.earthquake import Earthquake

logger = logging.getLogger(__name__)


USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_week.geojson"


@dataclass(frozen=True)
class AlertRules:
    danger_threshold: float = 5.5
    warning_threshold: float = 4.0


class EarthquakeService:
    def __init__(self, rules: AlertRules | None = None) -> None:
        self.rules = rules or AlertRules()

    def classify_alert(self, magnitude: float) -> str:
        if magnitude >= self.rules.danger_threshold:
            return "DANGER"
        if magnitude >= self.rules.warning_threshold:
            return "WARNING"
        return "SAFE"

    def _parse_time_ms(self, time_ms: Any) -> datetime | None:
        # USGS provides time as milliseconds since epoch.
        if time_ms is None:
            return None
        try:
            ms = int(time_ms)
            seconds, milliseconds = divmod(ms, 1000)
            # Avoid float rounding so deduplication on (time, location) is stable.
            return datetime.fromtimestamp(seconds, tz=timezone.utc) + timedelta(
                milliseconds=milliseconds
            )
        except (TypeError, ValueError):
            return None

    def parse_usgs_geojson(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        features: Iterable[dict[str, Any]] = payload.get("features") or []
        records: list[dict[str, Any]] = []

        for feature in features:
            props = feature.get("properties") or {}
            geom = feature.get("geometry") or {}

            magnitude = props.get("mag")
            location = props.get("place")
            time = self._parse_time_ms(props.get("time"))

            coordinates = geom.get("coordinates") or []
            # USGS format: [longitude, latitude, depth]
            if len(coordinates) < 3:
                continue
            lon, lat, depth = coordinates[0], coordinates[1], coordinates[2]

            if magnitude is None or location is None or time is None:
                continue

            try:
                magnitude_f = float(magnitude)
                depth_f = float(depth) if depth is not None else 0.0
                lat_f = float(lat)
                lon_f = float(lon)
            except (TypeError, ValueError):
                continue

            records.append(
                {
                    "magnitude": magnitude_f,
                    "depth": depth_f,
                    "latitude": lat_f,
                    "longitude": lon_f,
                    "location": str(location),
                    "time": time,
                    "alert_level": self.classify_alert(magnitude_f),
                }
            )

        return records

    async def fetch_live(self, *, max_items: int | None = None) -> list[dict[str, Any]]:
        """Fetch and parse the USGS feed without persisting."""
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(USGS_URL)
            resp.raise_for_status()
            payload = resp.json()

        records = self.parse_usgs_geojson(payload)
        if max_items is not None:
            records = records[:max_items]
        return records

    async def fetch_parse_classify_and_save(
        self,
        session: AsyncSession,
        *,
        max_items: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Fetch USGS data, classify alerts, and store in SQLite.

        Duplicate avoidance:
        We rely on a unique constraint on (time, location) and use SQLite
        `ON CONFLICT DO NOTHING`.
        """
        records = await self.fetch_live(max_items=max_items)
        if not records:
            return []

        stmt = sqlite_insert(Earthquake).values(records)
        stmt = stmt.on_conflict_do_nothing(index_elements=["time", "location"])
        await session.execute(stmt)
        await session.commit()
        logger.info("Stored %d earthquake record(s) (duplicates ignored).", len(records))
        return records

    # ---------------------------------------------------------------------
    # Compatibility wrapper for router layer.
    # The project requirements refer to this function name.
    # ---------------------------------------------------------------------
    async def process_and_store_earthquakes(
        self,
        db: AsyncSession,
        *,
        max_items: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Fetch USGS data, classify alerts, and store into DB.

        Returns the parsed-but-not-DB-ID records inserted (duplicates may be
        ignored by DB constraints).
        """
        return await self.fetch_parse_classify_and_save(db, max_items=max_items)


# ---------------------------------------------------------------------------
# Module-level convenience function (required by router requirements).
# ---------------------------------------------------------------------------
_default_service = EarthquakeService()


async def process_and_store_earthquakes(
    db: AsyncSession,
    *,
    max_items: int | None = None,
) -> list[dict[str, Any]]:
    """
    Fetch USGS data, classify alerts, and store into DB.

    This is a thin wrapper around the default service instance so the router
    can call `process_and_store_earthquakes(db)` directly.
    """
    return await _default_service.process_and_store_earthquakes(db, max_items=max_items)

