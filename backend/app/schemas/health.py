from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Schema for service health check response."""

    status: str = "ok"
    service: str = "dinespace-backend"
