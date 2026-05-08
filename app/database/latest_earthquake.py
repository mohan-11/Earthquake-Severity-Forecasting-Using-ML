from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.earthquake import Earthquake

logger = logging.getLogger(__name__)


async def get_latest_earthquake(db: AsyncSession) -> Optional[Earthquake]:
    """
    Get the most recent earthquake from the database.
    
    Args:
        db: Async database session
        
    Returns:
        Earthquake: The most recent earthquake record, or None if no records exist
    """
    try:
        # Query the latest earthquake by time (descending order)
        result = await db.execute(
            select(Earthquake)
            .order_by(desc(Earthquake.time))
            .limit(1)
        )
        
        latest_earthquake = result.scalar_one_or_none()
        
        if latest_earthquake:
            logger.info(f"Retrieved latest earthquake: magnitude={latest_earthquake.magnitude}, time={latest_earthquake.time}")
        else:
            logger.warning("No earthquakes found in database")
            
        return latest_earthquake
        
    except Exception as e:
        logger.error(f"Error retrieving latest earthquake: {e}")
        raise


# Import select function
from sqlalchemy import select
