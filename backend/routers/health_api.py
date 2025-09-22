from fastapi import APIRouter, HTTPException
from ..services import vaccination, outbreak

router = APIRouter()

@router.get("/vaccines/{age}")
async def get_vaccine_schedule(age: float):
    """
    Get vaccination schedule for given age
    """
    try:
        schedule = await vaccination.get_schedule(age)
        return schedule
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/outbreaks/{location}")
async def get_outbreaks(location: str):
    """
    Get disease outbreaks for given location
    """
    try:
        alerts = await outbreak.get_alerts(location)
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))