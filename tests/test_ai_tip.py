import os
import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from settings import get_dev_settings
from common.app_factory import create_app


@pytest.mark.asyncio
async def test_ai_tip_fallback_works_without_keys(monkeypatch):
    # Ensure no API keys to force fallback
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    settings = get_dev_settings()
    app = create_app(settings)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # We expect upstream services to not be running in unit tests;
        # so we skip calling them by monkeypatching service calls.
        from ai import routes as air

        async def fake_breakdown(budget, duration):
            return {
                "categories": {"food": "500", "transportation": "200", "utilities": "200", "emergency_fund": "50", "discretionary": "50"},
                "total_essential": "900",
                "total_savings": "100",
            }

        async def fake_savings(budget):
            return {"monthly_projections": ["100", "200"], "emergency_fund_progress": "10.0", "what_if_scenarios": {}}

        monkeypatch.setattr(air, "_get_budget_breakdown", fake_breakdown)
        monkeypatch.setattr(air, "_get_savings_forecast", fake_savings)

        resp = await ac.post("/api/tip", json={"budget": "1000", "duration": "monthly"})
        assert resp.status_code == 200
        data = resp.json()
        assert "tip" in data
        assert "Advice:" in data["tip"]
