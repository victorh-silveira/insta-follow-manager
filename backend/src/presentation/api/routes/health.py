"""Health-check endpoint."""

from fastapi import APIRouter, Depends

from src.domain.gateways.instagram_gateway import InstagramGateway
from src.presentation.api.dependencies import get_instagram_gateway

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health_check(
    gateway: InstagramGateway = Depends(get_instagram_gateway),
) -> dict[str, str]:
    """Return service health and active Instagram gateway mode."""
    return {"status": "ok", "gateway_mode": gateway.mode_name}
