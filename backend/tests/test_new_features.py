"""
Backend tests for new features: News Feed, Widgets (Weather/Currency/Magnetic), Problems Map, Verification
Tests both public endpoints and auth-protected endpoint behavior
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthAndRoot:
    """Basic health check tests"""
    
    def test_health_endpoint(self):
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        print("✓ Health endpoint working")
    
    def test_root_endpoint(self):
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        print("✓ Root endpoint working")


class TestNewsFeedAPI:
    """News Feed API tests"""
    
    def test_get_news_list(self):
        """GET /api/news returns news articles"""
        response = requests.get(f"{BASE_URL}/api/news")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            article = data[0]
            assert "article_id" in article
            assert "title" in article
            assert "content" in article
            assert "level" in article
            assert "category" in article
            assert "likes" in article
            assert "views" in article
            assert "created_at" in article
        print(f"✓ News list returned {len(data)} articles")
    
    def test_get_news_with_level_filter(self):
        """GET /api/news?level=city filters by level"""
        response = requests.get(f"{BASE_URL}/api/news", params={"level": "city"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for article in data:
            assert article.get("level") == "city"
        print(f"✓ News filtered by level returned {len(data)} city articles")
    
    def test_get_news_with_category_filter(self):
        """GET /api/news?category=health filters by category"""
        response = requests.get(f"{BASE_URL}/api/news", params={"category": "health"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for article in data:
            assert article.get("category") == "health"
        print(f"✓ News filtered by category returned {len(data)} health articles")
    
    def test_create_news_requires_auth(self):
        """POST /api/news requires authentication"""
        response = requests.post(f"{BASE_URL}/api/news", json={
            "title": "Test News",
            "content": "Test content"
        })
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        print("✓ Create news correctly requires authentication")
    
    def test_like_news_requires_auth(self):
        """POST /api/news/{id}/like requires authentication"""
        # Get a news article first
        news_response = requests.get(f"{BASE_URL}/api/news")
        assert news_response.status_code == 200
        articles = news_response.json()
        if len(articles) > 0:
            article_id = articles[0]["article_id"]
            response = requests.post(f"{BASE_URL}/api/news/{article_id}/like")
            assert response.status_code == 401
            print("✓ Like news correctly requires authentication")
        else:
            pytest.skip("No news articles to test like functionality")
    
    def test_get_news_comments(self):
        """GET /api/news/{id}/comments returns comments"""
        news_response = requests.get(f"{BASE_URL}/api/news")
        assert news_response.status_code == 200
        articles = news_response.json()
        if len(articles) > 0:
            article_id = articles[0]["article_id"]
            response = requests.get(f"{BASE_URL}/api/news/{article_id}/comments")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            print(f"✓ News comments endpoint working, returned {len(data)} comments")
        else:
            pytest.skip("No news articles to test comments")


class TestWidgetsAPI:
    """Info Widgets API tests: Weather, Currency, Magnetic Storms"""
    
    def test_get_weather(self):
        """GET /api/widgets/weather returns weather data"""
        response = requests.get(f"{BASE_URL}/api/widgets/weather", params={"lat": 43.023, "lon": 44.682})
        assert response.status_code == 200
        data = response.json()
        # Validate structure
        assert "current" in data
        assert "daily" in data
        current = data["current"]
        assert "temperature_2m" in current
        assert "relative_humidity_2m" in current
        assert "wind_speed_10m" in current
        assert "weather_code" in current
        assert "uv_index" in current
        # Validate daily forecast
        daily = data["daily"]
        assert "temperature_2m_max" in daily
        assert "temperature_2m_min" in daily
        assert len(daily["temperature_2m_max"]) >= 3
        print(f"✓ Weather widget working - current temp: {current['temperature_2m']}°C")
    
    def test_get_currency_rates(self):
        """GET /api/widgets/currency returns currency rates"""
        response = requests.get(f"{BASE_URL}/api/widgets/currency")
        assert response.status_code == 200
        data = response.json()
        assert "rates" in data
        rates = data["rates"]
        # Check expected currencies
        expected_currencies = ["USD", "EUR", "CNY", "GBP", "TRY"]
        for currency in expected_currencies:
            assert currency in rates, f"Missing currency: {currency}"
            rate = rates[currency]
            assert "name" in rate
            assert "value" in rate
            assert "previous" in rate
            assert "nominal" in rate
        print(f"✓ Currency widget working - USD: {rates['USD']['value']} RUB")
    
    def test_get_magnetic_storms(self):
        """GET /api/widgets/magnetic returns magnetic storm data"""
        response = requests.get(f"{BASE_URL}/api/widgets/magnetic")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        storm_data = data["data"]
        assert isinstance(storm_data, list)
        if len(storm_data) > 0:
            entry = storm_data[0]
            assert "time" in entry
            assert "kp" in entry
            assert "kp_str" in entry
        print(f"✓ Magnetic storms widget working - {len(storm_data)} readings")
    
    def test_search_locations(self):
        """GET /api/widgets/locations?q=Moscow returns location results"""
        response = requests.get(f"{BASE_URL}/api/widgets/locations", params={"q": "Moscow"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Should return at least one location for 'Moscow'"
        loc = data[0]
        assert "name" in loc
        assert "country" in loc
        assert "latitude" in loc
        assert "longitude" in loc
        print(f"✓ Location search working - found {len(data)} results for 'Moscow'")
    
    def test_search_locations_short_query(self):
        """GET /api/widgets/locations?q=M returns empty for short queries"""
        response = requests.get(f"{BASE_URL}/api/widgets/locations", params={"q": "M"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0, "Short queries should return empty"
        print("✓ Location search correctly rejects short queries")


class TestProblemsMapAPI:
    """Problems Map API tests"""
    
    def test_get_problems_map(self):
        """GET /api/map/problems returns problems with coordinates"""
        response = requests.get(f"{BASE_URL}/api/map/problems")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            problem = data[0]
            # Validate required fields
            assert "review_id" in problem
            assert "title" in problem
            assert "status" in problem
            assert "rating" in problem
            assert "latitude" in problem
            assert "longitude" in problem
            assert "org_name" in problem
            assert "verification_count" in problem
            assert "created_at" in problem
            # Validate coordinates are numbers
            assert isinstance(problem["latitude"], (int, float))
            assert isinstance(problem["longitude"], (int, float))
        print(f"✓ Problems map API working - {len(data)} problems with coordinates")
    
    def test_problems_have_valid_status(self):
        """Problems should have valid status values"""
        response = requests.get(f"{BASE_URL}/api/map/problems")
        assert response.status_code == 200
        data = response.json()
        valid_statuses = ["pending", "approved", "rejected", "expired"]
        for problem in data:
            assert problem["status"] in valid_statuses, f"Invalid status: {problem['status']}"
        print(f"✓ All {len(data)} problems have valid status values")


class TestVerificationAPI:
    """Verification API tests - all require authentication"""
    
    def test_verification_status_requires_auth(self):
        """GET /api/verification/status requires authentication"""
        response = requests.get(f"{BASE_URL}/api/verification/status")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        print("✓ Verification status correctly requires authentication")
    
    def test_send_phone_code_requires_auth(self):
        """POST /api/verification/phone requires authentication"""
        response = requests.post(f"{BASE_URL}/api/verification/phone", json={"phone": "+79991234567"})
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        print("✓ Phone verification correctly requires authentication")
    
    def test_confirm_phone_requires_auth(self):
        """POST /api/verification/phone/confirm requires authentication"""
        response = requests.post(f"{BASE_URL}/api/verification/phone/confirm", json={"code": "123456"})
        assert response.status_code == 401
        print("✓ Phone confirmation correctly requires authentication")
    
    def test_verify_passport_requires_auth(self):
        """POST /api/verification/passport requires authentication"""
        response = requests.post(f"{BASE_URL}/api/verification/passport", json={
            "full_name": "Test User",
            "birth_date": "1990-01-01",
            "series": "1234",
            "number": "567890"
        })
        assert response.status_code == 401
        print("✓ Passport verification correctly requires authentication")
    
    def test_bank_id_requires_auth(self):
        """POST /api/verification/bank-id requires authentication"""
        response = requests.post(f"{BASE_URL}/api/verification/bank-id", json={"bank": "sber"})
        assert response.status_code == 401
        print("✓ Bank ID verification correctly requires authentication")
    
    def test_yandex_id_requires_auth(self):
        """POST /api/verification/yandex-id requires authentication"""
        response = requests.post(f"{BASE_URL}/api/verification/yandex-id")
        assert response.status_code == 401
        print("✓ Yandex ID verification correctly requires authentication")


class TestExistingAPIs:
    """Test existing APIs are still working"""
    
    def test_organizations_list(self):
        """GET /api/organizations returns organizations"""
        response = requests.get(f"{BASE_URL}/api/organizations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Organizations API working - {len(data)} organizations")
    
    def test_reviews_list(self):
        """GET /api/reviews returns reviews"""
        response = requests.get(f"{BASE_URL}/api/reviews")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Reviews API working - {len(data)} reviews")
    
    def test_rewards_list(self):
        """GET /api/rewards returns rewards"""
        response = requests.get(f"{BASE_URL}/api/rewards")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Rewards API working - {len(data)} rewards")
    
    def test_leaderboard(self):
        """GET /api/rating/leaderboard returns leaderboard"""
        response = requests.get(f"{BASE_URL}/api/rating/leaderboard")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Leaderboard API working - {len(data)} users")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
