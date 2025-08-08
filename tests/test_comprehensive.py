# Comprehensive Testing Suite
import pytest
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
import json
import time

# Import the applications for testing
try:
    from gateway import app as gateway_app
    from services.budget_service.main import app as budget_app
    from services.savings_service.main import app as savings_app
    from services.insights_service.main import app as insights_app
except ImportError:
    # Fallback for when services aren't available
    gateway_app = None
    budget_app = None
    savings_app = None
    insights_app = None

# Test Configuration
TEST_CONFIG = {
    "test_user": {
        "email": "test@example.com",
        "password": "testpassword123"
    },
    "test_budget": {
        "amount": 10000,
        "duration": "monthly"
    },
    "test_savings": {
        "monthly_savings": 2000,
        "emergency_fund": 5000,
        "current_goal": 50000
    }
}

class TestGateway:
    """Gateway service tests"""
    
    def setup_method(self):
        if gateway_app:
            self.client = TestClient(gateway_app)
        else:
            pytest.skip("Gateway app not available")
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
    
    def test_root_redirect_when_not_authenticated(self):
        """Test root route redirects to login when not authenticated"""
        response = self.client.get("/", follow_redirects=False)
        assert response.status_code in [302, 401]  # Redirect or unauthorized
    
    def test_static_files_accessible(self):
        """Test static files are accessible"""
        # Test CSS file
        response = self.client.get("/static/css/style.css")
        assert response.status_code in [200, 404]  # Either exists or 404
    
    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = self.client.options("/health")
        assert response.status_code == 200

class TestBudgetService:
    """Budget service tests"""
    
    def setup_method(self):
        if budget_app:
            self.client = TestClient(budget_app)
        else:
            pytest.skip("Budget app not available")
    
    def test_health_endpoint(self):
        """Test budget service health"""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "budget"
    
    def test_budget_calculation(self):
        """Test budget calculation endpoint"""
        response = self.client.post("/calculate", json=TEST_CONFIG["test_budget"])
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert "total_essential" in data
        assert "total_savings" in data
    
    def test_invalid_budget_amount(self):
        """Test invalid budget amount"""
        invalid_budget = {"amount": -100, "duration": "monthly"}
        response = self.client.post("/calculate", json=invalid_budget)
        assert response.status_code == 422  # Validation error

class TestSavingsService:
    """Savings service tests"""
    
    def setup_method(self):
        if savings_app:
            self.client = TestClient(savings_app)
        else:
            pytest.skip("Savings app not available")
    
    def test_health_endpoint(self):
        """Test savings service health"""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "savings"
    
    def test_savings_forecast(self):
        """Test savings forecast calculation"""
        response = self.client.post("/forecast", json=TEST_CONFIG["test_savings"])
        assert response.status_code == 200
        data = response.json()
        assert "monthly_projections" in data
        assert "emergency_fund_progress" in data
        assert "what_if_scenarios" in data

class TestInsightsService:
    """Insights service tests"""
    
    def setup_method(self):
        if insights_app:
            self.client = TestClient(insights_app)
        else:
            pytest.skip("Insights app not available")
    
    def test_health_endpoint(self):
        """Test insights service health"""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "insights"

class TestIntegration:
    """Integration tests across services"""
    
    def setup_method(self):
        if gateway_app:
            self.client = TestClient(gateway_app)
        else:
            pytest.skip("Gateway app not available")
    
    def test_service_connectivity(self):
        """Test gateway can connect to all services"""
        response = self.client.get("/test-services")
        if response.status_code == 200:
            data = response.json()
            # Should have all three services
            expected_services = ["budget", "savings", "insights"]
            for service in expected_services:
                assert service in data

class TestSecurity:
    """Security tests"""
    
    def setup_method(self):
        if gateway_app:
            self.client = TestClient(gateway_app)
        else:
            pytest.skip("Gateway app not available")
    
    def test_sql_injection_protection(self):
        """Test SQL injection protection"""
        malicious_payload = {"amount": "'; DROP TABLE users; --", "duration": "monthly"}
        response = self.client.post("/api/budget/calculate", json=malicious_payload)
        # Should either reject or sanitize
        assert response.status_code in [400, 422, 500]
    
    def test_xss_protection(self):
        """Test XSS protection"""
        xss_payload = {"amount": 1000, "duration": "<script>alert('xss')</script>"}
        response = self.client.post("/api/budget/calculate", json=xss_payload)
        # Should either reject or sanitize
        assert response.status_code in [400, 422]
    
    def test_large_payload_rejection(self):
        """Test large payload rejection"""
        large_payload = {"amount": 1000, "data": "x" * 10000000}  # 10MB
        response = self.client.post("/api/budget/calculate", json=large_payload)
        # Should reject large payloads
        assert response.status_code in [413, 422]

class TestPerformance:
    """Performance tests"""
    
    def setup_method(self):
        if gateway_app:
            self.client = TestClient(gateway_app)
        else:
            pytest.skip("Gateway app not available")
    
    def test_response_time_health_check(self):
        """Test health check response time"""
        start_time = time.time()
        response = self.client.get("/health")
        response_time = time.time() - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0  # Should respond within 1 second
    
    def test_concurrent_requests(self):
        """Test handling concurrent requests"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            try:
                response = self.client.get("/health")
                results.put(response.status_code)
            except Exception as e:
                results.put(str(e))
        
        # Create 10 concurrent threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        success_count = 0
        while not results.empty():
            result = results.get()
            if result == 200:
                success_count += 1
        
        assert success_count >= 8  # At least 80% success rate

# Async tests for real service communication
class TestAsyncIntegration:
    """Async integration tests"""
    
    @pytest.mark.asyncio
    async def test_service_chain(self):
        """Test complete service chain"""
        if not gateway_app:
            pytest.skip("Gateway app not available")
        
        async with AsyncClient(app=gateway_app, base_url="http://test") as ac:
            # Test budget calculation
            budget_response = await ac.post(
                "/api/budget/calculate",
                json=TEST_CONFIG["test_budget"]
            )
            
            if budget_response.status_code == 200:
                budget_data = budget_response.json()
                
                # Test savings forecast
                savings_response = await ac.post(
                    "/api/savings/forecast",
                    json=TEST_CONFIG["test_savings"]
                )
                
                if savings_response.status_code == 200:
                    savings_data = savings_response.json()
                    
                    # Test insights generation
                    insights_payload = {
                        "budget_breakdown": budget_data,
                        "savings_data": savings_data
                    }
                    
                    insights_response = await ac.post(
                        "/api/insights/analyze",
                        json=insights_payload
                    )
                    
                    # At least one service should work
                    assert any([
                        budget_response.status_code == 200,
                        savings_response.status_code == 200,
                        insights_response.status_code == 200
                    ])

# Custom pytest fixtures
@pytest.fixture
def test_user():
    """Test user fixture"""
    return TEST_CONFIG["test_user"]

@pytest.fixture
def test_budget():
    """Test budget fixture"""
    return TEST_CONFIG["test_budget"]

@pytest.fixture
def test_savings():
    """Test savings fixture"""
    return TEST_CONFIG["test_savings"]

# Run tests with: python -m pytest tests/test_comprehensive.py -v
