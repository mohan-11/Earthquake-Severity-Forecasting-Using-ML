from __future__ import annotations

import logging
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Dict, Any

import joblib
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def load_ml_artifacts() -> tuple[Any, LabelEncoder, KMeans, LabelEncoder]:
    """
    Load all ML artifacts once globally for performance.
    
    Returns:
        tuple: (model, label_encoder, kmeans, depth_encoder)
    """
    try:
        project_root = Path(__file__).resolve().parents[2]
        
        # Load model artifacts
        model_path = project_root / "earthquake_model.pkl"
        label_encoder_path = project_root / "label_encoder.pkl"
        kmeans_path = project_root / "location_kmeans.pkl"
        depth_encoder_path = project_root / "depth_encoder.pkl"
        
        logger.info(f"Loading ML artifacts from {project_root}")
        
        model = joblib.load(model_path)
        label_encoder = joblib.load(label_encoder_path)
        kmeans = joblib.load(kmeans_path)
        depth_encoder = joblib.load(depth_encoder_path)
        
        logger.info("All ML artifacts loaded successfully")
        return model, label_encoder, kmeans, depth_encoder
        
    except Exception as e:
        logger.error(f"Failed to load ML artifacts: {e}")
        raise


def prepare_features(event: Dict[str, Any]) -> pd.DataFrame:
    """
    Feature engineering function for earthquake prediction.
    
    Args:
        event: Dictionary containing earthquake data with keys:
               magnitude, depth_km, latitude, longitude, time
        
    Returns:
        pd.DataFrame: DataFrame with engineered features matching training columns
    """
    try:
        # Extract basic features
        magnitude = float(event['magnitude'])
        depth_km = float(event['depth_km'])
        latitude = float(event['latitude'])
        longitude = float(event['longitude'])
        
        # Load encoders
        _, _, kmeans, depth_encoder = load_ml_artifacts()
        
        # A) magnitude_squared
        magnitude_squared = magnitude ** 2
        
        # B) hour_of_day (extract from timestamp)
        if 'time' in event:
            if isinstance(event['time'], str):
                # Parse timestamp string
                timestamp = pd.to_datetime(event['time'])
            else:
                # Assume it's already a datetime object
                timestamp = event['time']
            hour_of_day = timestamp.hour
        else:
            # Default to current hour if no time provided
            hour_of_day = datetime.now().hour
        
        # C) depth_category
        if depth_km <= 70:
            depth_category = "shallow"
        elif depth_km <= 300:
            depth_category = "intermediate"
        else:
            depth_category = "deep"
        
        # Encode depth category
        depth_category_encoded = depth_encoder.transform([depth_category])[0]
        
        # D) location_cluster
        location_coords = pd.DataFrame([[latitude, longitude]], columns=['latitude', 'longitude'])
        location_cluster = kmeans.predict(location_coords)[0]
        
        # Create feature DataFrame with exact training columns
        features = pd.DataFrame({
            'magnitude': [magnitude],
            'magnitude_squared': [magnitude_squared],
            'depth_km': [depth_km],
            'latitude': [latitude],
            'longitude': [longitude],
            'hour_of_day': [hour_of_day],
            'depth_category_encoded': [depth_category_encoded],
            'location_cluster': [location_cluster]
        })
        
        # Validate that features match expected training columns
        expected_columns = ['magnitude', 'magnitude_squared', 'depth_km', 'latitude', 'longitude', 'hour_of_day', 'depth_category_encoded', 'location_cluster']
        actual_columns = features.columns.tolist()
        
        if set(actual_columns) != set(expected_columns):
            missing_columns = set(expected_columns) - set(actual_columns)
            extra_columns = set(actual_columns) - set(expected_columns)
            
            logger.error(f"Feature columns mismatch!")
            logger.error(f"Expected: {expected_columns}")
            logger.error(f"Actual: {actual_columns}")
            logger.error(f"Missing: {missing_columns}")
            logger.error(f"Extra: {extra_columns}")
            
            raise ValueError(
                f"Feature columns do not match training columns. "
                f"Missing: {missing_columns}. Extra: {extra_columns}. "
                f"Expected: {expected_columns}"
            )
        
        logger.debug(f"Engineered features columns: {features.columns.tolist()}")
        logger.debug(f"Feature shape: {features.shape}")
        return features
        
        logger.debug(f"Engineered features: {features.columns.tolist()}")
        return features
        
    except Exception as e:
        logger.error(f"Feature engineering failed: {e}")
        raise


def predict_earthquake_severity(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predict earthquake severity using trained ML model.
    
    Args:
        event: Dictionary containing earthquake data
        
    Returns:
        Dict: Prediction response with predicted_alert, confidence, probabilities
    """
    try:
        logger.info(f"Processing earthquake prediction: {event.get('magnitude', 'unknown magnitude')} at {event.get('latitude', 'unknown')}, {event.get('longitude', 'unknown')}")
        
        # Load model artifacts
        model, label_encoder, _, _ = load_ml_artifacts()
        
        # Prepare features
        features = prepare_features(event)
        
        # Make prediction with probabilities
        probabilities = model.predict_proba(features)[0]
        predicted_index = int(probabilities.argmax())
        predicted_alert = label_encoder.inverse_transform([predicted_index])[0]
        confidence = float(probabilities[predicted_index])
        
        # Create probability dictionary for all classes
        prob_dict = {}
        for i, class_name in enumerate(label_encoder.classes_):
            prob_dict[class_name] = float(probabilities[i])
        
        response = {
            'predicted_alert': predicted_alert,
            'confidence': round(confidence, 3),
            'probabilities': prob_dict
        }
        
        logger.info(f"Prediction completed: {predicted_alert} with {confidence:.3f} confidence")
        return response
        
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
        logger.error(f"Prediction failed with traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error during prediction") from e


def validate_earthquake_data(event: Dict[str, Any]) -> None:
    """
    Validate earthquake event data before processing.
    
    Args:
        event: Dictionary containing earthquake data
        
    Raises:
        ValueError: If required fields are missing or invalid
    """
    required_fields = ['magnitude', 'depth_km', 'latitude', 'longitude']
    
    logger.info(f"Validating earthquake data: {event}")
    
    for field in required_fields:
        if field not in event:
            logger.warning(f"Missing required field: {field}")
            raise ValueError(f"Missing required field: {field}")
        
    for field in required_fields:
        try:
            float(event[field])
        except (ValueError, TypeError):
            logger.error(f"Invalid {field} value: {event[field]} - must be numeric")
            raise ValueError(f"Invalid {field}: must be numeric")
    
    # Validate reasonable ranges
    magnitude = float(event['magnitude'])
    depth = float(event['depth_km'])
    lat = float(event['latitude'])
    lon = float(event['longitude'])
    
    if not -2 <= magnitude <= 10:  # Reasonable earthquake magnitude range
        logger.error(f"Invalid magnitude: {magnitude}. Expected range: -2 to 10")
        raise ValueError(f"Invalid magnitude: {magnitude}. Expected range: -2 to 10")
    
    if not 0 <= depth <= 700:  # Reasonable depth range
        logger.error(f"Invalid depth: {depth}. Expected range: 0 to 700 km")
        raise ValueError(f"Invalid depth: {depth}. Expected range: 0 to 700 km")
    
    if not -90 <= lat <= 90:  # Valid latitude range
        logger.error(f"Invalid latitude: {lat}. Expected range: -90 to 90")
        raise ValueError(f"Invalid latitude: {lat}. Expected range: -90 to 90")
    
    if not -180 <= lon <= 180:  # Valid longitude range
        logger.error(f"Invalid longitude: {lon}. Expected range: -180 to 180")
        raise ValueError(f"Invalid longitude: {lon}. Expected range: -180 to 180")


def get_model_info() -> Dict[str, Any]:
    """
    Get information about the loaded ML model.
    
    Returns:
        Dict: Model information including classes and feature count
    """
    try:
        _, label_encoder, _, _ = load_ml_artifacts()
        
        return {
            'model_type': 'RandomForestClassifier',
            'alert_classes': label_encoder.classes_.tolist(),
            'num_classes': len(label_encoder.classes_),
            'features': [
                'magnitude', 'magnitude_squared', 'depth_km', 'latitude', 'longitude',
                'hour_of_day', 'depth_category_encoded', 'location_cluster'
            ],
            'feature_count': 8
        }
    except Exception as e:
        logger.error(f"Failed to get model info: {e}")
        raise
