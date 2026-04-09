"""
Iteration 12: Testing NEW features - Stats, Mood, Public Org Pages, Push, Telegram Admin
Features tested:
- GET /api/stats/public - Public statistics
- GET /api/stats/mood - Global mood aggregation
- GET /api/stats/mood/{council_id} - Per-council mood stats
- POST /api/mood - Set user mood (requires auth)
- GET /api/mood - Get user's moods (requires auth)
- GET /api/org/{org_id}/public - Public org page with reviews
- GET /api/push/vapid-key - VAPID public key
- POST /api/push/subscribe - Save push subscription (requires auth)
- GET /api/admin/telegram/config - Telegram config (requires admin)
- POST /api/admin/telegram/staff - Add telegram staff (requires admin)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
USER1_TOKEN = "Bearer WRANhsgZEBRoK2GSyIUvBEaqIWo0YtmhTsICy2Y4cPc"
USER2_TOKEN = "Bearer qaiAgO3W1YY2ZRN-5c2wk2BrNaGBNVE_rfYAxlye9cI"
ORG_ID = "org_seed_001"
COUNCIL_ID = "council_766c80223222"


class TestPublicStats:
    """Public statistics endpoint tests - no auth required"""
    
    def test_public_stats_returns_200(self):
        """GET /api/stats/public returns 200"""
        response = requests.get(f"{BASE_URL}/api/stats/public")
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields
        assert "total_users" in data
        assert "total_reviews" in data
        assert "total_orgs" in data
        assert "total_councils" in data
        assert "council_by_level" in data
        assert "top_orgs" in data
        assert "problems_on_map" in data
        print(f"✓ Public stats: {data['total_users']} users, {data['total_reviews']} reviews, {data['total_orgs']} orgs")
    
    def test_public_stats_council_by_level(self):
        """GET /api/stats/public returns council counts by level"""
        response = requests.get(f"{BASE_URL}/api/stats/public")
        assert response.status_code == 200
        data = response.json()
        
        council_by_level = data.get("council_by_level", {})
        expected_levels = ["yard", "district", "city", "republic", "country"]
        for level in expected_levels:
            assert level in council_by_level, f"Missing level: {level}"
        print(f"✓ Council by level: {council_by_level}")
    
    def test_public_stats_top_orgs(self):
        """GET /api/stats/public returns top organizations"""
        response = requests.get(f"{BASE_URL}/api/stats/public")
        assert response.status_code == 200
        data = response.json()
        
        top_orgs = data.get("top_orgs", [])
        if len(top_orgs) > 0:
            org = top_orgs[0]
            assert "org_id" in org
            assert "name" in org
            assert "average_rating" in org
            print(f"✓ Top org: {org['name']} with rating {org['average_rating']}")


class TestMoodSystem:
    """Mood system endpoint tests"""
    
    def test_global_mood_stats_returns_200(self):
        """GET /api/stats/mood returns global mood aggregation"""
        response = requests.get(f"{BASE_URL}/api/stats/mood")
        assert response.status_code == 200
        data = response.json()
        
        assert "mood_counts" in data
        assert "total_votes" in data
        assert "average_score" in data
        assert "dominant_mood" in data
        assert "mood_levels" in data
        print(f"✓ Global mood: {data['dominant_mood']} (score: {data['average_score']}, votes: {data['total_votes']})")
    
    def test_council_mood_stats_returns_200(self):
        """GET /api/stats/mood/{council_id} returns per-council mood"""
        response = requests.get(f"{BASE_URL}/api/stats/mood/{COUNCIL_ID}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["council_id"] == COUNCIL_ID
        assert "mood_counts" in data
        assert "average_score" in data
        assert "dominant_mood" in data
        print(f"✓ Council {COUNCIL_ID} mood: {data['dominant_mood']} (score: {data['average_score']})")
    
    def test_set_mood_requires_auth(self):
        """POST /api/mood requires authentication"""
        response = requests.post(f"{BASE_URL}/api/mood", json={"mood": "normal"})
        assert response.status_code == 401
        print("✓ POST /api/mood requires auth (401)")
    
    def test_set_mood_with_auth(self):
        """POST /api/mood sets user mood"""
        response = requests.post(
            f"{BASE_URL}/api/mood",
            headers={"Authorization": USER1_TOKEN},
            json={"mood": "excellent"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print("✓ Set mood to 'excellent' successfully")
    
    def test_set_mood_invalid_value(self):
        """POST /api/mood rejects invalid mood value"""
        response = requests.post(
            f"{BASE_URL}/api/mood",
            headers={"Authorization": USER1_TOKEN},
            json={"mood": "invalid_mood"}
        )
        assert response.status_code == 400
        print("✓ Invalid mood rejected (400)")
    
    def test_set_mood_for_council(self):
        """POST /api/mood sets mood for specific council"""
        response = requests.post(
            f"{BASE_URL}/api/mood",
            headers={"Authorization": USER1_TOKEN},
            json={"mood": "normal", "council_id": COUNCIL_ID}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"✓ Set mood for council {COUNCIL_ID} successfully")
    
    def test_get_my_moods_requires_auth(self):
        """GET /api/mood requires authentication"""
        response = requests.get(f"{BASE_URL}/api/mood")
        assert response.status_code == 401
        print("✓ GET /api/mood requires auth (401)")
    
    def test_get_my_moods_with_auth(self):
        """GET /api/mood returns user's moods"""
        response = requests.get(
            f"{BASE_URL}/api/mood",
            headers={"Authorization": USER1_TOKEN}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Got {len(data)} mood entries for user")


class TestPublicOrgPage:
    """Public organization page endpoint tests"""
    
    def test_public_org_page_returns_200(self):
        """GET /api/org/{org_id}/public returns org with reviews"""
        response = requests.get(f"{BASE_URL}/api/org/{ORG_ID}/public")
        assert response.status_code == 200
        data = response.json()
        
        assert data["org_id"] == ORG_ID
        assert "name" in data
        assert "reviews" in data
        assert "rating_distribution" in data
        print(f"✓ Public org page: {data['name']} with {len(data['reviews'])} reviews")
    
    def test_public_org_page_rating_distribution(self):
        """GET /api/org/{org_id}/public returns rating distribution"""
        response = requests.get(f"{BASE_URL}/api/org/{ORG_ID}/public")
        assert response.status_code == 200
        data = response.json()
        
        dist = data.get("rating_distribution", {})
        # Should have keys 1-5
        for rating in [1, 2, 3, 4, 5]:
            assert rating in dist or str(rating) in dist
        print(f"✓ Rating distribution: {dist}")
    
    def test_public_org_page_not_found(self):
        """GET /api/org/{org_id}/public returns 404 for non-existent org"""
        response = requests.get(f"{BASE_URL}/api/org/nonexistent_org/public")
        assert response.status_code == 404
        print("✓ Non-existent org returns 404")


class TestPushNotifications:
    """Push notification endpoint tests"""
    
    def test_vapid_key_returns_200(self):
        """GET /api/push/vapid-key returns VAPID public key"""
        response = requests.get(f"{BASE_URL}/api/push/vapid-key")
        assert response.status_code == 200
        data = response.json()
        
        assert "public_key" in data
        assert len(data["public_key"]) > 0
        print(f"✓ VAPID key: {data['public_key'][:20]}...")
    
    def test_push_subscribe_requires_auth(self):
        """POST /api/push/subscribe requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/push/subscribe",
            json={"subscription": {"endpoint": "https://test.com"}}
        )
        assert response.status_code == 401
        print("✓ POST /api/push/subscribe requires auth (401)")
    
    def test_push_subscribe_with_auth(self):
        """POST /api/push/subscribe saves subscription"""
        response = requests.post(
            f"{BASE_URL}/api/push/subscribe",
            headers={"Authorization": USER1_TOKEN},
            json={
                "subscription": {
                    "endpoint": "https://test.example.com/push/test123",
                    "keys": {"p256dh": "test_key", "auth": "test_auth"}
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print("✓ Push subscription saved successfully")
    
    def test_push_subscribe_missing_subscription(self):
        """POST /api/push/subscribe requires subscription data"""
        response = requests.post(
            f"{BASE_URL}/api/push/subscribe",
            headers={"Authorization": USER1_TOKEN},
            json={}
        )
        assert response.status_code == 400
        print("✓ Missing subscription rejected (400)")


class TestTelegramAdminPanel:
    """Telegram admin panel endpoint tests - MOCKED (tokens not configured)"""
    
    def test_telegram_config_requires_admin(self):
        """GET /api/admin/telegram/config requires admin role"""
        response = requests.get(
            f"{BASE_URL}/api/admin/telegram/config",
            headers={"Authorization": USER2_TOKEN}  # User2 is not admin
        )
        assert response.status_code == 403
        print("✓ GET /api/admin/telegram/config requires admin (403)")
    
    def test_telegram_config_with_admin(self):
        """GET /api/admin/telegram/config returns config for admin"""
        response = requests.get(
            f"{BASE_URL}/api/admin/telegram/config",
            headers={"Authorization": USER1_TOKEN}  # User1 is admin
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "user_bot_configured" in data
        assert "admin_bot_configured" in data
        assert "staff" in data
        assert "permissions_template" in data
        # Bots should NOT be configured (MOCKED)
        assert data["user_bot_configured"] == False
        assert data["admin_bot_configured"] == False
        print(f"✓ Telegram config: user_bot={data['user_bot_configured']}, admin_bot={data['admin_bot_configured']} (MOCKED)")
    
    def test_add_telegram_staff_requires_admin(self):
        """POST /api/admin/telegram/staff requires admin role"""
        response = requests.post(
            f"{BASE_URL}/api/admin/telegram/staff",
            headers={"Authorization": USER2_TOKEN},
            json={"telegram_user_id": "999", "name": "Test"}
        )
        assert response.status_code == 403
        print("✓ POST /api/admin/telegram/staff requires admin (403)")
    
    def test_add_telegram_staff_with_admin(self):
        """POST /api/admin/telegram/staff adds staff member"""
        response = requests.post(
            f"{BASE_URL}/api/admin/telegram/staff",
            headers={"Authorization": USER1_TOKEN},
            json={
                "telegram_user_id": "987654321",
                "name": "Test Staff Member",
                "permissions": ["view_stats", "manage_reviews"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "staff_id" in data
        print(f"✓ Added telegram staff: {data['staff_id']}")
    
    def test_add_telegram_staff_missing_user_id(self):
        """POST /api/admin/telegram/staff requires telegram_user_id"""
        response = requests.post(
            f"{BASE_URL}/api/admin/telegram/staff",
            headers={"Authorization": USER1_TOKEN},
            json={"name": "Test"}
        )
        assert response.status_code == 400
        print("✓ Missing telegram_user_id rejected (400)")


class TestMoodLevels:
    """Test all mood levels are valid"""
    
    @pytest.mark.parametrize("mood", ["excellent", "normal", "mild_upset", "dissatisfaction", "stress", "anger"])
    def test_all_mood_levels_valid(self, mood):
        """All mood levels can be set"""
        response = requests.post(
            f"{BASE_URL}/api/mood",
            headers={"Authorization": USER1_TOKEN},
            json={"mood": mood}
        )
        assert response.status_code == 200
        print(f"✓ Mood '{mood}' set successfully")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
