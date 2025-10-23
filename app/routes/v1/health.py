from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/health", tags=["health"])


class HealthChecks(BaseModel):
    status: str


@router.get(
    "/readiness",
    response_model=HealthChecks,
    responses={
        200: {
            "content": {"application/json": {"example": {"status": "ready"}}},
            "description": "verify if the service is ready to receive traffic",
        }
    },
)
def readiness() -> object:
    return {"status": "ready"}


@router.get(
    "/liveness",
    response_model=HealthChecks,
    responses={
        200: {
            "content": {"application/json": {"example": {"status": "alive"}}},
            "description": "Uses to know when a to restart the container(kubernetes)",
        }
    },
)
def liveness() -> object:
    return {"status": "alive"}
