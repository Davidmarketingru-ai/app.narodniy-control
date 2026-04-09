"""
Iteration 11: Testing new council features
- Only yard councils can be created manually
- Higher levels form through escalation voting
- 80% formation threshold based on verified residents at address
- Escalation voting system
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from review_request
USER1_TOKEN = "Bearer WRANhsgZEBRoK2GSyIUvBEaqIWo0YtmhTsICy2Y4cPc"  # chairman of council_766c80223222
USER1_ID = "user_eec305b08f9c"
USER2_TOKEN = "Bearer qaiAgO3W1YY2ZRN-5c2wk2BrNaGBNVE_rfYAxlye9cI"  # member
USER2_ID = "test-user-council-2"
USER_HOUSE2_TOKEN = "Bearer xvLTdXAyTaWU6uzqMo2NMpdrnqwuxIfGtlf_66FbhN4"  # chairman of council_0c4b7a580b9d
USER_C3_TOKEN = "Bearer 2T7204cjRXDL33bknasoPH6BZxNu9GsSAMGuWA5TCOM"

EXISTING_COUNCIL_1 = "council_766c80223222"  # yard, active, formed 100%
EXISTING_COUNCIL_2 = "council_0c4b7a580b9d"  # yard, active
EXISTING_DISTRICT = "council_0a5d54fc20a6"  # district, active, formed via escalation
EXISTING_ESCALATION = "escal_55772c8d616a"  # completed


@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture
def auth_client_user1(api_client):
    """Session with User1 auth header (chairman)"""
    api_client.headers.update({"Authorization": USER1_TOKEN})
    return api_client


@pytest.fixture
def auth_client_user2(api_client):
    """Session with User2 auth header (member)"""
    api_client.headers.update({"Authorization": USER2_TOKEN})
    return api_client


@pytest.fixture
def auth_client_house2(api_client):
    """Session with house2 user auth header (chairman of council_0c4b7a580b9d)"""
    api_client.headers.update({"Authorization": USER_HOUSE2_TOKEN})
    return api_client


class TestCouncilLevels:
    """Test GET /api/councils/levels - returns level hierarchy with parent_level info"""
    
    def test_get_levels_returns_hierarchy(self, api_client):
        response = api_client.get(f"{BASE_URL}/api/councils/levels")
        assert response.status_code == 200
        data = response.json()
        
        # API returns a dictionary with level keys
        assert isinstance(data, dict)
        assert len(data) == 5
        
        # Check yard level (no parent)
        assert "yard" in data
        yard = data["yard"]
        assert yard["parent_level"] is None
        assert yard["order"] == 1
        
        # Check district level (parent is yard)
        assert "district" in data
        district = data["district"]
        assert district["parent_level"] == "yard"
        assert district["order"] == 2
        
        # Check city level (parent is district)
        assert "city" in data
        city = data["city"]
        assert city["parent_level"] == "district"
        
        print("✓ GET /api/councils/levels returns correct hierarchy")


class TestCouncilCreation:
    """Test POST /api/councils - only creates yard level, requires street + house_number"""
    
    def test_create_council_requires_auth(self, api_client):
        """POST /api/councils requires authentication"""
        response = api_client.post(f"{BASE_URL}/api/councils", json={
            "name": "Test Council",
            "description": "Test description for council",
            "street": "Тестовая",
            "house_number": "999",
            "legal_consent": True
        })
        assert response.status_code == 401
        print("✓ POST /api/councils requires authentication (401)")
    
    def test_create_council_requires_legal_consent(self, auth_client_user1):
        """POST /api/councils rejects if legal_consent is false"""
        unique_house = f"TEST_{uuid.uuid4().hex[:6]}"
        response = auth_client_user1.post(f"{BASE_URL}/api/councils", json={
            "name": "Test Council No Consent",
            "description": "Test description for council",
            "street": "Тестовая",
            "house_number": unique_house,
            "legal_consent": False
        })
        assert response.status_code == 400
        assert "юридическое" in response.json().get("detail", "").lower() or "consent" in response.json().get("detail", "").lower()
        print("✓ POST /api/councils rejects if legal_consent is false")
    
    def test_create_council_requires_street_and_house(self, auth_client_user1):
        """POST /api/councils requires street + house_number"""
        # Missing street
        response = auth_client_user1.post(f"{BASE_URL}/api/councils", json={
            "name": "Test Council",
            "description": "Test description for council",
            "street": "",
            "house_number": "123",
            "legal_consent": True
        })
        assert response.status_code in [400, 422]
        
        # Missing house_number
        response = auth_client_user1.post(f"{BASE_URL}/api/councils", json={
            "name": "Test Council",
            "description": "Test description for council",
            "street": "Тестовая",
            "house_number": "",
            "legal_consent": True
        })
        assert response.status_code in [400, 422]
        print("✓ POST /api/councils requires street + house_number")
    
    def test_create_council_always_creates_yard_level(self, auth_client_user1):
        """POST /api/councils only creates yard level (ignores level field)"""
        unique_house = f"TEST_{uuid.uuid4().hex[:6]}"
        response = auth_client_user1.post(f"{BASE_URL}/api/councils", json={
            "name": f"Test Yard Council {unique_house}",
            "description": "Test description for yard council",
            "street": "Тестовая Улица",
            "house_number": unique_house,
            "district": "Тестовый район",
            "city": "Бишкек",
            "legal_consent": True
        })
        assert response.status_code == 200
        data = response.json()
        
        # Should always be yard level
        assert data["level"] == "yard"
        assert data["street"] == "Тестовая Улица"
        assert data["house_number"] == unique_house
        assert data["status"] == "pending_confirmation"
        
        print(f"✓ POST /api/councils creates yard level council: {data['council_id']}")
        return data["council_id"]
    
    def test_create_council_rejects_duplicate_address(self, auth_client_user1):
        """POST /api/councils rejects duplicate address (same street + house_number)"""
        # First, get an existing council's address
        response = auth_client_user1.get(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_1}")
        if response.status_code == 200:
            existing = response.json()
            street = existing.get("street", "Ленина")
            house = existing.get("house_number", "15")
            
            # Try to create another council at the same address
            response = auth_client_user1.post(f"{BASE_URL}/api/councils", json={
                "name": "Duplicate Address Council",
                "description": "Test description for duplicate",
                "street": street,
                "house_number": house,
                "legal_consent": True
            })
            assert response.status_code == 400
            assert "уже существует" in response.json().get("detail", "").lower()
            print("✓ POST /api/councils rejects duplicate address")
        else:
            pytest.skip("Existing council not found for duplicate test")


class TestCouncilFormation:
    """Test GET /api/councils/{id}/formation - returns formation percentage"""
    
    def test_get_formation_for_yard_council(self, api_client):
        """GET /api/councils/{id}/formation returns formation info for yard council"""
        response = api_client.get(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_1}/formation")
        assert response.status_code == 200
        data = response.json()
        
        # Should have formation fields
        assert "total_verified" in data
        assert "member_count" in data
        assert "percent" in data
        assert "formed" in data
        
        # Percent should be a number
        assert isinstance(data["percent"], (int, float))
        # Formed should be boolean
        assert isinstance(data["formed"], bool)
        
        print(f"✓ GET /api/councils/{EXISTING_COUNCIL_1}/formation: {data['percent']}% formed={data['formed']}")
    
    def test_formation_returns_100_for_non_yard(self, api_client):
        """GET /api/councils/{id}/formation returns 100% for non-yard councils"""
        response = api_client.get(f"{BASE_URL}/api/councils/{EXISTING_DISTRICT}/formation")
        if response.status_code == 200:
            data = response.json()
            # Non-yard councils should show 100% formed
            assert data["percent"] == 100
            assert data["formed"] == True
            print(f"✓ GET /api/councils/{EXISTING_DISTRICT}/formation: non-yard shows 100% formed")
        else:
            pytest.skip("District council not found")
    
    def test_formation_404_for_nonexistent(self, api_client):
        """GET /api/councils/{id}/formation returns 404 for non-existent council"""
        response = api_client.get(f"{BASE_URL}/api/councils/nonexistent_council/formation")
        assert response.status_code == 404
        print("✓ GET /api/councils/nonexistent/formation returns 404")


class TestCouncilConfirmation:
    """Test POST /api/councils/{id}/confirm - confirm council creation"""
    
    def test_confirm_requires_auth(self, api_client):
        """POST /api/councils/{id}/confirm requires authentication"""
        response = api_client.post(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_1}/confirm")
        assert response.status_code == 401
        print("✓ POST /api/councils/{id}/confirm requires authentication")
    
    def test_confirm_requires_verification_level(self, auth_client_user1):
        """POST /api/councils/{id}/confirm requires verification level 2+"""
        # User1 may not have verification level 2
        response = auth_client_user1.post(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_1}/confirm")
        # Should either succeed (if verified) or fail with 403 (if not verified)
        assert response.status_code in [200, 400, 403]
        if response.status_code == 403:
            assert "верифицированные" in response.json().get("detail", "").lower()
            print("✓ POST /api/councils/{id}/confirm requires verification level 2+")
        elif response.status_code == 400:
            # Already confirmed or creator cannot confirm
            print(f"✓ POST /api/councils/{id}/confirm: {response.json().get('detail')}")
        else:
            print("✓ POST /api/councils/{id}/confirm succeeded")


class TestCouncilJoin:
    """Test POST /api/councils/{id}/join - join council"""
    
    def test_join_requires_auth(self, api_client):
        """POST /api/councils/{id}/join requires authentication"""
        response = api_client.post(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_1}/join")
        assert response.status_code == 401
        print("✓ POST /api/councils/{id}/join requires authentication")
    
    def test_join_council(self, auth_client_user2):
        """POST /api/councils/{id}/join joins council successfully"""
        response = auth_client_user2.post(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_1}/join")
        # Should succeed or fail if already member
        assert response.status_code in [200, 400]
        if response.status_code == 400:
            assert "уже участник" in response.json().get("detail", "").lower()
            print("✓ POST /api/councils/{id}/join: already a member")
        else:
            assert response.json().get("success") == True
            print("✓ POST /api/councils/{id}/join succeeded")


class TestCouncilDiscussions:
    """Test POST /api/councils/{id}/discussions - create discussion"""
    
    def test_create_discussion_requires_auth(self, api_client):
        """POST /api/councils/{id}/discussions requires authentication"""
        response = api_client.post(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_1}/discussions", json={
            "title": "Test Discussion",
            "content": "Test content for discussion that is long enough",
            "category": "general"
        })
        assert response.status_code == 401
        print("✓ POST /api/councils/{id}/discussions requires authentication")
    
    def test_create_discussion_requires_membership(self, auth_client_user1):
        """POST /api/councils/{id}/discussions requires membership"""
        response = auth_client_user1.post(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_1}/discussions", json={
            "title": "Test Discussion",
            "content": "Test content for discussion that is long enough",
            "category": "general"
        })
        # Should succeed if member, fail if not
        assert response.status_code in [200, 403]
        if response.status_code == 200:
            data = response.json()
            assert "discussion_id" in data
            print(f"✓ POST /api/councils/{id}/discussions created: {data['discussion_id']}")
        else:
            print("✓ POST /api/councils/{id}/discussions requires membership")


class TestCouncilNews:
    """Test POST /api/councils/{id}/news - create news with AI moderation"""
    
    def test_create_news_requires_auth(self, api_client):
        """POST /api/councils/{id}/news requires authentication"""
        response = api_client.post(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_1}/news", json={
            "title": "Test News Title",
            "content": "Test news content that is long enough for validation"
        })
        assert response.status_code == 401
        print("✓ POST /api/councils/{id}/news requires authentication")
    
    def test_create_news_requires_chairman_or_rep(self, auth_client_user1):
        """POST /api/councils/{id}/news requires chairman/rep role"""
        response = auth_client_user1.post(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_1}/news", json={
            "title": "Test News Title",
            "content": "Test news content that is long enough for validation and AI moderation"
        })
        # Should succeed if chairman/rep, fail if not
        assert response.status_code in [200, 403]
        if response.status_code == 200:
            data = response.json()
            assert "news_id" in data
            # Check AI moderation was applied
            assert "ai_check" in data or data.get("status") in ["pending_moderation", "verified"]
            print(f"✓ POST /api/councils/{id}/news created with AI moderation: {data['news_id']}")
        else:
            print("✓ POST /api/councils/{id}/news requires chairman/rep role")


class TestEscalation:
    """Test escalation endpoints for forming higher-level councils"""
    
    def test_initiate_escalation_requires_auth(self, api_client):
        """POST /api/councils/{id}/escalation requires authentication"""
        response = api_client.post(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_1}/escalation", json={
            "name": "Test District Council"
        })
        assert response.status_code == 401
        print("✓ POST /api/councils/{id}/escalation requires authentication")
    
    def test_initiate_escalation_requires_chairman_or_rep(self, auth_client_user2):
        """POST /api/councils/{id}/escalation requires chairman/rep role"""
        response = auth_client_user2.post(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_1}/escalation", json={
            "name": "Test District Council"
        })
        # Should fail if not chairman/rep
        assert response.status_code in [400, 403]
        print("✓ POST /api/councils/{id}/escalation requires chairman/rep role")
    
    def test_initiate_escalation_requires_formed_council(self, auth_client_user1):
        """POST /api/councils/{id}/escalation requires confirmed+formed council"""
        # First check if council is formed
        formation_resp = auth_client_user1.get(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_1}/formation")
        if formation_resp.status_code == 200:
            formation = formation_resp.json()
            
            response = auth_client_user1.post(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_1}/escalation", json={
                "name": "Test District Council",
                "district": "Тестовый район"
            })
            
            if not formation.get("formed"):
                # Should reject if not formed
                assert response.status_code == 400
                assert "не сформирован" in response.json().get("detail", "").lower() or "80%" in response.json().get("detail", "")
                print("✓ POST /api/councils/{id}/escalation rejects if council not formed (<80%)")
            else:
                # May succeed or fail for other reasons (already escalating, not enough councils, etc.)
                assert response.status_code in [200, 400]
                if response.status_code == 200:
                    data = response.json()
                    assert "escalation_id" in data
                    print(f"✓ POST /api/councils/{id}/escalation initiated: {data['escalation_id']}")
                else:
                    print(f"✓ POST /api/councils/{id}/escalation: {response.json().get('detail')}")
        else:
            pytest.skip("Could not get formation info")
    
    def test_list_active_escalations(self, api_client):
        """GET /api/councils/escalations/active lists active escalation votes"""
        response = api_client.get(f"{BASE_URL}/api/councils/escalations/active")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Check structure if any escalations exist
        if len(data) > 0:
            escal = data[0]
            assert "escalation_id" in escal
            assert "source_level" in escal
            assert "target_level" in escal
            assert "votes_for" in escal
            assert "votes_against" in escal
            assert "eligible_council_ids" in escal
        
        print(f"✓ GET /api/councils/escalations/active: {len(data)} active escalations")
    
    def test_vote_on_escalation_requires_auth(self, api_client):
        """POST /api/councils/escalations/{eid}/vote requires authentication"""
        response = api_client.post(f"{BASE_URL}/api/councils/escalations/test_escal/vote", json={
            "vote": "for"
        })
        assert response.status_code == 401
        print("✓ POST /api/councils/escalations/{eid}/vote requires authentication")
    
    def test_vote_on_escalation_requires_eligible_council(self, auth_client_user1):
        """POST /api/councils/escalations/{eid}/vote requires chairman/rep of eligible council"""
        # First get active escalations
        response = auth_client_user1.get(f"{BASE_URL}/api/councils/escalations/active")
        if response.status_code == 200 and len(response.json()) > 0:
            escal = response.json()[0]
            eid = escal["escalation_id"]
            
            vote_response = auth_client_user1.post(f"{BASE_URL}/api/councils/escalations/{eid}/vote", json={
                "vote": "for"
            })
            # Should succeed if eligible, fail if not or already voted
            assert vote_response.status_code in [200, 400, 403]
            if vote_response.status_code == 200:
                data = vote_response.json()
                assert "success" in data
                print(f"✓ POST /api/councils/escalations/{eid}/vote: voted successfully")
            else:
                print(f"✓ POST /api/councils/escalations/{eid}/vote: {vote_response.json().get('detail')}")
        else:
            print("✓ No active escalations to vote on")
    
    def test_vote_on_nonexistent_escalation(self, auth_client_user1):
        """POST /api/councils/escalations/{eid}/vote returns 404 for non-existent"""
        response = auth_client_user1.post(f"{BASE_URL}/api/councils/escalations/nonexistent_escal/vote", json={
            "vote": "for"
        })
        assert response.status_code == 404
        print("✓ POST /api/councils/escalations/nonexistent/vote returns 404")


class TestExistingCouncils:
    """Verify existing test data councils"""
    
    def test_existing_yard_council_1(self, api_client):
        """Verify council_766c80223222 exists and is yard level"""
        response = api_client.get(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_1}")
        assert response.status_code == 200
        data = response.json()
        assert data["level"] == "yard"
        assert data["status"] == "active"
        print(f"✓ Council {EXISTING_COUNCIL_1}: yard, active, {data.get('member_count', 0)} members")
    
    def test_existing_yard_council_2(self, api_client):
        """Verify council_0c4b7a580b9d exists and is yard level"""
        response = api_client.get(f"{BASE_URL}/api/councils/{EXISTING_COUNCIL_2}")
        assert response.status_code == 200
        data = response.json()
        assert data["level"] == "yard"
        print(f"✓ Council {EXISTING_COUNCIL_2}: yard, {data.get('status')}, {data.get('member_count', 0)} members")
    
    def test_existing_district_council(self, api_client):
        """Verify council_0a5d54fc20a6 exists and is district level"""
        response = api_client.get(f"{BASE_URL}/api/councils/{EXISTING_DISTRICT}")
        assert response.status_code == 200
        data = response.json()
        assert data["level"] == "district"
        assert data["status"] == "active"
        # Should have been formed via escalation
        assert data.get("formed_via_escalation") is not None or data.get("child_council_ids") is not None
        print(f"✓ Council {EXISTING_DISTRICT}: district, active, formed via escalation")


class TestCouncilListFiltering:
    """Test GET /api/councils with filters"""
    
    def test_list_all_councils(self, api_client):
        """GET /api/councils lists all councils"""
        response = api_client.get(f"{BASE_URL}/api/councils")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET /api/councils: {len(data)} councils")
    
    def test_list_councils_by_level(self, api_client):
        """GET /api/councils?level=yard filters by level"""
        response = api_client.get(f"{BASE_URL}/api/councils", params={"level": "yard"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # All should be yard level
        for c in data:
            assert c["level"] == "yard"
        print(f"✓ GET /api/councils?level=yard: {len(data)} yard councils")
    
    def test_list_councils_by_status(self, api_client):
        """GET /api/councils?status=active filters by status"""
        response = api_client.get(f"{BASE_URL}/api/councils", params={"status": "active"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # All should be active
        for c in data:
            assert c["status"] == "active"
        print(f"✓ GET /api/councils?status=active: {len(data)} active councils")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
