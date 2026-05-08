from __future__ import annotations

from pydantic import BaseModel


class PredictionRequest(BaseModel):
    magnitude: float
    depth: float
    latitude: float
    longitude: float


class PredictionResponse(BaseModel):
    prediction: str
    confidence: float

