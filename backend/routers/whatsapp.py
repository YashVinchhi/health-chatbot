from fastapi import APIRouter, HTTPException, Depends
from services import vaccination, outbreak
from db import crud, models
from utils import security

router = APIRouter()

@router.post("/webhook")
async def whatsapp_webhook(message: dict):
    """
    Handle incoming WhatsApp messages via webhook
    """
    try:
        # Process incoming message
        return {"message": "Message processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def whatsapp_status():
    """
    Check WhatsApp connection status
    """
    return {"status": "connected"}