from fastapi import APIRouter, HTTPException
from ..services import vaccination, outbreak
from ..db import crud, models

router = APIRouter()

@router.post("/webhook")
async def sms_webhook(message: dict):
    """
    Handle incoming SMS messages via webhook
    """
    try:
        # Process incoming SMS
        return {"message": "SMS processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def sms_status():
    """
    Check SMS gateway status
    """
    return {"status": "connected"}