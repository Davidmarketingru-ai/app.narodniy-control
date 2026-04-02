"""
Test suite for Iteration 7 - Quick-Win Improvements
Tests: Onboarding, Verify Feed, Daily Missions, Adaptive Timer, Public Review, Social Sharing
"""
import pytest
import requests
import os
from datetime import datetime, timezone, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test session from previous iteration
TEST_SESSION_TOKEN = "test_session_comprehensive_1773178288724"
TEST_USER_ID = "test_user_comprehensive_1773178288724"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def auth_headers():
    """Auth headers using test session token"""
    return {"Authorization": f"Bearer {TEST_SESSION_TOKEN}"}


class TestOnboardingEndpoints:
    """Test onboarding status and completion endpoints"""
    
    def test_onboarding_status_requires_auth(self, api_client):
        """GET /api/onboarding/status requires authentication"""
        response = api_client.get(f"{BASE_URL}/api/onboarding/status")
        assert response.status_code == 401
        print("✓ GET /api/onboarding/status requires auth (401)")
    
    def test_onboarding_status_authenticated(self, api_client, auth_headers):
        """GET /api/onboarding/status returns completed/step for authenticated user"""
        response = api_client.get(f"{BASE_URL}/api/onboarding/status", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "completed" in data
        assert "step" in data
        assert isinstance(data["completed"], bool)
        assert isinstance(data["step"], int)
        print(f"✓ GET /api/onboarding/status returns: completed={data['completed']}, step={data['step']}")
    
    def test_onboarding_complete_requires_auth(self, api_client):
        """POST /api/onboarding/complete requires authentication"""
        response = api_client.post(f"{BASE_URL}/api/onboarding/complete", json={"step": 1})
        assert response.status_code == 401
        print("✓ POST /api/onboarding/complete requires auth (401)")
    
    def test_onboarding_complete_step(self, api_client, auth_headers):
        """POST /api/onboarding/complete updates step"""
        response = api_client.post(
            f"{BASE_URL}/api/onboarding/complete",
            headers=auth_headers,
            json={"step": 2}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print("✓ POST /api/onboarding/complete updates step successfully")


class TestVerifyFeedEndpoints:
    """Test verification feed endpoints"""
    
    def test_pending_verification_requires_auth(self, api_client):
        """GET /api/reviews/pending-verification requires authentication"""
        response = api_client.get(f"{BASE_URL}/api/reviews/pending-verification")
        assert response.status_code == 401
        print("✓ GET /api/reviews/pending-verification requires auth (401)")
    
    def test_pending_verification_authenticated(self, api_client, auth_headers):
        """GET /api/reviews/pending-verification returns pending reviews NOT authored by current user"""
        response = api_client.get(f"{BASE_URL}/api/reviews/pending-verification", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Verify none of the reviews are authored by the current user
        for review in data:
            assert review.get("user_id") != TEST_USER_ID, "Should not return user's own reviews"
            assert review.get("status") == "pending", "Should only return pending reviews"
        print(f"✓ GET /api/reviews/pending-verification returns {len(data)} pending reviews (excluding user's own)")
    
    def test_pending_verification_not_caught_by_review_id_route(self, api_client, auth_headers):
        """Verify /api/reviews/pending-verification is NOT caught by /reviews/{review_id} route"""
        # This should return 200 with a list, not 404 (which would happen if caught by {review_id})
        response = api_client.get(f"{BASE_URL}/api/reviews/pending-verification", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        print("✓ /api/reviews/pending-verification is correctly routed (not caught by {review_id})")


class TestDailyMissionsEndpoints:
    """Test daily missions and streak endpoints"""
    
    def test_daily_missions_requires_auth(self, api_client):
        """GET /api/missions/daily requires authentication"""
        response = api_client.get(f"{BASE_URL}/api/missions/daily")
        assert response.status_code == 401
        print("✓ GET /api/missions/daily requires auth (401)")
    
    def test_daily_missions_authenticated(self, api_client, auth_headers):
        """GET /api/missions/daily returns missions array and streak count"""
        response = api_client.get(f"{BASE_URL}/api/missions/daily", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "missions" in data
        assert "streak" in data
        assert "date" in data
        assert isinstance(data["missions"], list)
        assert isinstance(data["streak"], int)
        # Verify mission structure
        if data["missions"]:
            mission = data["missions"][0]
            assert "mission_id" in mission
            assert "type" in mission
            assert "title" in mission
            assert "target" in mission
            assert "progress" in mission
            assert "reward" in mission
            assert "claimed" in mission
        print(f"✓ GET /api/missions/daily returns {len(data['missions'])} missions, streak={data['streak']}")
    
    def test_mission_progress_requires_auth(self, api_client):
        """POST /api/missions/{mission_id}/progress requires authentication"""
        response = api_client.post(f"{BASE_URL}/api/missions/test_mission/progress", json={"increment": 1})
        assert response.status_code == 401
        print("✓ POST /api/missions/{id}/progress requires auth (401)")
    
    def test_mission_progress_update(self, api_client, auth_headers):
        """POST /api/missions/{mission_id}/progress increments progress"""
        # First get missions to get a valid mission_id
        missions_resp = api_client.get(f"{BASE_URL}/api/missions/daily", headers=auth_headers)
        missions = missions_resp.json().get("missions", [])
        if missions:
            mission_id = missions[0]["mission_id"]
            response = api_client.post(
                f"{BASE_URL}/api/missions/{mission_id}/progress",
                headers=auth_headers,
                json={"increment": 1}
            )
            assert response.status_code == 200
            data = response.json()
            assert "progress" in data
            assert "target" in data
            assert "completed" in data
            print(f"✓ POST /api/missions/{mission_id}/progress updates progress: {data['progress']}/{data['target']}")
        else:
            print("⚠ No missions available to test progress update")
    
    def test_mission_claim_requires_auth(self, api_client):
        """POST /api/missions/{mission_id}/claim requires authentication"""
        response = api_client.post(f"{BASE_URL}/api/missions/test_mission/claim")
        assert response.status_code == 401
        print("✓ POST /api/missions/{id}/claim requires auth (401)")
    
    def test_mission_claim_not_found(self, api_client, auth_headers):
        """POST /api/missions/{mission_id}/claim returns 404 for invalid mission"""
        response = api_client.post(
            f"{BASE_URL}/api/missions/invalid_mission_id/claim",
            headers=auth_headers
        )
        assert response.status_code == 404
        print("✓ POST /api/missions/invalid_id/claim returns 404")


class TestPublicReviewEndpoint:
    """Test public review endpoint for sharing"""
    
    def test_public_review_no_auth_required(self, api_client):
        """GET /api/reviews/{review_id}/public does not require auth"""
        # First get an approved review
        reviews_resp = api_client.get(f"{BASE_URL}/api/reviews?status=approved")
        reviews = reviews_resp.json()
        if reviews:
            review_id = reviews[0]["review_id"]
            response = api_client.get(f"{BASE_URL}/api/reviews/{review_id}/public")
            assert response.status_code == 200
            data = response.json()
            assert data["review_id"] == review_id
            assert data["status"] == "approved"
            print(f"✓ GET /api/reviews/{review_id}/public returns approved review without auth")
        else:
            print("⚠ No approved reviews available to test public endpoint")
    
    def test_public_review_not_found_for_pending(self, api_client):
        """GET /api/reviews/{review_id}/public returns 404 for non-approved reviews"""
        # Get a pending review
        reviews_resp = api_client.get(f"{BASE_URL}/api/reviews?status=pending")
        reviews = reviews_resp.json()
        if reviews:
            review_id = reviews[0]["review_id"]
            response = api_client.get(f"{BASE_URL}/api/reviews/{review_id}/public")
            assert response.status_code == 404
            print(f"✓ GET /api/reviews/{review_id}/public returns 404 for pending review")
        else:
            print("⚠ No pending reviews available to test")


class TestAdaptiveTimer:
    """Test adaptive verification timer based on user count"""
    
    def test_review_creation_has_expires_at(self, api_client, auth_headers):
        """Review creation includes expires_at field with adaptive timer"""
        # Get organizations first
        orgs_resp = api_client.get(f"{BASE_URL}/api/organizations")
        orgs = orgs_resp.json()
        if orgs:
            org_id = orgs[0]["org_id"]
            # Create a test review
            response = api_client.post(
                f"{BASE_URL}/api/reviews",
                headers=auth_headers,
                json={
                    "org_id": org_id,
                    "title": "TEST_Adaptive Timer Test Review",
                    "content": "Testing adaptive timer functionality",
                    "rating": 3
                }
            )
            assert response.status_code == 201
            data = response.json()
            assert "expires_at" in data
            assert "created_at" in data
            # Verify expires_at is in the future
            expires_at = datetime.fromisoformat(data["expires_at"].replace("Z", "+00:00"))
            created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
            diff_hours = (expires_at - created_at).total_seconds() / 3600
            # Should be 12, 24, 48, or 72 hours based on user count
            assert diff_hours in [12, 24, 48, 72], f"Expected 12/24/48/72h, got {diff_hours}h"
            print(f"✓ Review created with adaptive timer: expires in {diff_hours}h")
        else:
            print("⚠ No organizations available to test review creation")


class TestExistingEndpointsRegression:
    """Regression tests for existing endpoints"""
    
    def test_news_endpoint(self, api_client):
        """GET /api/news still works"""
        response = api_client.get(f"{BASE_URL}/api/news")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        print("✓ GET /api/news works (regression)")
    
    def test_weather_widget(self, api_client):
        """GET /api/widgets/weather still works"""
        response = api_client.get(f"{BASE_URL}/api/widgets/weather")
        assert response.status_code == 200
        print("✓ GET /api/widgets/weather works (regression)")
    
    def test_currency_widget(self, api_client):
        """GET /api/widgets/currency still works"""
        response = api_client.get(f"{BASE_URL}/api/widgets/currency")
        assert response.status_code == 200
        print("✓ GET /api/widgets/currency works (regression)")
    
    def test_support_faq(self, api_client):
        """GET /api/support/faq still works"""
        response = api_client.get(f"{BASE_URL}/api/support/faq")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        print("✓ GET /api/support/faq works (regression)")
    
    def test_legal_info(self, api_client):
        """GET /api/legal/info still works"""
        response = api_client.get(f"{BASE_URL}/api/legal/info")
        assert response.status_code == 200
        data = response.json()
        assert "operator_name" in data
        assert "inn" in data
        print("✓ GET /api/legal/info works (regression)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
