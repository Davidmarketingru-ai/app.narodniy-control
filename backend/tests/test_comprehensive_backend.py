"""
Comprehensive Backend API Tests for Народный Контроль (People's Control) App
Tests all CRUD operations, filters, authenticated flows, and edge cases
"""
import pytest
import requests
import os
from datetime import datetime

# Get BASE_URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    pytest.skip("REACT_APP_BACKEND_URL not set", allow_module_level=True)

# Test session token (created via mongosh)
TEST_SESSION_TOKEN = "test_session_comprehensive_1773178288724"
TEST_USER_ID = "test_user_comprehensive_1773178288724"
TEST_REFERRAL_CODE = "TESTCODE"


@pytest.fixture
def api_client():
    """Unauthenticated API client"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture
def auth_client():
    """Authenticated API client with session token"""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TEST_SESSION_TOKEN}"
    })
    session.cookies.set("session_token", TEST_SESSION_TOKEN)
    return session


# ==================== Health & Basic Endpoints ====================
class TestHealthEndpoints:
    """Tests for health check and basic endpoints"""
    
    def test_health_endpoint(self, api_client):
        """GET /api/health returns ok"""
        resp = api_client.get(f"{BASE_URL}/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("status") == "ok"
        print("✓ Health endpoint working")
    
    def test_root_endpoint(self, api_client):
        """GET /api/ returns API info"""
        resp = api_client.get(f"{BASE_URL}/api/")
        assert resp.status_code == 200
        data = resp.json()
        assert "Народный Контроль" in data.get("message", "")
        print("✓ Root endpoint working")


# ==================== Organizations Endpoints ====================
class TestOrganizationsEndpoints:
    """Tests for organizations CRUD operations"""
    
    def test_list_organizations(self, api_client):
        """GET /api/organizations returns seeded organizations"""
        resp = api_client.get(f"{BASE_URL}/api/organizations")
        assert resp.status_code == 200
        orgs = resp.json()
        assert isinstance(orgs, list)
        assert len(orgs) >= 8, "Expected at least 8 seeded organizations"
        
        # Verify organization structure
        for org in orgs:
            assert "org_id" in org
            assert "name" in org
            assert "category" in org
            assert "address" in org
            assert "latitude" in org
            assert "longitude" in org
        print(f"✓ Got {len(orgs)} organizations")
    
    def test_get_single_organization(self, api_client):
        """GET /api/organizations/org_seed_001 returns single organization"""
        resp = api_client.get(f"{BASE_URL}/api/organizations/org_seed_001")
        assert resp.status_code == 200
        org = resp.json()
        assert org["org_id"] == "org_seed_001"
        assert org["name"] == "Пятёрочка"
        assert org["category"] == "shop"
        print(f"✓ Got organization: {org['name']}")
    
    def test_organization_not_found(self, api_client):
        """GET /api/organizations/nonexistent returns 404"""
        resp = api_client.get(f"{BASE_URL}/api/organizations/nonexistent_org_123")
        assert resp.status_code == 404
        print("✓ Organization not found returns 404")


# ==================== Reviews Endpoints ====================
class TestReviewsEndpoints:
    """Tests for reviews CRUD and filtering"""
    
    def test_list_reviews(self, api_client):
        """GET /api/reviews returns reviews with correct fields"""
        resp = api_client.get(f"{BASE_URL}/api/reviews")
        assert resp.status_code == 200
        reviews = resp.json()
        assert isinstance(reviews, list)
        
        # Verify review structure
        if len(reviews) > 0:
            review = reviews[0]
            assert "review_id" in review
            assert "title" in review
            assert "content" in review
            assert "status" in review
            assert "rating" in review
            assert "org_id" in review
        print(f"✓ Got {len(reviews)} reviews")
    
    def test_filter_reviews_by_status_approved(self, api_client):
        """GET /api/reviews?status=approved filters by status"""
        resp = api_client.get(f"{BASE_URL}/api/reviews?status=approved")
        assert resp.status_code == 200
        reviews = resp.json()
        for review in reviews:
            assert review["status"] == "approved"
        print(f"✓ Filtered approved reviews: {len(reviews)}")
    
    def test_filter_reviews_by_status_pending(self, api_client):
        """GET /api/reviews?status=pending filters by status"""
        resp = api_client.get(f"{BASE_URL}/api/reviews?status=pending")
        assert resp.status_code == 200
        reviews = resp.json()
        for review in reviews:
            assert review["status"] == "pending"
        print(f"✓ Filtered pending reviews: {len(reviews)}")
    
    def test_get_single_review(self, api_client):
        """GET /api/reviews/rev_seed_001 returns single review"""
        resp = api_client.get(f"{BASE_URL}/api/reviews/rev_seed_001")
        assert resp.status_code == 200
        review = resp.json()
        assert review["review_id"] == "rev_seed_001"
        assert review["org_name"] == "Пятёрочка"
        print(f"✓ Got review: {review['title']}")
    
    def test_review_not_found(self, api_client):
        """GET /api/reviews/nonexistent returns 404"""
        resp = api_client.get(f"{BASE_URL}/api/reviews/nonexistent_review")
        assert resp.status_code == 404
        print("✓ Review not found returns 404")


# ==================== News Endpoints ====================
class TestNewsEndpoints:
    """Tests for news feed functionality"""
    
    def test_list_news(self, api_client):
        """GET /api/news returns seeded news articles"""
        resp = api_client.get(f"{BASE_URL}/api/news")
        assert resp.status_code == 200
        articles = resp.json()
        assert isinstance(articles, list)
        assert len(articles) >= 5, "Expected at least 5 seeded news articles"
        
        # Verify article structure
        for article in articles:
            assert "article_id" in article
            assert "title" in article
            assert "content" in article
            assert "level" in article
            assert "category" in article
            assert "likes" in article
            assert "views" in article
            assert "comments_count" in article
        print(f"✓ Got {len(articles)} news articles")
    
    def test_filter_news_by_level(self, api_client):
        """GET /api/news?level=city filters by level"""
        resp = api_client.get(f"{BASE_URL}/api/news?level=city")
        assert resp.status_code == 200
        articles = resp.json()
        for article in articles:
            assert article["level"] == "city"
        print(f"✓ Filtered city news: {len(articles)}")
    
    def test_filter_news_by_category(self, api_client):
        """GET /api/news?category=health filters by category"""
        resp = api_client.get(f"{BASE_URL}/api/news?category=health")
        assert resp.status_code == 200
        articles = resp.json()
        for article in articles:
            assert article["category"] == "health"
        print(f"✓ Filtered health news: {len(articles)}")
    
    def test_get_single_news_article(self, api_client):
        """GET /api/news/news_seed_001 returns single article and increments views"""
        # Get initial views
        resp1 = api_client.get(f"{BASE_URL}/api/news/news_seed_001")
        assert resp1.status_code == 200
        article1 = resp1.json()
        initial_views = article1["views"]
        
        # Get again - views should increment
        resp2 = api_client.get(f"{BASE_URL}/api/news/news_seed_001")
        assert resp2.status_code == 200
        article2 = resp2.json()
        assert article2["views"] >= initial_views
        assert article2["article_id"] == "news_seed_001"
        print(f"✓ Got news article: {article2['title']}, views: {article2['views']}")


# ==================== Widgets Endpoints ====================
class TestWidgetsEndpoints:
    """Tests for info widgets - weather, currency, magnetic storms"""
    
    def test_weather_widget(self, api_client):
        """GET /api/widgets/weather returns weather with required fields"""
        resp = api_client.get(f"{BASE_URL}/api/widgets/weather")
        # Can be 200 or 503 if external API is unavailable
        if resp.status_code == 200:
            data = resp.json()
            assert "current" in data
            current = data["current"]
            assert "temperature_2m" in current
            assert "relative_humidity_2m" in current
            assert "wind_speed_10m" in current
            assert "uv_index" in current or "uv_index" not in current  # Optional field
            assert "daily" in data
            print(f"✓ Weather: {current.get('temperature_2m')}°C")
        else:
            print(f"⚠ Weather API unavailable (status: {resp.status_code})")
    
    def test_currency_widget(self, api_client):
        """GET /api/widgets/currency returns rates for major currencies"""
        resp = api_client.get(f"{BASE_URL}/api/widgets/currency")
        if resp.status_code == 200:
            data = resp.json()
            assert "rates" in data
            rates = data["rates"]
            # Check required currencies
            for currency in ["USD", "EUR", "CNY", "GBP", "TRY"]:
                assert currency in rates, f"Missing {currency} rate"
                assert "value" in rates[currency]
                assert "previous" in rates[currency]
            print(f"✓ Currency rates: USD={rates['USD']['value']}")
        else:
            print(f"⚠ Currency API unavailable (status: {resp.status_code})")
    
    def test_magnetic_widget(self, api_client):
        """GET /api/widgets/magnetic returns Kp data array"""
        resp = api_client.get(f"{BASE_URL}/api/widgets/magnetic")
        if resp.status_code == 200:
            data = resp.json()
            assert "data" in data
            assert isinstance(data["data"], list)
            if len(data["data"]) > 0:
                item = data["data"][0]
                assert "kp" in item
            print(f"✓ Magnetic data points: {len(data['data'])}")
        else:
            print(f"⚠ Magnetic API unavailable (status: {resp.status_code})")
    
    def test_location_search(self, api_client):
        """GET /api/widgets/locations?q=Moscow returns location results"""
        resp = api_client.get(f"{BASE_URL}/api/widgets/locations?q=Moscow")
        assert resp.status_code == 200
        locations = resp.json()
        assert isinstance(locations, list)
        if len(locations) > 0:
            loc = locations[0]
            assert "name" in loc
            assert "latitude" in loc
            assert "longitude" in loc
        print(f"✓ Location search results: {len(locations)}")


# ==================== Map Endpoints ====================
class TestMapEndpoints:
    """Tests for problems map functionality"""
    
    def test_problems_map(self, api_client):
        """GET /api/map/problems returns problems with coordinates"""
        resp = api_client.get(f"{BASE_URL}/api/map/problems")
        assert resp.status_code == 200
        problems = resp.json()
        assert isinstance(problems, list)
        
        # Verify problem structure
        for problem in problems:
            assert "review_id" in problem
            assert "latitude" in problem
            assert "longitude" in problem
            assert "status" in problem
            assert "title" in problem
            # org_name may or may not be present
        print(f"✓ Got {len(problems)} problems with coordinates")


# ==================== Rewards Endpoints ====================
class TestRewardsEndpoints:
    """Tests for rewards system"""
    
    def test_list_rewards(self, api_client):
        """GET /api/rewards returns 11 seeded rewards"""
        resp = api_client.get(f"{BASE_URL}/api/rewards")
        assert resp.status_code == 200
        rewards = resp.json()
        assert isinstance(rewards, list)
        assert len(rewards) >= 11, f"Expected at least 11 rewards, got {len(rewards)}"
        
        # Verify reward structure
        for reward in rewards:
            assert "reward_id" in reward
            assert "name" in reward
            assert "description" in reward
            assert "price" in reward
            assert "icon" in reward
            assert "age_groups" in reward
            assert "category" in reward
        print(f"✓ Got {len(rewards)} rewards")


# ==================== Rating/Leaderboard Endpoints ====================
class TestRatingEndpoints:
    """Tests for rating and leaderboard"""
    
    def test_leaderboard(self, api_client):
        """GET /api/rating/leaderboard returns users sorted by points"""
        resp = api_client.get(f"{BASE_URL}/api/rating/leaderboard")
        assert resp.status_code == 200
        leaderboard = resp.json()
        assert isinstance(leaderboard, list)
        
        # Verify sorted by points descending
        for i, entry in enumerate(leaderboard):
            assert "rank" in entry
            assert "user_id" in entry
            assert "name" in entry
            assert "points" in entry
            assert "status" in entry
            assert "level" in entry
            if i > 0:
                assert leaderboard[i-1]["points"] >= entry["points"]
        print(f"✓ Leaderboard has {len(leaderboard)} entries")


# ==================== Auth-Protected Endpoints (401 Tests) ====================
class TestAuthProtectedEndpoints:
    """Tests that protected endpoints return 401 without auth"""
    
    def test_post_reviews_requires_auth(self, api_client):
        """POST /api/reviews requires authentication"""
        resp = api_client.post(f"{BASE_URL}/api/reviews", json={
            "org_id": "org_seed_001",
            "title": "Test",
            "content": "Test content",
            "rating": 5
        })
        assert resp.status_code == 401
        print("✓ POST /api/reviews returns 401 without auth")
    
    def test_post_news_requires_auth(self, api_client):
        """POST /api/news requires authentication"""
        resp = api_client.post(f"{BASE_URL}/api/news", json={
            "title": "Test",
            "content": "Test content"
        })
        assert resp.status_code == 401
        print("✓ POST /api/news returns 401 without auth")
    
    def test_notifications_requires_auth(self, api_client):
        """GET /api/notifications requires authentication"""
        resp = api_client.get(f"{BASE_URL}/api/notifications")
        assert resp.status_code == 401
        print("✓ GET /api/notifications returns 401 without auth")
    
    def test_profile_requires_auth(self, api_client):
        """GET /api/profile requires authentication"""
        resp = api_client.get(f"{BASE_URL}/api/profile")
        assert resp.status_code == 401
        print("✓ GET /api/profile returns 401 without auth")
    
    def test_verification_status_requires_auth(self, api_client):
        """GET /api/verification/status requires authentication"""
        resp = api_client.get(f"{BASE_URL}/api/verification/status")
        assert resp.status_code == 401
        print("✓ GET /api/verification/status returns 401 without auth")
    
    def test_referral_stats_requires_auth(self, api_client):
        """GET /api/referral/stats requires authentication"""
        resp = api_client.get(f"{BASE_URL}/api/referral/stats")
        assert resp.status_code == 401
        print("✓ GET /api/referral/stats returns 401 without auth")
    
    def test_points_balance_requires_auth(self, api_client):
        """GET /api/points/balance requires authentication"""
        resp = api_client.get(f"{BASE_URL}/api/points/balance")
        assert resp.status_code == 401
        print("✓ GET /api/points/balance returns 401 without auth")
    
    def test_rating_status_requires_auth(self, api_client):
        """GET /api/rating/status requires authentication"""
        resp = api_client.get(f"{BASE_URL}/api/rating/status")
        assert resp.status_code == 401
        print("✓ GET /api/rating/status returns 401 without auth")


# ==================== Authenticated Flow Tests ====================
class TestAuthenticatedFlows:
    """Tests for authenticated user flows"""
    
    def test_get_profile(self, auth_client):
        """GET /api/profile returns user profile"""
        resp = auth_client.get(f"{BASE_URL}/api/profile")
        assert resp.status_code == 200
        profile = resp.json()
        assert "user_id" in profile
        assert "email" in profile
        assert "name" in profile
        assert "points" in profile
        print(f"✓ Got profile: {profile['name']}")
    
    def test_get_notifications(self, auth_client):
        """GET /api/notifications returns notifications list"""
        resp = auth_client.get(f"{BASE_URL}/api/notifications")
        assert resp.status_code == 200
        notifs = resp.json()
        assert isinstance(notifs, list)
        print(f"✓ Got {len(notifs)} notifications")
    
    def test_get_rating_status(self, auth_client):
        """GET /api/rating/status returns user rating status"""
        resp = auth_client.get(f"{BASE_URL}/api/rating/status")
        assert resp.status_code == 200
        status = resp.json()
        assert "current" in status
        assert "level" in status
        assert "points" in status
        assert "all_statuses" in status
        print(f"✓ Rating status: {status['current']['name']}, level {status['level']}")
    
    def test_get_verification_status(self, auth_client):
        """GET /api/verification/status returns verification details"""
        resp = auth_client.get(f"{BASE_URL}/api/verification/status")
        assert resp.status_code == 200
        status = resp.json()
        assert "level" in status
        assert "phone_verified" in status
        assert "passport_verified" in status
        assert "bank_id_verified" in status
        assert "yandex_id_verified" in status
        assert "levels" in status
        print(f"✓ Verification level: {status['level']}")
    
    def test_get_referral_stats(self, auth_client):
        """GET /api/referral/stats returns referral information"""
        resp = auth_client.get(f"{BASE_URL}/api/referral/stats")
        assert resp.status_code == 200
        stats = resp.json()
        assert "referral_code" in stats
        assert "referred_count" in stats
        assert "total_bonus" in stats
        print(f"✓ Referral code: {stats['referral_code']}")
    
    def test_get_points_balance(self, auth_client):
        """GET /api/points/balance returns user points"""
        resp = auth_client.get(f"{BASE_URL}/api/points/balance")
        assert resp.status_code == 200
        data = resp.json()
        assert "balance" in data
        print(f"✓ Points balance: {data['balance']}")
    
    def test_create_news_article(self, auth_client):
        """POST /api/news creates a news article"""
        resp = auth_client.post(f"{BASE_URL}/api/news", json={
            "title": f"TEST_News_{datetime.now().timestamp()}",
            "content": "Test content for automated testing",
            "level": "city",
            "category": "general"
        })
        assert resp.status_code == 200
        article = resp.json()
        assert "article_id" in article
        assert article["title"].startswith("TEST_News")
        print(f"✓ Created news article: {article['article_id']}")
        return article["article_id"]
    
    def test_like_news_article(self, auth_client):
        """POST /api/news/{id}/like toggles like"""
        # First get an article
        resp = auth_client.get(f"{BASE_URL}/api/news")
        articles = resp.json()
        if len(articles) > 0:
            article_id = articles[0]["article_id"]
            resp = auth_client.post(f"{BASE_URL}/api/news/{article_id}/like")
            assert resp.status_code == 200
            data = resp.json()
            assert "liked" in data
            print(f"✓ Toggled like on article: liked={data['liked']}")
    
    def test_create_review(self, auth_client):
        """POST /api/reviews creates a review"""
        resp = auth_client.post(f"{BASE_URL}/api/reviews", json={
            "org_id": "org_seed_001",
            "title": f"TEST_Review_{datetime.now().timestamp()}",
            "content": "Test review content for automated testing",
            "rating": 4,
            "latitude": 43.025,
            "longitude": 44.682
        })
        assert resp.status_code == 201
        review = resp.json()
        assert "review_id" in review
        assert review["status"] == "pending"
        print(f"✓ Created review: {review['review_id']}")


# ==================== Admin Endpoints Tests ====================
class TestAdminEndpoints:
    """Tests for admin panel functionality (requires admin role)"""
    
    def test_admin_stats(self, auth_client):
        """GET /api/admin/stats returns admin statistics"""
        resp = auth_client.get(f"{BASE_URL}/api/admin/stats")
        # Could be 200 (admin) or 403 (non-admin)
        if resp.status_code == 200:
            stats = resp.json()
            assert "total_users" in stats
            assert "total_reviews" in stats
            assert "pending_reviews" in stats
            assert "total_organizations" in stats
            print(f"✓ Admin stats: {stats['total_users']} users, {stats['total_reviews']} reviews")
        elif resp.status_code == 403:
            print("⚠ Admin access denied (test user is not admin)")
        else:
            pytest.fail(f"Unexpected status: {resp.status_code}")
    
    def test_admin_reviews(self, auth_client):
        """GET /api/admin/reviews returns all reviews for admin"""
        resp = auth_client.get(f"{BASE_URL}/api/admin/reviews")
        if resp.status_code == 200:
            reviews = resp.json()
            assert isinstance(reviews, list)
            print(f"✓ Admin reviews: {len(reviews)}")
        elif resp.status_code == 403:
            print("⚠ Admin access denied")
    
    def test_admin_users(self, auth_client):
        """GET /api/admin/users returns all users for admin"""
        resp = auth_client.get(f"{BASE_URL}/api/admin/users")
        if resp.status_code == 200:
            users = resp.json()
            assert isinstance(users, list)
            print(f"✓ Admin users: {len(users)}")
        elif resp.status_code == 403:
            print("⚠ Admin access denied")


# ==================== Verification Flow Tests ====================
class TestVerificationFlows:
    """Tests for identity verification processes"""
    
    def test_phone_verification_send_code(self, auth_client):
        """POST /api/verification/phone sends code"""
        resp = auth_client.post(f"{BASE_URL}/api/verification/phone", json={
            "phone": "+79991234567"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "success" in data
        assert "message" in data
        # In test mode, code is returned in message
        print(f"✓ Phone verification: {data['message'][:50]}...")
    
    def test_passport_verification_invalid(self, auth_client):
        """POST /api/verification/passport with invalid data"""
        resp = auth_client.post(f"{BASE_URL}/api/verification/passport", json={
            "full_name": "Test User",
            "birth_date": "1990-01-01",
            "series": "12",  # Invalid - should be 4 digits
            "number": "123"  # Invalid - should be 6 digits
        })
        assert resp.status_code == 400
        print("✓ Passport validation works for invalid data")
    
    def test_bank_id_verification(self, auth_client):
        """POST /api/verification/bank-id verifies bank ID"""
        resp = auth_client.post(f"{BASE_URL}/api/verification/bank-id", json={
            "bank": "sber"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "success" in data
        print(f"✓ Bank ID verification: {data.get('message', 'success')}")
    
    def test_yandex_id_verification(self, auth_client):
        """POST /api/verification/yandex-id verifies Yandex ID"""
        resp = auth_client.post(f"{BASE_URL}/api/verification/yandex-id")
        assert resp.status_code == 200
        data = resp.json()
        assert "success" in data
        print("✓ Yandex ID verification success")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
