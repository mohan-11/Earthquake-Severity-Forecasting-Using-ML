from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.ml.predict import predict_earthquake_severity, validate_earthquake_data, get_model_info

logger = logging.getLogger(__name__)

# Create router with /predict prefix
router = APIRouter(prefix="/predict", tags=["Earthquake Prediction"])


# Pydantic models for request/response
class EarthquakeEvent(BaseModel):
    """Schema for earthquake event data."""
    magnitude: float = Field(..., ge=-2, le=10, description="Earthquake magnitude")
    depth_km: float = Field(..., ge=0, le=700, description="Depth in kilometers")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    time: str = Field(None, description="Timestamp (ISO format or string)")

    class Config:
        schema_extra = {
            "example": {
                "magnitude": 5.2,
                "depth_km": 10.0,
                "latitude": 36.5,
                "longitude": -121.1,
                "time": "2024-01-15T14:30:00Z"
            }
        }


class PredictionResponse(BaseModel):
    """Schema for prediction response."""
    predicted_alert: str = Field(..., description="Predicted earthquake alert level")
    confidence: float = Field(..., ge=0, le=1, description="Prediction confidence score")
    probabilities: Dict[str, float] = Field(..., description="Probabilities for all alert levels")

    class Config:
        schema_extra = {
            "example": {
                "predicted_alert": "yellow",
                "confidence": 0.82,
                "probabilities": {
                    "green": 0.10,
                    "yellow": 0.82,
                    "orange": 0.06,
                    "red": 0.02
                }
            }
        }


class ModelInfo(BaseModel):
    """Schema for model information."""
    model_type: str
    alert_classes: list[str]
    num_classes: int
    features: list[str]
    feature_count: int


@router.post("/custom", response_model=PredictionResponse, summary="Predict earthquake severity for custom event")
async def predict_custom_earthquake(event: EarthquakeEvent) -> PredictionResponse:
    """
    Predict earthquake severity for a custom earthquake event.
    
    Accepts earthquake event data and returns ML prediction with confidence scores.
    
    - **magnitude**: Earthquake magnitude (-2 to 10)
    - **depth_km**: Depth in kilometers (0 to 700)
    - **latitude**: Latitude coordinate (-90 to 90)
    - **longitude**: Longitude coordinate (-180 to 180)
    - **time**: Optional timestamp string
    """
    try:
        logger.info(f"Received custom prediction request: magnitude={event.magnitude}, location=({event.latitude}, {event.longitude})")
        
        # Validate input data
        event_dict = event.dict()
        validate_earthquake_data(event_dict)
        
        # Make prediction
        prediction = predict_earthquake_severity(event_dict)
        
        logger.info(f"Custom prediction completed: {prediction['predicted_alert']} with {prediction['confidence']:.3f} confidence")
        return PredictionResponse(**prediction)
        
    except ValueError as e:
        logger.warning(f"Validation error in custom prediction: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e
    except FileNotFoundError as e:
        logger.error("Model artifacts not found for custom prediction")
        raise HTTPException(
            status_code=503,
            detail="ML model not available. Please ensure model training has been completed."
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error in custom prediction: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during prediction") from e


@router.get("/latest", response_model=PredictionResponse, summary="Predict severity for latest earthquake")
async def predict_latest_earthquake() -> PredictionResponse:
    """
    Predict earthquake severity for the latest earthquake in the database.
    
    Fetches the most recent earthquake record from the database and runs
    ML prediction to determine severity level.
    """
    try:
        logger.info("Received request for latest earthquake prediction")
        
        # Import here to avoid circular imports
        from app.database.latest_earthquake import get_latest_earthquake
        from app.database.session import AsyncSessionLocal
        
        # Get latest earthquake from database
        async with AsyncSessionLocal() as db:
            latest_earthquake = await get_latest_earthquake(db)
        
        if not latest_earthquake:
            logger.warning("No earthquakes found in database")
            raise HTTPException(status_code=404, detail="No earthquake data found in database")
        
        # Convert to event dictionary
        event_dict = {
            'magnitude': latest_earthquake.magnitude,
            'depth_km': latest_earthquake.depth,  # Map depth field to depth_km
            'latitude': latest_earthquake.latitude,
            'longitude': latest_earthquake.longitude,
            'time': latest_earthquake.time.isoformat() if latest_earthquake.time else None
        }
        
        logger.info(f"Processing latest earthquake: magnitude={event_dict['magnitude']}, location=({event_dict['latitude']}, {event_dict['longitude']})")
        
        # Make prediction
        prediction = predict_earthquake_severity(event_dict)
        
        logger.info(f"Latest earthquake prediction completed: {prediction['predicted_alert']} with {prediction['confidence']:.3f} confidence")
        return PredictionResponse(**prediction)
        
    except HTTPException:
        raise
    except FileNotFoundError as e:
        logger.error("Model artifacts not found for latest prediction")
        raise HTTPException(
            status_code=503,
            detail="ML model not available. Please ensure model training has been completed."
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error in latest prediction: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during prediction") from e


@router.get("/model-info", response_model=ModelInfo, summary="Get ML model information")
async def get_prediction_model_info() -> ModelInfo:
    """
    Get information about the loaded ML prediction model.
    
    Returns model details including:
    - Model type and architecture
    - Available alert classes
    - Feature list and count
    """
    try:
        logger.info("Request for model information")
        
        model_info = get_model_info()
        return ModelInfo(**model_info)
        
    except FileNotFoundError as e:
        logger.error("Model artifacts not found for model info")
        raise HTTPException(
            status_code=503,
            detail="ML model not available. Please ensure model training has been completed."
        ) from e
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while getting model info") from e


@router.get("/health", summary="Health check for prediction service")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint for the prediction service.
    
    Returns service status and model availability.
    """
    try:
        # Try to load model artifacts to verify they're available
        get_model_info()
        return {
            "status": "healthy",
            "model": "available",
            "timestamp": datetime.utcnow().isoformat()
        }
    except FileNotFoundError:
        return {
            "status": "degraded",
            "model": "unavailable",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "model": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }
