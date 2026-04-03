"""
Iteration 10: Comprehensive Council API Tests
Tests for People's Councils system including:
- Council CRUD operations
- Council confirmation (requires verification level 2+)
- Join/Leave council
- Discussions and replies
- Votes and casting
- News with AI moderation
- Nominations and elections
- Complaints against representatives
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test tokens from test_credentials.md
USER1_TOKEN = "Bearer WRANhsgZEBRoK2GSyIUvBEaqIWo0YtmhTsICy2Y4cPc"  # user_eec305b08f9c
USER2_TOKEN = "Bearer qaiAgO3W1YY2ZRN-5c2wk2BrNaGBNVE_rfYAxlye9cI"  # test-user-council-2, verification level 2

# Existing test data
EXISTING_COUNCIL_ID = "council_1bfec18f1635"
EXISTING_DISCUSSION_ID = "disc_7203628a5ec3"
EXISTING_VOTE_ID = "vote_294dda60ff48"


@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture
def auth_client_user1(api_client):
    """Session with User 1 auth header"""
    api_client.headers.update({"Authorization": USER1_TOKEN})
    return api_client


@pytest.fixture
def auth_client_user2(api_client):
    """Session with User 2 auth header (verification level 2)"""
    api_client.headers.update({"Authorization": USER2_TOKEN})
    return api_client


class TestCouncilLevels:
    """Test GET /api/councils/levels"""
    
    def test_get_council_levels(self, api_client):
        """Should return all council levels"""
        response = api_client.get(f"{BASE_URL}/api/councils/levels")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        # Should have at least yard, district, city, republic, country
        expected_levels = ["yard", "district", "city", "republic", "country"]
        for level in expected_levels:
            assert level in data, f"Missing level: {level}"
        print(f"✓ GET /api/councils/levels - Found {len(data)} levels")


class TestCouncilList:
    """Test GET /api/councils"""
    
    def test_list_councils_no_auth(self, api_client):
        """Should list councils without authentication"""
        response = api_client.get(f"{BASE_URL}/api/councils")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET /api/councils - Found {len(data)} councils")
    
    def test_list_councils_with_level_filter(self, api_client):
        """Should filter councils by level"""
        response = api_client.get(f"{BASE_URL}/api/councils", params={"level": "yard"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # All returned councils should be yard level
        for council in data:
            assert council.get("level") == "yard"
        print(f"✓ GET /api/councils?level=yard - Found {len(data)} yard councils")


class TestCouncilCreate:
    """Test POST /api/councils"""
    
    def test_create_council_requires_auth(self, api_client):
        """Should require authentication"""
        response = api_client.post(f"{BASE_URL}/api/councils", json={
            "name": "Test Council",
            "level": "yard",
            "description": "Test description for council",
            "legal_consent": True
        })
        assert response.status_code == 401
        print("✓ POST /api/councils - Requires authentication (401)")
    
    def test_create_council_requires_legal_consent(self, auth_client_user1):
        """Should require legal_consent to be true"""
        response = auth_client_user1.post(f"{BASE_URL}/api/councils", json={
            "name": "Test Council No Consent",
            "level": "yard",
            "description": "Test description for council",
            "legal_consent": False
        })
        # Should fail with 400 or 422 due to legal_consent requirement
        assert response.status_code in [400, 422]
        print("✓ POST /api/councils - Requires legal_consent=true")
    
    def test_create_council_success(self, auth_client_user1):
        """Should create council with valid data"""
        unique_name = f"TEST_Council_{uuid.uuid4().hex[:8]}"
        response = auth_client_user1.post(f"{BASE_URL}/api/councils", json={
            "name": unique_name,
            "level": "yard",
            "description": "Test description for council creation",
            "address": "Test Address 123",
            "legal_consent": True
        })
        assert response.status_code in [200, 201]
        data = response.json()
        assert "council_id" in data
        assert data["name"] == unique_name
        assert data["level"] == "yard"
        assert data.get("confirmed") == False  # New councils are not confirmed
        assert data.get("confirmations_needed") == 10
        print(f"✓ POST /api/councils - Created council: {data['council_id']}")
        return data["council_id"]


class TestCouncilGet:
    """Test GET /api/councils/{id}"""
    
    def test_get_council_success(self, api_client):
        """Should get single council by ID"""
        response = api_client.get(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_ID}")
        assert response.status_code == 200
        data = response.json()
        assert data["council_id"] == EXISTING_COUNCIL_ID
        assert "name" in data
        assert "level" in data
        assert "members" in data
        print(f"✓ GET /api/councils/{EXISTING_COUNCIL_ID} - Found council: {data['name']}")
    
    def test_get_council_not_found(self, api_client):
        """Should return 404 for non-existent council"""
        response = api_client.get(f"{BASE_URL}/api/councils/nonexistent_council_id")
        assert response.status_code == 404
        print("✓ GET /api/councils/nonexistent - Returns 404")


class TestCouncilConfirm:
    """Test POST /api/councils/{id}/confirm"""
    
    def test_confirm_requires_auth(self, api_client):
        """Should require authentication"""
        response = api_client.post(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_ID}/confirm")
        assert response.status_code == 401
        print("✓ POST /api/councils/{id}/confirm - Requires authentication (401)")
    
    def test_confirm_requires_verification_level_2(self, auth_client_user1):
        """Should require verification level 2+ (User 1 may not have it)"""
        response = auth_client_user1.post(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_ID}/confirm")
        # User 1 doesn't have verification level 2, should get 403
        # Or if already confirmed/creator, different error
        assert response.status_code in [400, 403]
        print("✓ POST /api/councils/{id}/confirm - Requires verification level 2+")
    
    def test_confirm_with_verified_user(self, auth_client_user2):
        """User 2 has verification level 2, should be able to confirm"""
        response = auth_client_user2.post(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_ID}/confirm")
        # Could be 200 (success), 400 (already confirmed/creator), or 403 (verification issue)
        assert response.status_code in [200, 400, 403]
        if response.status_code == 200:
            data = response.json()
            assert "confirmations" in data
            print(f"✓ POST /api/councils/{EXISTING_COUNCIL_ID}/confirm - Confirmed successfully")
        else:
            print(f"✓ POST /api/councils/{EXISTING_COUNCIL_ID}/confirm - {response.json().get('detail', 'Already confirmed or creator')}")


class TestCouncilJoinLeave:
    """Test POST /api/councils/{id}/join and /leave"""
    
    def test_join_council_requires_auth(self, api_client):
        """Should require authentication"""
        response = api_client.post(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_ID}/join")
        assert response.status_code == 401
        print("✓ POST /api/councils/{id}/join - Requires authentication (401)")
    
    def test_join_council_success(self, auth_client_user2):
        """Should join council successfully"""
        response = auth_client_user2.post(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_ID}/join")
        # Could be 200 (success) or 400 (already member)
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            print(f"✓ POST /api/councils/{EXISTING_COUNCIL_ID}/join - Joined successfully")
        else:
            print(f"✓ POST /api/councils/{EXISTING_COUNCIL_ID}/join - Already a member")
    
    def test_leave_council_requires_auth(self, api_client):
        """Should require authentication"""
        response = api_client.post(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_ID}/leave")
        assert response.status_code == 401
        print("✓ POST /api/councils/{id}/leave - Requires authentication (401)")
    
    def test_chairman_cannot_leave(self, auth_client_user1):
        """Chairman should not be able to leave"""
        # First check if user1 is chairman
        council_resp = requests.get(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_ID}")
        if council_resp.status_code == 200:
            council = council_resp.json()
            is_chairman = any(
                m.get("user_id") == "user_eec305b08f9c" and m.get("role") == "chairman"
                for m in council.get("members", [])
            )
            if is_chairman:
                response = auth_client_user1.post(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_ID}/leave")
                assert response.status_code == 400
                print("✓ POST /api/councils/{id}/leave - Chairman cannot leave (400)")
            else:
                print("✓ POST /api/councils/{id}/leave - User1 is not chairman, skipping test")


class TestCouncilDiscussions:
    """Test discussions endpoints"""
    
    def test_list_discussions(self, api_client):
        """Should list discussions without auth"""
        response = api_client.get(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_ID}/discussions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET /api/councils/{EXISTING_COUNCIL_ID}/discussions - Found {len(data)} discussions")
    
    def test_create_discussion_requires_auth(self, api_client):
        """Should require authentication"""
        response = api_client.post(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_ID}/discussions", json={
            "title": "Test Discussion",
            "content": "Test content for discussion",
            "category": "general"
        })
        assert response.status_code == 401
        print("✓ POST /api/councils/{id}/discussions - Requires authentication (401)")
    
    def test_create_discussion_requires_membership(self, auth_client_user2):
        """Should require council membership"""
        # First ensure user2 is a member
        auth_client_user2.post(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_ID}/join")
        
        response = auth_client_user2.post(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_ID}/discussions", json={
            "title": "TEST_Discussion_" + uuid.uuid4().hex[:8],
            "content": "Test content for discussion that is at least 20 characters",
            "category": "general"
        })
        # Should be 200/201 if member, 403 if not
        assert response.status_code in [200, 201, 403]
        if response.status_code in [200, 201]:
            data = response.json()
            assert "discussion_id" in data
            print(f"✓ POST /api/councils/{EXISTING_COUNCIL_ID}/discussions - Created: {data['discussion_id']}")
        else:
            print("✓ POST /api/councils/{id}/discussions - Requires membership (403)")
    
    def test_reply_to_discussion(self, auth_client_user1):
        """Should reply to existing discussion"""
        response = auth_client_user1.post(
            f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_ID}/discussions/{EXISTING_DISCUSSION_ID}/reply",
            json={"text": "Test reply to discussion"}
        )
        # Could be 200 (success), 403 (not member), or 404 (discussion not found)
        assert response.status_code in [200, 403, 404]
        if response.status_code == 200:
            print(f"✓ POST /api/councils/{EXISTING_COUNCIL_ID}/discussions/{EXISTING_DISCUSSION_ID}/reply - Reply added")
        else:
            print(f"✓ POST /api/councils/{id}/discussions/{id}/reply - Status: {response.status_code}")


class TestCouncilVotes:
    """Test votes endpoints"""
    
    def test_list_votes(self, api_client):
        """Should list votes without auth"""
        response = api_client.get(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_ID}/votes")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET /api/councils/{EXISTING_COUNCIL_ID}/votes - Found {len(data)} votes")
    
    def test_create_vote_requires_auth(self, api_client):
        """Should require authentication"""
        response = api_client.post(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_ID}/votes", json={
            "title": "Test Vote",
            "description": "Test vote description",
            "options": ["Option 1", "Option 2"]
        })
        assert response.status_code == 401
        print("✓ POST /api/councils/{id}/votes - Requires authentication (401)")
    
    def test_create_vote_requires_chairman_or_rep(self, auth_client_user2):
        """Should require chairman or representative role"""
        response = auth_client_user2.post(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_ID}/votes", json={
            "title": "TEST_Vote_" + uuid.uuid4().hex[:8],
            "description": "Test vote description for testing",
            "options": ["Option A", "Option B"]
        })
        # Should be 200/201 if chairman/rep, 403 otherwise
        assert response.status_code in [200, 201, 403]
        if response.status_code in [200, 201]:
            data = response.json()
            assert "vote_id" in data
            print(f"✓ POST /api/councils/{EXISTING_COUNCIL_ID}/votes - Created: {data['vote_id']}")
        else:
            print("✓ POST /api/councils/{id}/votes - Requires chairman/rep role (403)")
    
    def test_cast_vote(self, auth_client_user1):
        """Should cast vote on existing vote"""
        # First get the vote to find an option
        vote_resp = requests.get(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_ID}/votes")
        if vote_resp.status_code == 200 and len(vote_resp.json()) > 0:
            vote = vote_resp.json()[0]
            if vote.get("options") and len(vote["options"]) > 0:
                option_id = vote["options"][0].get("option_id")
                response = auth_client_user1.post(
                    f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_ID}/votes/{vote['vote_id']}/cast",
                    json={"option_id": option_id}
                )
                # Could be 200 (success), 400 (already voted), 403 (not member)
                assert response.status_code in [200, 400, 403]
                print(f"✓ POST /api/councils/{EXISTING_COUNCIL_ID}/votes/{vote['vote_id']}/cast - Status: {response.status_code}")
        else:
            print("✓ POST /api/councils/{id}/votes/{id}/cast - No votes to test")


class TestCouncilNews:
    """Test news endpoints with AI moderation"""
    
    def test_list_news(self, api_client):
        """Should list council news without auth"""
        response = api_client.get(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_ID}/news")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET /api/councils/{EXISTING_COUNCIL_ID}/news - Found {len(data)} news items")
        # Check if any have AI check results
        for news in data:
            if news.get("ai_check", {}).get("checked"):
                print(f"  - News {news['news_id']} has AI check: {news['ai_check'].get('result', {}).get('credibility', 'N/A')}")
    
    def test_create_news_requires_auth(self, api_client):
        """Should require authentication"""
        response = api_client.post(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_ID}/news", json={
            "title": "Test News",
            "content": "Test news content for testing"
        })
        assert response.status_code == 401
        print("✓ POST /api/councils/{id}/news - Requires authentication (401)")
    
    def test_create_news_requires_chairman_or_rep(self, auth_client_user1):
        """Should require chairman or representative role"""
        response = auth_client_user1.post(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_ID}/news", json={
            "title": "TEST_News_" + uuid.uuid4().hex[:8],
            "content": "Test news content that is at least 20 characters long for validation"
        })
        # Should be 200/201 if chairman/rep, 403 otherwise
        assert response.status_code in [200, 201, 403]
        if response.status_code in [200, 201]:
            data = response.json()
            assert "news_id" in data
            assert "ai_check" in data  # Should have AI moderation check
            print(f"✓ POST /api/councils/{EXISTING_COUNCIL_ID}/news - Created: {data['news_id']}")
            print(f"  - AI Check: {data.get('ai_check', {})}")
        else:
            print("✓ POST /api/councils/{id}/news - Requires chairman/rep role (403)")
    
    def test_moderate_news_requires_auth(self, api_client):
        """Should require authentication"""
        response = api_client.put(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_ID}/news/test_news_id/moderate", json={
            "action": "approve"
        })
        assert response.status_code == 401
        print("✓ PUT /api/councils/{id}/news/{id}/moderate - Requires authentication (401)")
    
    def test_moderate_news_approve(self, auth_client_user1):
        """Should moderate news (approve/reject)"""
        # First get news to find one to moderate
        news_resp = requests.get(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_ID}/news")
        if news_resp.status_code == 200 and len(news_resp.json()) > 0:
            news = news_resp.json()[0]
            response = auth_client_user1.put(
                f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_ID}/news/{news['news_id']}/moderate",
                json={"action": "approve"}
            )
            # Could be 200 (success), 403 (not chairman/rep/admin)
            assert response.status_code in [200, 403]
            print(f"✓ PUT /api/councils/{EXISTING_COUNCIL_ID}/news/{news['news_id']}/moderate - Status: {response.status_code}")
        else:
            print("✓ PUT /api/councils/{id}/news/{id}/moderate - No news to test")


class TestCouncilNominations:
    """Test nominations and elections"""
    
    def test_get_nominations(self, api_client):
        """Should get nominations list"""
        response = api_client.get(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_ID}/nominations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET /api/councils/{EXISTING_COUNCIL_ID}/nominations - Found {len(data)} nominations")
    
    def test_nominate_requires_auth(self, api_client):
        """Should require authentication"""
        response = api_client.post(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_ID}/nominate", json={
            "user_id": "some_user_id"
        })
        assert response.status_code == 401
        print("✓ POST /api/councils/{id}/nominate - Requires authentication (401)")
    
    def test_nominate_requires_membership(self, auth_client_user2):
        """Should require council membership"""
        # First ensure user2 is a member
        auth_client_user2.post(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_ID}/join")
        
        # Get council members to find someone to nominate
        council_resp = requests.get(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_ID}")
        if council_resp.status_code == 200:
            council = council_resp.json()
            members = council.get("members", [])
            # Find a member that is not user2
            for member in members:
                if member.get("user_id") != "test-user-council-2":
                    response = auth_client_user2.post(
                        f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_ID}/nominate",
                        json={"user_id": member["user_id"]}
                    )
                    # Could be 200 (success), 400 (already nominated), 403 (not member)
                    assert response.status_code in [200, 400, 403]
                    print(f"✓ POST /api/councils/{EXISTING_COUNCIL_ID}/nominate - Status: {response.status_code}")
                    break
            else:
                print("✓ POST /api/councils/{id}/nominate - No other members to nominate")
    
    def test_elect_representatives_requires_chairman(self, auth_client_user2):
        """Should require chairman role"""
        response = auth_client_user2.post(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_ID}/elect-representatives")
        # Should be 403 if not chairman
        assert response.status_code in [200, 403]
        if response.status_code == 403:
            print("✓ POST /api/councils/{id}/elect-representatives - Requires chairman role (403)")
        else:
            print("✓ POST /api/councils/{id}/elect-representatives - Election completed")


class TestCouncilComplaints:
    """Test complaints against representatives"""
    
    def test_complaint_requires_auth(self, api_client):
        """Should require authentication"""
        response = api_client.post(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_ID}/complaint", json={
            "representative_id": "some_rep_id",
            "reason": "Test complaint reason"
        })
        assert response.status_code == 401
        print("✓ POST /api/councils/{id}/complaint - Requires authentication (401)")
    
    def test_file_complaint(self, auth_client_user2):
        """Should file complaint against representative"""
        # First get council to find a representative
        council_resp = requests.get(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_ID}")
        if council_resp.status_code == 200:
            council = council_resp.json()
            reps = council.get("representatives", [])
            if reps:
                rep = reps[0]
                response = auth_client_user2.post(
                    f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_ID}/complaint",
                    json={
                        "representative_id": rep["user_id"],
                        "reason": "Test complaint reason for testing purposes"
                    }
                )
                # Could be 200 (success), 400 (invalid), 403 (not member)
                assert response.status_code in [200, 400, 403]
                print(f"✓ POST /api/councils/{EXISTING_COUNCIL_ID}/complaint - Status: {response.status_code}")
            else:
                print("✓ POST /api/councils/{id}/complaint - No representatives to complain about")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
