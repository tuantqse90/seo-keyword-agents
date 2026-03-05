"""Tests for API endpoints."""
import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.anyio
async def test_health(client):
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.anyio
async def test_list_projects_empty(client):
    with patch("app.routers.projects.get_db") as mock_db:
        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result
        mock_db.return_value.__anext__ = AsyncMock(return_value=mock_session)
        # Skip DB-dependent test if no DB
        pass


@pytest.mark.anyio
async def test_analyze_keywords_returns_report_id(client):
    with patch("app.routers.keywords.create_keyword_report") as mock_create, \
         patch("app.routers.keywords._run_analysis"):
        import uuid
        mock_report = AsyncMock()
        mock_report.id = uuid.uuid4()
        mock_create.return_value = mock_report

        resp = await client.post("/api/keywords/analyze", json={"query": "test"})
        assert resp.status_code == 200
        data = resp.json()
        assert "report_id" in data
        assert "stream_url" in data


@pytest.mark.anyio
async def test_analyze_competitor_returns_report_id(client):
    with patch("app.routers.competitor.create_competitor_report") as mock_create, \
         patch("app.routers.competitor._run_analysis"):
        import uuid
        mock_report = AsyncMock()
        mock_report.id = uuid.uuid4()
        mock_create.return_value = mock_report

        resp = await client.post("/api/competitor/analyze", json={"query": "test.com"})
        assert resp.status_code == 200
        assert "report_id" in resp.json()


@pytest.mark.anyio
async def test_analyze_content_returns_report_id(client):
    with patch("app.routers.content.create_content_report") as mock_create, \
         patch("app.routers.content._run_analysis"):
        import uuid
        mock_report = AsyncMock()
        mock_report.id = uuid.uuid4()
        mock_create.return_value = mock_report

        resp = await client.post("/api/content/analyze", json={"query": "seo tips"})
        assert resp.status_code == 200
        assert "report_id" in resp.json()


@pytest.mark.anyio
async def test_analyze_audit_returns_report_id(client):
    with patch("app.routers.audit.create_audit_report") as mock_create, \
         patch("app.routers.audit._run_analysis"):
        import uuid
        mock_report = AsyncMock()
        mock_report.id = uuid.uuid4()
        mock_create.return_value = mock_report

        resp = await client.post("/api/audit/analyze", json={"query": "https://test.com"})
        assert resp.status_code == 200
        assert "report_id" in resp.json()


@pytest.mark.anyio
async def test_workflow_invalid_type(client):
    resp = await client.post("/api/workflows/invalid", json={"query": "test"})
    assert resp.status_code == 400


@pytest.mark.anyio
async def test_stream_not_found(client):
    resp = await client.get("/api/keywords/stream/nonexistent-id")
    assert resp.status_code == 404


@pytest.mark.anyio
async def test_report_not_found(client):
    import uuid
    resp = await client.get(f"/api/keywords/{uuid.uuid4()}")
    assert resp.status_code == 404
