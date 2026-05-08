from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, UniqueConstraint

from app.database.session import Base


class Earthquake(Base):
    """
    Earthquake record stored in SQLite.

    alert_level values:
    - SAFE
    - WARNING
    - DANGER
    """

    __tablename__ = "earthquakes"

    __table_args__ = (
        # Duplicate avoidance: do not store multiple entries for the same event time+location.
        UniqueConstraint("time", "location", name="uq_earthquakes_time_location"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    magnitude = Column(Float, nullable=False)
    depth = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location = Column(String(255), nullable=False)
    time = Column(DateTime(timezone=True), nullable=False)
    alert_level = Column(String(16), nullable=False)  # SAFE/WARNING/DANGER

    def __repr__(self) -> str:
        return (
            "Earthquake("
            f"id={self.id!r}, magnitude={self.magnitude!r}, location={self.location!r}, "
            f"time={self.time!r}, alert_level={self.alert_level!r}"
            ")"
        )

