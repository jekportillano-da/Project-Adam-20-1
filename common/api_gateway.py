import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Any, Dict

from common.resilience import ServiceClient

logger = logging.getLogger(__name__)


def create_api_routes(settings) -> APIRouter:
    """Create API gateway routes that proxy to internal microservices."""
    router = APIRouter(prefix="/api", tags=["gateway"])

    @router.get("/health")
    async def api_health():
        return {"status": "ok"}

    @router.post("/budget/calculate")
    async def budget_calculate(payload: Dict[str, Any]):
        try:
            client = ServiceClient(base_url=settings.budget_service_url, timeout=10.0)
            resp = await client.post("/calculate", json=payload)
            return JSONResponse(content=resp.json(), status_code=resp.status_code)
        except HTTPException as he:
            raise he
        except Exception as e:
            logger.exception("Budget service error")
            raise HTTPException(status_code=502, detail=f"Budget service unavailable: {e}")

    @router.post("/savings/forecast")
    async def savings_forecast(payload: Dict[str, Any]):
        try:
            client = ServiceClient(base_url=settings.savings_service_url, timeout=10.0)
            resp = await client.post("/forecast", json=payload)
            return JSONResponse(content=resp.json(), status_code=resp.status_code)
        except HTTPException as he:
            raise he
        except Exception as e:
            logger.exception("Savings service error")
            raise HTTPException(status_code=502, detail=f"Savings service unavailable: {e}")

    @router.post("/insights/analyze")
    async def insights_analyze(payload: Dict[str, Any]):
        try:
            client = ServiceClient(base_url=settings.insights_service_url, timeout=10.0)
            resp = await client.post("/analyze", json=payload)
            return JSONResponse(content=resp.json(), status_code=resp.status_code)
        except HTTPException as he:
            raise he
        except Exception as e:
            logger.exception("Insights service error")
            raise HTTPException(status_code=502, detail=f"Insights service unavailable: {e}")

    return router
