from fastapi import Depends, HTTPException, Header
from typing import Optional


def verify_signature(signature: Optional[str], payload: Optional[str] = None) -> bool:
    """Placeholder signature verification. Replace with real implementation.

    For now, returns True if a signature header is provided; otherwise False.
    """
    if signature:
        return True
    return False


async def require_valid_signature(x_whatsapp_signature: Optional[str] = Header(None)) -> bool:
    """FastAPI dependency to require a signature header on incoming requests.

    Raises HTTP 401 if missing or invalid.
    """
    if not verify_signature(x_whatsapp_signature):
        raise HTTPException(status_code=401, detail="Invalid or missing signature")
    return True


# Export names expected by the codebase
__all__ = ["verify_signature", "require_valid_signature"]

