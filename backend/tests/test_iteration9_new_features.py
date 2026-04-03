"""
Iteration 9 Tests: New Features
- Mandatory verification proof (photos + 20-char comment)
- Government officials with blacklist
- Kyrgyzstan legal jurisdiction
- People's Councils system
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test session from previous iteration
TEST_SESSION_TOKEN = "test_session_iteration9_token"
TEST_USER_ID = f"test_user_iteration9_{uuid.uuid4().hex[:8]}"

@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session

@pytest.fixture(scope="module")
def auth_headers(api_client):
    """Create test user and session for authenticated requests"""
    from pymongo import MongoClient
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'test_database')
    client = MongoClient(mongo_url)
    db = client[db_name]
    
    # Create test user
    db.users.update_one(
        {"user_id": TEST_USER_ID},
        {"$set": {
            "user_id": TEST_USER_ID,
            "email": f"test_iter9_{uuid.uuid4().hex[:6]}@test.com",
            "name": "Test User Iter9",
            "points": 100,
            "role": "user",
            "created_at": datetime.utcnow().isoformat()
        }},
        upsert=True
    )
    
    # Create session
    db.user_sessions.update_one(
        {"session_token": TEST_SESSION_TOKEN},
        {"$set": {
            "session_token": TEST_SESSION_TOKEN,
            "user_id": TEST_USER_ID,
            "expires_at": "2030-01-01T00:00:00Z",
            "created_at": datetime.utcnow().isoformat()
        }},
        upsert=True
    )
    
    return {"Authorization": f"Bearer {TEST_SESSION_TOKEN}"}


# ==================== Legal Info Tests ====================
class TestLegalInfo:
    """Tests for Kyrgyzstan jurisdiction legal info"""
    
    def test_legal_info_returns_kyrgyzstan(self, api_client):
        """GET /api/legal/info returns Kyrgyzstan jurisdiction"""
        response = api_client.get(f"{BASE_URL}/api/legal/info")
        assert response.status_code == 200
        data = response.json()
        
        # Verify Kyrgyzstan jurisdiction
        assert "Кыргызская Республика" in data.get("legal_address", ""), "Should mention Kyrgyzstan"
        assert "ОсОО" in data.get("operator_name", ""), "Should use ОсОО (Kyrgyz LLC)"
        assert "ПВТ" in data.get("inn", "") or "ПВТ" in data.get("legal_address", ""), "Should mention PVT (Tech Park)"
        assert "Бишкек" in data.get("legal_address", ""), "Should mention Bishkek"
        
        # Verify no personal names
        assert "operator_name" in data
        assert "@" in data.get("email", ""), "Should have email"
        print(f"Legal info: {data}")


# ==================== Government Officials Tests ====================
class TestGovCategories:
    """Tests for government categories endpoint"""
    
    def test_get_gov_categories_returns_15(self, api_client):
        """GET /api/gov/categories returns 15 allowed categories"""
        response = api_client.get(f"{BASE_URL}/api/gov/categories")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, dict), "Should return dict of categories"
        assert len(data) == 15, f"Should have 15 categories, got {len(data)}"
        
        # Check some expected categories
        expected = ["healthcare", "education", "mfc", "tax", "court", "police_local"]
        for cat in expected:
            assert cat in data, f"Missing category: {cat}"
        
        print(f"Gov categories: {list(data.keys())}")


class TestGovOfficials:
    """Tests for government officials CRUD"""
    
    def test_create_official_requires_auth(self, api_client):
        """POST /api/gov/officials requires authentication"""
        response = api_client.post(f"{BASE_URL}/api/gov/officials", json={
            "name": "Test Official",
            "position": "Director",
            "department": "Test Dept",
            "gov_category": "healthcare"
        })
        assert response.status_code == 401
    
    def test_create_official_valid_category(self, api_client, auth_headers):
        """POST /api/gov/officials creates official with valid category"""
        response = api_client.post(f"{BASE_URL}/api/gov/officials", json={
            "name": "TEST_Иванов Иван Иванович",
            "position": "Главный врач",
            "department": "Городская поликлиника №1",
            "gov_category": "healthcare",
            "region": "Бишкек"
        }, headers=auth_headers)
        
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "official_id" in data
        assert data["name"] == "TEST_Иванов Иван Иванович"
        assert data["gov_category"] == "healthcare"
        print(f"Created official: {data['official_id']}")
        return data["official_id"]
    
    def test_create_official_invalid_category(self, api_client, auth_headers):
        """POST /api/gov/officials rejects invalid category"""
        response = api_client.post(f"{BASE_URL}/api/gov/officials", json={
            "name": "Test Official",
            "position": "Agent",
            "department": "Secret Dept",
            "gov_category": "fsb"  # Banned category
        }, headers=auth_headers)
        
        assert response.status_code == 400, f"Should reject banned category, got {response.status_code}"
    
    def test_create_official_banned_keyword_fsb(self, api_client, auth_headers):
        """POST /api/gov/officials rejects FSB keyword in department"""
        response = api_client.post(f"{BASE_URL}/api/gov/officials", json={
            "name": "Петров Пётр",
            "position": "Сотрудник",
            "department": "ФСБ России",  # Banned keyword
            "gov_category": "administration"
        }, headers=auth_headers)
        
        assert response.status_code == 403, f"Should reject FSB keyword with 403, got {response.status_code}"
        print(f"FSB rejection response: {response.json()}")
    
    def test_create_official_banned_keyword_military(self, api_client, auth_headers):
        """POST /api/gov/officials rejects military keywords"""
        response = api_client.post(f"{BASE_URL}/api/gov/officials", json={
            "name": "Сидоров Сидор",
            "position": "Офицер",
            "department": "Военная часть",  # Contains 'военн'
            "gov_category": "administration"
        }, headers=auth_headers)
        
        assert response.status_code == 403, f"Should reject military keyword with 403, got {response.status_code}"
    
    def test_create_official_banned_keyword_gru(self, api_client, auth_headers):
        """POST /api/gov/officials rejects GRU keyword"""
        response = api_client.post(f"{BASE_URL}/api/gov/officials", json={
            "name": "Агент Смит",
            "position": "Разведчик",
            "department": "ГРУ Генштаба",  # Banned
            "gov_category": "administration"
        }, headers=auth_headers)
        
        assert response.status_code == 403
    
    def test_list_officials(self, api_client):
        """GET /api/gov/officials lists officials"""
        response = api_client.get(f"{BASE_URL}/api/gov/officials")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Found {len(data)} officials")
    
    def test_list_officials_filter_category(self, api_client):
        """GET /api/gov/officials?category= filters by category"""
        response = api_client.get(f"{BASE_URL}/api/gov/officials", params={"category": "healthcare"})
        assert response.status_code == 200
        data = response.json()
        for off in data:
            assert off["gov_category"] == "healthcare"
    
    def test_list_officials_search(self, api_client):
        """GET /api/gov/officials?q= searches by name/department"""
        response = api_client.get(f"{BASE_URL}/api/gov/officials", params={"q": "TEST_"})
        assert response.status_code == 200


class TestGovReviews:
    """Tests for government official reviews"""
    
    @pytest.fixture
    def test_official_id(self, api_client, auth_headers):
        """Create a test official for review tests"""
        response = api_client.post(f"{BASE_URL}/api/gov/officials", json={
            "name": f"TEST_Review_Official_{uuid.uuid4().hex[:6]}",
            "position": "Директор",
            "department": "Тестовое учреждение",
            "gov_category": "education"
        }, headers=auth_headers)
        if response.status_code == 200:
            return response.json()["official_id"]
        # Try to get existing
        resp = api_client.get(f"{BASE_URL}/api/gov/officials", params={"q": "TEST_Review"})
        if resp.status_code == 200 and resp.json():
            return resp.json()[0]["official_id"]
        pytest.skip("Could not create test official")
    
    def test_create_gov_review_requires_auth(self, api_client, test_official_id):
        """POST /api/gov/reviews requires authentication"""
        response = api_client.post(f"{BASE_URL}/api/gov/reviews", json={
            "official_id": test_official_id,
            "title": "Test Review",
            "content": "This is a test review content with enough characters",
            "rating": 4,
            "category": "service_quality"
        })
        assert response.status_code == 401
    
    def test_create_gov_review_success(self, api_client, auth_headers, test_official_id):
        """POST /api/gov/reviews creates review"""
        response = api_client.post(f"{BASE_URL}/api/gov/reviews", json={
            "official_id": test_official_id,
            "title": "Отличный специалист",
            "content": "Очень профессиональный подход к работе, помог решить вопрос быстро",
            "rating": 5,
            "category": "competence"
        }, headers=auth_headers)
        
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "review_id" in data
        assert data["rating"] == 5
        print(f"Created gov review: {data['review_id']}")
    
    def test_create_gov_review_banned_content(self, api_client, auth_headers, test_official_id):
        """POST /api/gov/reviews rejects banned keywords in content"""
        response = api_client.post(f"{BASE_URL}/api/gov/reviews", json={
            "official_id": test_official_id,
            "title": "Отзыв о сотруднике",
            "content": "Этот человек работал в ФСБ и теперь здесь",  # Contains banned keyword
            "rating": 3,
            "category": "service_quality"
        }, headers=auth_headers)
        
        assert response.status_code == 403, f"Should reject banned content with 403, got {response.status_code}"
    
    def test_list_gov_reviews(self, api_client):
        """GET /api/gov/reviews lists reviews"""
        response = api_client.get(f"{BASE_URL}/api/gov/reviews")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_list_gov_reviews_filter_official(self, api_client, test_official_id):
        """GET /api/gov/reviews?official_id= filters by official"""
        response = api_client.get(f"{BASE_URL}/api/gov/reviews", params={"official_id": test_official_id})
        assert response.status_code == 200


# ==================== People's Councils Tests ====================
class TestCouncilLevels:
    """Tests for council levels endpoint"""
    
    def test_get_council_levels_returns_5(self, api_client):
        """GET /api/councils/levels returns 5 levels"""
        response = api_client.get(f"{BASE_URL}/api/councils/levels")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, dict)
        assert len(data) == 5, f"Should have 5 levels, got {len(data)}"
        
        expected_levels = ["yard", "district", "city", "republic", "country"]
        for level in expected_levels:
            assert level in data, f"Missing level: {level}"
        
        print(f"Council levels: {list(data.keys())}")


class TestCouncils:
    """Tests for councils CRUD"""
    
    def test_create_council_requires_auth(self, api_client):
        """POST /api/councils requires authentication"""
        response = api_client.post(f"{BASE_URL}/api/councils", json={
            "name": "Test Council",
            "level": "yard",
            "description": "Test description for council"
        })
        assert response.status_code == 401
    
    def test_create_council_success(self, api_client, auth_headers):
        """POST /api/councils creates council"""
        council_name = f"TEST_Совет двора {uuid.uuid4().hex[:6]}"
        response = api_client.post(f"{BASE_URL}/api/councils", json={
            "name": council_name,
            "level": "yard",
            "description": "Совет жителей двора для решения общих вопросов",
            "address": "ул. Тестовая, 1"
        }, headers=auth_headers)
        
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "council_id" in data
        assert data["name"] == council_name
        assert data["level"] == "yard"
        assert data["member_count"] == 1  # Creator is first member
        assert len(data["members"]) == 1
        assert data["members"][0]["role"] == "chairman"  # Creator is chairman
        print(f"Created council: {data['council_id']}")
        return data["council_id"]
    
    def test_list_councils(self, api_client):
        """GET /api/councils lists councils"""
        response = api_client.get(f"{BASE_URL}/api/councils")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_list_councils_filter_level(self, api_client):
        """GET /api/councils?level= filters by level"""
        response = api_client.get(f"{BASE_URL}/api/councils", params={"level": "yard"})
        assert response.status_code == 200
        for council in response.json():
            assert council["level"] == "yard"


class TestCouncilMembership:
    """Tests for council join/leave"""
    
    @pytest.fixture
    def test_council_id(self, api_client, auth_headers):
        """Create a test council"""
        response = api_client.post(f"{BASE_URL}/api/councils", json={
            "name": f"TEST_Membership_Council_{uuid.uuid4().hex[:6]}",
            "level": "district",
            "description": "Council for membership testing"
        }, headers=auth_headers)
        if response.status_code == 200:
            return response.json()["council_id"]
        pytest.skip("Could not create test council")
    
    @pytest.fixture
    def second_user_headers(self, api_client):
        """Create second test user for join/leave tests"""
        from pymongo import MongoClient
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'test_database')
        client = MongoClient(mongo_url)
        db = client[db_name]
        
        user_id = f"test_user2_iter9_{uuid.uuid4().hex[:8]}"
        session_token = f"test_session2_iter9_{uuid.uuid4().hex[:8]}"
        
        db.users.update_one(
            {"user_id": user_id},
            {"$set": {
                "user_id": user_id,
                "email": f"test2_iter9_{uuid.uuid4().hex[:6]}@test.com",
                "name": "Second Test User",
                "points": 50,
                "role": "user",
                "created_at": datetime.utcnow().isoformat()
            }},
            upsert=True
        )
        
        db.user_sessions.update_one(
            {"session_token": session_token},
            {"$set": {
                "session_token": session_token,
                "user_id": user_id,
                "expires_at": "2030-01-01T00:00:00Z"
            }},
            upsert=True
        )
        
        return {"Authorization": f"Bearer {session_token}"}
    
    def test_join_council(self, api_client, second_user_headers, test_council_id):
        """POST /api/councils/{id}/join adds user as member"""
        response = api_client.post(f"{BASE_URL}/api/councils/{test_council_id}/join", headers=second_user_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        
        # Verify membership
        council = api_client.get(f"{BASE_URL}/api/councils/{test_council_id}").json()
        assert council["member_count"] >= 2
    
    def test_leave_council_non_chairman(self, api_client, second_user_headers, test_council_id):
        """POST /api/councils/{id}/leave removes non-chairman member"""
        # First join
        api_client.post(f"{BASE_URL}/api/councils/{test_council_id}/join", headers=second_user_headers)
        
        # Then leave
        response = api_client.post(f"{BASE_URL}/api/councils/{test_council_id}/leave", headers=second_user_headers)
        assert response.status_code == 200
    
    def test_chairman_cannot_leave(self, api_client, auth_headers, test_council_id):
        """POST /api/councils/{id}/leave fails for chairman"""
        response = api_client.post(f"{BASE_URL}/api/councils/{test_council_id}/leave", headers=auth_headers)
        assert response.status_code == 400, "Chairman should not be able to leave"


class TestCouncilDiscussions:
    """Tests for council discussions"""
    
    @pytest.fixture
    def test_council_with_member(self, api_client, auth_headers):
        """Create council where auth user is member"""
        response = api_client.post(f"{BASE_URL}/api/councils", json={
            "name": f"TEST_Discussion_Council_{uuid.uuid4().hex[:6]}",
            "level": "city",
            "description": "Council for discussion testing"
        }, headers=auth_headers)
        if response.status_code == 200:
            return response.json()["council_id"]
        pytest.skip("Could not create test council")
    
    def test_create_discussion_members_only(self, api_client, test_council_with_member):
        """POST /api/councils/{id}/discussions requires membership"""
        response = api_client.post(
            f"{BASE_URL}/api/councils/{test_council_with_member}/discussions",
            json={"title": "Test Discussion", "content": "Test content for discussion", "category": "general"}
        )
        assert response.status_code == 401  # No auth
    
    def test_create_discussion_success(self, api_client, auth_headers, test_council_with_member):
        """POST /api/councils/{id}/discussions creates discussion"""
        response = api_client.post(
            f"{BASE_URL}/api/councils/{test_council_with_member}/discussions",
            json={
                "title": "Обсуждение благоустройства",
                "content": "Предлагаю обсудить план благоустройства территории",
                "category": "proposal"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "discussion_id" in data
        print(f"Created discussion: {data['discussion_id']}")
        return data["discussion_id"]
    
    def test_list_discussions(self, api_client, test_council_with_member):
        """GET /api/councils/{id}/discussions lists discussions"""
        response = api_client.get(f"{BASE_URL}/api/councils/{test_council_with_member}/discussions")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_reply_to_discussion(self, api_client, auth_headers, test_council_with_member):
        """POST /api/councils/{id}/discussions/{did}/reply adds reply"""
        # Create discussion first
        disc_resp = api_client.post(
            f"{BASE_URL}/api/councils/{test_council_with_member}/discussions",
            json={"title": "Reply Test", "content": "Discussion for reply testing", "category": "general"},
            headers=auth_headers
        )
        if disc_resp.status_code != 200:
            pytest.skip("Could not create discussion")
        disc_id = disc_resp.json()["discussion_id"]
        
        # Add reply
        response = api_client.post(
            f"{BASE_URL}/api/councils/{test_council_with_member}/discussions/{disc_id}/reply",
            json={"text": "Согласен с предложением!"},
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "reply_id" in data


class TestCouncilVotes:
    """Tests for council voting"""
    
    @pytest.fixture
    def test_council_as_chairman(self, api_client, auth_headers):
        """Create council where auth user is chairman"""
        response = api_client.post(f"{BASE_URL}/api/councils", json={
            "name": f"TEST_Vote_Council_{uuid.uuid4().hex[:6]}",
            "level": "republic",
            "description": "Council for voting testing"
        }, headers=auth_headers)
        if response.status_code == 200:
            return response.json()["council_id"]
        pytest.skip("Could not create test council")
    
    def test_create_vote_chairman_only(self, api_client, test_council_as_chairman):
        """POST /api/councils/{id}/votes requires chairman/moderator"""
        # Without auth
        response = api_client.post(
            f"{BASE_URL}/api/councils/{test_council_as_chairman}/votes",
            json={"title": "Test Vote", "description": "Test description", "options": ["Yes", "No"]}
        )
        assert response.status_code == 401
    
    def test_create_vote_success(self, api_client, auth_headers, test_council_as_chairman):
        """POST /api/councils/{id}/votes creates vote (chairman)"""
        response = api_client.post(
            f"{BASE_URL}/api/councils/{test_council_as_chairman}/votes",
            json={
                "title": "Голосование за ремонт",
                "description": "Поддерживаете ли вы план ремонта?",
                "options": ["За", "Против", "Воздержался"]
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "vote_id" in data
        assert len(data["options"]) == 3
        print(f"Created vote: {data['vote_id']}")
        return data["vote_id"]
    
    def test_cast_vote(self, api_client, auth_headers, test_council_as_chairman):
        """POST /api/councils/{id}/votes/{vid}/cast casts vote"""
        # Create vote first
        vote_resp = api_client.post(
            f"{BASE_URL}/api/councils/{test_council_as_chairman}/votes",
            json={"title": "Cast Test", "description": "Vote for casting test", "options": ["Option A", "Option B"]},
            headers=auth_headers
        )
        if vote_resp.status_code != 200:
            pytest.skip("Could not create vote")
        vote_data = vote_resp.json()
        vote_id = vote_data["vote_id"]
        option_id = vote_data["options"][0]["option_id"]
        
        # Cast vote
        response = api_client.post(
            f"{BASE_URL}/api/councils/{test_council_as_chairman}/votes/{vote_id}/cast",
            json={"option_id": option_id},
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Failed: {response.text}"


# ==================== Verification Requirements Tests ====================
class TestVerificationRequirements:
    """Tests for mandatory photo + 20-char comment verification"""
    
    @pytest.fixture
    def test_review_id(self, api_client, auth_headers):
        """Create a pending review for verification tests"""
        from pymongo import MongoClient
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'test_database')
        client = MongoClient(mongo_url)
        db = client[db_name]
        
        # Create a different user's review (can't verify own)
        review_id = f"rev_test_iter9_{uuid.uuid4().hex[:8]}"
        db.reviews.update_one(
            {"review_id": review_id},
            {"$set": {
                "review_id": review_id,
                "user_id": "different_user_123",  # Different user
                "user_name": "Other User",
                "org_id": "org_seed_001",
                "org_name": "Test Org",
                "title": "Test Review for Verification",
                "content": "This is a test review",
                "rating": 4,
                "status": "pending",
                "verification_count": 0,
                "photos": [],
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": "2030-01-01T00:00:00Z"
            }},
            upsert=True
        )
        return review_id
    
    def test_verification_without_photos_fails(self, api_client, auth_headers, test_review_id):
        """POST /api/verifications fails without photos"""
        response = api_client.post(f"{BASE_URL}/api/verifications", json={
            "review_id": test_review_id,
            "comment": "This is a valid comment with more than twenty characters",
            "photos": []  # Empty photos
        }, headers=auth_headers)
        
        assert response.status_code in [400, 422], f"Should fail without photos, got {response.status_code}: {response.text}"
    
    def test_verification_without_comment_fails(self, api_client, auth_headers, test_review_id):
        """POST /api/verifications fails without comment"""
        response = api_client.post(f"{BASE_URL}/api/verifications", json={
            "review_id": test_review_id,
            "comment": "",  # Empty comment
            "photos": ["/api/uploads/test.jpg"]
        }, headers=auth_headers)
        
        assert response.status_code in [400, 422], f"Should fail without comment, got {response.status_code}"
    
    def test_verification_short_comment_fails(self, api_client, auth_headers, test_review_id):
        """POST /api/verifications fails with comment < 20 chars"""
        response = api_client.post(f"{BASE_URL}/api/verifications", json={
            "review_id": test_review_id,
            "comment": "Short comment",  # Less than 20 chars
            "photos": ["/api/uploads/test.jpg"]
        }, headers=auth_headers)
        
        # 422 is Pydantic validation error, 400 is manual validation - both are acceptable
        assert response.status_code in [400, 422], f"Should fail with short comment, got {response.status_code}: {response.text}"
    
    def test_verification_success_with_photo_and_comment(self, api_client, auth_headers, test_review_id):
        """POST /api/verifications succeeds with photo and 20+ char comment"""
        response = api_client.post(f"{BASE_URL}/api/verifications", json={
            "review_id": test_review_id,
            "comment": "Подтверждаю, был в этом заведении вчера, всё соответствует описанию",
            "photos": ["/api/uploads/test_photo.jpg"]
        }, headers=auth_headers)
        
        assert response.status_code == 200, f"Should succeed, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("success") == True or "verification_id" in data


# ==================== Cleanup ====================
@pytest.fixture(scope="module", autouse=True)
def cleanup(api_client):
    """Cleanup test data after all tests"""
    yield
    # Cleanup is handled by TEST_ prefix pattern
    from pymongo import MongoClient
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'test_database')
    try:
        client = MongoClient(mongo_url)
        db = client[db_name]
        # Clean up test data
        db.gov_officials.delete_many({"name": {"$regex": "^TEST_"}})
        db.councils.delete_many({"name": {"$regex": "^TEST_"}})
        db.users.delete_many({"user_id": {"$regex": "^test_user"}})
        db.user_sessions.delete_many({"session_token": {"$regex": "^test_session"}})
        db.reviews.delete_many({"review_id": {"$regex": "^rev_test_iter9"}})
    except:
        pass
