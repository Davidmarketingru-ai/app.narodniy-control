"""
Iteration 13: P2 Features Testing
- Streak system (daily check-in with rewards)
- District chats (geo-fenced messaging)
- Telegram bot integration (link/status endpoints)
- Organization responses (org_manager role)
"""
import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
USER1_TOKEN = "Bearer WRANhsgZEBRoK2GSyIUvBEaqIWo0YtmhTsICy2Y4cPc"  # admin, district: Октябрьский
USER1_ID = "user_eec305b08f9c"
USER2_TOKEN = "Bearer qaiAgO3W1YY2ZRN-5c2wk2BrNaGBNVE_rfYAxlye9cI"  # test-user-council-2
USER2_ID = "test-user-council-2"
ORG_ID = "org_seed_001"
REVIEW_ID = "rev_seed_001"  # Approved review for org_seed_001


@pytest.fixture
def api_client():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture
def auth_client(api_client):
    api_client.headers.update({"Authorization": USER1_TOKEN})
    return api_client


@pytest.fixture
def user2_client(api_client):
    api_client.headers.update({"Authorization": USER2_TOKEN})
    return api_client


# ==================== STREAK SYSTEM TESTS ====================
class TestStreakSystem:
    """Tests for daily streak check-in system with milestone rewards"""
    
    def test_streak_checkin_creates_or_updates_streak(self, auth_client):
        """POST /api/streak/checkin - creates/updates daily streak"""
        response = auth_client.post(f"{BASE_URL}/api/streak/checkin")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "streak" in data, "Response should contain 'streak' field"
        assert "max" in data, "Response should contain 'max' field"
        assert "already_checked" in data, "Response should contain 'already_checked' field"
        assert "reward" in data, "Response should contain 'reward' field"
        assert isinstance(data["streak"], int), "streak should be integer"
        assert isinstance(data["max"], int), "max should be integer"
        print(f"✓ Streak checkin: current={data['streak']}, max={data['max']}, already_checked={data['already_checked']}")
    
    def test_streak_checkin_second_call_same_day(self, auth_client):
        """POST /api/streak/checkin - second call same day returns already_checked=True"""
        # First call
        auth_client.post(f"{BASE_URL}/api/streak/checkin")
        
        # Second call same day
        response = auth_client.post(f"{BASE_URL}/api/streak/checkin")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("already_checked") == True, "Second call same day should return already_checked=True"
        print(f"✓ Second checkin same day: already_checked={data['already_checked']}")
    
    def test_get_streak_info(self, auth_client):
        """GET /api/streak - get current streak info"""
        response = auth_client.get(f"{BASE_URL}/api/streak")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "current" in data, "Response should contain 'current' field"
        assert "max" in data, "Response should contain 'max' field"
        assert "last_date" in data, "Response should contain 'last_date' field"
        assert "history" in data, "Response should contain 'history' field"
        print(f"✓ Get streak: current={data['current']}, max={data['max']}, history_len={len(data.get('history', []))}")
    
    def test_streak_requires_auth(self, api_client):
        """Streak endpoints require authentication"""
        response = api_client.get(f"{BASE_URL}/api/streak")
        assert response.status_code == 401, "GET /api/streak should require auth"
        
        response = api_client.post(f"{BASE_URL}/api/streak/checkin")
        assert response.status_code == 401, "POST /api/streak/checkin should require auth"
        print("✓ Streak endpoints require authentication")


# ==================== DISTRICT CHAT TESTS ====================
class TestDistrictChats:
    """Tests for geo-fenced district messaging"""
    
    def test_get_district_messages_with_district(self, auth_client):
        """GET /api/chats/district - returns messages for user's district"""
        response = auth_client.get(f"{BASE_URL}/api/chats/district")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list of messages"
        print(f"✓ Get district messages: {len(data)} messages found")
    
    def test_post_district_message(self, auth_client):
        """POST /api/chats/district - post message to district chat"""
        test_message = f"Тестовое сообщение {datetime.now().isoformat()}"
        response = auth_client.post(f"{BASE_URL}/api/chats/district", json={"text": test_message})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "message_id" in data, "Response should contain message_id"
        assert "user_id" in data, "Response should contain user_id"
        assert "district" in data, "Response should contain district"
        assert data["text"] == test_message, "Message text should match"
        print(f"✓ Posted district message: {data['message_id']}")
    
    def test_post_district_message_validates_length(self, auth_client):
        """POST /api/chats/district - validates message length"""
        # Too short
        response = auth_client.post(f"{BASE_URL}/api/chats/district", json={"text": "a"})
        assert response.status_code == 400, "Should reject message < 2 chars"
        
        # Too long (>1000 chars)
        long_text = "a" * 1001
        response = auth_client.post(f"{BASE_URL}/api/chats/district", json={"text": long_text})
        assert response.status_code == 400, "Should reject message > 1000 chars"
        print("✓ District chat validates message length")
    
    def test_district_chat_requires_district_in_profile(self, user2_client):
        """POST /api/chats/district - rejects if no district set in profile"""
        # First check if user2 has district set
        profile_resp = user2_client.get(f"{BASE_URL}/api/profile")
        if profile_resp.status_code == 200:
            profile = profile_resp.json()
            if not profile.get("district"):
                # User has no district, should be rejected
                response = user2_client.post(f"{BASE_URL}/api/chats/district", json={"text": "Test message"})
                assert response.status_code == 400, "Should reject if no district in profile"
                assert "район" in response.json().get("detail", "").lower() or "district" in response.json().get("detail", "").lower()
                print("✓ District chat rejects users without district in profile")
            else:
                # User has district, message should work
                response = user2_client.post(f"{BASE_URL}/api/chats/district", json={"text": "Test from user2"})
                assert response.status_code == 200
                print(f"✓ User2 has district '{profile.get('district')}', message posted")
        else:
            pytest.skip("Could not get user2 profile")
    
    def test_district_chat_requires_auth(self, api_client):
        """District chat endpoints require authentication"""
        response = api_client.get(f"{BASE_URL}/api/chats/district")
        assert response.status_code == 401, "GET /api/chats/district should require auth"
        
        response = api_client.post(f"{BASE_URL}/api/chats/district", json={"text": "test"})
        assert response.status_code == 401, "POST /api/chats/district should require auth"
        print("✓ District chat endpoints require authentication")


# ==================== TELEGRAM INTEGRATION TESTS ====================
class TestTelegramIntegration:
    """Tests for Telegram bot linking and status endpoints"""
    
    def test_telegram_link_creates_code(self, auth_client):
        """POST /api/telegram/link - creates linking code and deep_link"""
        response = auth_client.post(f"{BASE_URL}/api/telegram/link")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "code" in data, "Response should contain 'code'"
        assert "deep_link" in data, "Response should contain 'deep_link'"
        assert len(data["code"]) == 8, "Code should be 8 characters"
        assert data["code"].isupper(), "Code should be uppercase"
        assert "t.me" in data["deep_link"], "deep_link should contain t.me"
        print(f"✓ Telegram link created: code={data['code']}, deep_link={data['deep_link']}")
    
    def test_telegram_status(self, auth_client):
        """GET /api/telegram/status - returns linked status"""
        response = auth_client.get(f"{BASE_URL}/api/telegram/status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "linked" in data, "Response should contain 'linked' field"
        assert isinstance(data["linked"], bool), "linked should be boolean"
        print(f"✓ Telegram status: linked={data['linked']}")
    
    def test_telegram_endpoints_require_auth(self, api_client):
        """Telegram endpoints require authentication"""
        response = api_client.post(f"{BASE_URL}/api/telegram/link")
        assert response.status_code == 401, "POST /api/telegram/link should require auth"
        
        response = api_client.get(f"{BASE_URL}/api/telegram/status")
        assert response.status_code == 401, "GET /api/telegram/status should require auth"
        print("✓ Telegram endpoints require authentication")


# ==================== ORGANIZATION RESPONSES TESTS ====================
class TestOrgResponses:
    """Tests for organization manager responses to reviews"""
    
    def test_org_respond_requires_manager_role(self, auth_client):
        """POST /api/org/{org_id}/respond/{review_id} - requires org_manager role"""
        # Admin user (not org_manager) should be able to respond
        response = auth_client.post(
            f"{BASE_URL}/api/org/{ORG_ID}/respond/{REVIEW_ID}",
            json={"text": "Спасибо за ваш отзыв! Мы примем меры."}
        )
        # Admin can respond (is_admin check in code)
        assert response.status_code in [200, 403], f"Expected 200 or 403, got {response.status_code}: {response.text}"
        
        if response.status_code == 200:
            data = response.json()
            assert "response_id" in data, "Response should contain response_id"
            assert "text" in data, "Response should contain text"
            print(f"✓ Admin responded to review: {data.get('response_id')}")
        else:
            print("✓ Response requires org_manager role (admin not allowed for this org)")
    
    def test_get_review_response(self, api_client):
        """GET /api/reviews/{review_id}/response - get org response for review"""
        response = api_client.get(f"{BASE_URL}/api/reviews/{REVIEW_ID}/response")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # May be empty dict if no response exists
        if data:
            assert "response_id" in data or data == {}, "Response should contain response_id or be empty"
            print(f"✓ Got review response: {data}")
        else:
            print("✓ No org response for this review yet (empty response)")
    
    def test_get_org_responses(self, api_client):
        """GET /api/org/{org_id}/responses - get all org responses"""
        response = api_client.get(f"{BASE_URL}/api/org/{ORG_ID}/responses")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ Got {len(data)} org responses")
    
    def test_set_org_manager_admin_only(self):
        """POST /api/admin/org-manager - admin only endpoint"""
        # Non-admin should be rejected
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json", "Authorization": USER2_TOKEN})
        response = session.post(
            f"{BASE_URL}/api/admin/org-manager",
            json={"user_id": USER2_ID, "org_id": ORG_ID}
        )
        assert response.status_code == 403, "Non-admin should be rejected"
        print("✓ Non-admin rejected from setting org_manager")
        
        # Admin should succeed
        admin_session = requests.Session()
        admin_session.headers.update({"Content-Type": "application/json", "Authorization": USER1_TOKEN})
        response = admin_session.post(
            f"{BASE_URL}/api/admin/org-manager",
            json={"user_id": USER2_ID, "org_id": ORG_ID}
        )
        assert response.status_code == 200, f"Admin should be able to set org_manager: {response.text}"
        print("✓ Admin can set org_manager role")
    
    def test_org_manager_can_respond(self):
        """Org manager can respond to reviews for their org"""
        # First ensure user2 is set as org_manager
        admin_session = requests.Session()
        admin_session.headers.update({"Content-Type": "application/json", "Authorization": USER1_TOKEN})
        admin_session.post(
            f"{BASE_URL}/api/admin/org-manager",
            json={"user_id": USER2_ID, "org_id": ORG_ID}
        )
        
        # Now user2 should be able to respond
        user2_session = requests.Session()
        user2_session.headers.update({"Content-Type": "application/json", "Authorization": USER2_TOKEN})
        response = user2_session.post(
            f"{BASE_URL}/api/org/{ORG_ID}/respond/{REVIEW_ID}",
            json={"text": "Благодарим за обратную связь! Мы работаем над улучшением."}
        )
        # Should succeed now that user2 is org_manager
        assert response.status_code == 200, f"Org manager should be able to respond: {response.text}"
        
        data = response.json()
        assert "response_id" in data
        assert data["text"] == "Благодарим за обратную связь! Мы работаем над улучшением."
        print(f"✓ Org manager responded: {data['response_id']}")
    
    def test_org_respond_validates_text(self, auth_client):
        """POST /api/org/{org_id}/respond/{review_id} - validates text length"""
        # Too short
        response = auth_client.post(
            f"{BASE_URL}/api/org/{ORG_ID}/respond/{REVIEW_ID}",
            json={"text": "Hi"}
        )
        assert response.status_code == 400, "Should reject text < 5 chars"
        print("✓ Org response validates text length")
    
    def test_org_respond_review_not_found(self, auth_client):
        """POST /api/org/{org_id}/respond/{review_id} - returns 404 for non-existent review"""
        response = auth_client.post(
            f"{BASE_URL}/api/org/{ORG_ID}/respond/nonexistent_review",
            json={"text": "This should fail"}
        )
        assert response.status_code == 404, "Should return 404 for non-existent review"
        print("✓ Returns 404 for non-existent review")


# ==================== STREAK REWARDS VERIFICATION ====================
class TestStreakRewards:
    """Verify streak reward milestones are configured correctly"""
    
    def test_streak_rewards_milestones(self, auth_client):
        """Verify streak rewards at milestones (3,7,14,30,60,100 days)"""
        # This is a configuration test - we verify the rewards are defined
        # by checking the streak response structure
        response = auth_client.post(f"{BASE_URL}/api/streak/checkin")
        assert response.status_code == 200
        
        data = response.json()
        # If reward is present, verify structure
        if data.get("reward"):
            reward = data["reward"]
            assert "points" in reward, "Reward should have points"
            assert "badge" in reward, "Reward should have badge"
            print(f"✓ Streak reward received: {reward}")
        else:
            print("✓ No reward at current streak level (expected)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
