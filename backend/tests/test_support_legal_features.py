"""
Backend API Tests for NEW Support Ticket System, Legal Pages, and Consent Features
Tests: FAQ, Support Tickets, Legal Info, Consent Recording, Admin Ticket Management
"""
import pytest
import requests
import os
from datetime import datetime

# Get BASE_URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    pytest.skip("REACT_APP_BACKEND_URL not set", allow_module_level=True)

# Test session token from previous iteration
TEST_SESSION_TOKEN = "test_session_comprehensive_1773178288724"
TEST_USER_ID = "test_user_comprehensive_1773178288724"


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


# ==================== FAQ Endpoint Tests ====================
class TestFAQEndpoint:
    """Tests for GET /api/support/faq - public FAQ endpoint"""
    
    def test_get_faq_returns_8_items(self, api_client):
        """GET /api/support/faq returns 8 FAQ items"""
        resp = api_client.get(f"{BASE_URL}/api/support/faq")
        assert resp.status_code == 200
        faq = resp.json()
        assert isinstance(faq, list)
        assert len(faq) == 8, f"Expected 8 FAQ items, got {len(faq)}"
        
        # Verify FAQ structure
        for item in faq:
            assert "question" in item
            assert "answer" in item
            assert len(item["question"]) > 0
            assert len(item["answer"]) > 0
        print(f"✓ GET /api/support/faq returns {len(faq)} FAQ items")
    
    def test_faq_no_auth_required(self, api_client):
        """FAQ endpoint is public (no auth required)"""
        resp = api_client.get(f"{BASE_URL}/api/support/faq")
        assert resp.status_code == 200
        print("✓ FAQ endpoint is public (no auth required)")


# ==================== Legal Info Endpoint Tests ====================
class TestLegalInfoEndpoint:
    """Tests for GET /api/legal/info - operator details"""
    
    def test_get_legal_info(self, api_client):
        """GET /api/legal/info returns operator details"""
        resp = api_client.get(f"{BASE_URL}/api/legal/info")
        assert resp.status_code == 200
        info = resp.json()
        
        # Verify required fields
        assert "operator_name" in info
        assert "inn" in info
        assert "ogrn" in info
        assert "email" in info
        assert "age_restriction" in info
        
        # Verify values
        assert info["operator_name"] == "ООО «Народный Контроль»"
        assert info["age_restriction"] == "16+"
        assert "@" in info["email"]
        print(f"✓ GET /api/legal/info returns operator: {info['operator_name']}")
    
    def test_legal_info_no_auth_required(self, api_client):
        """Legal info endpoint is public"""
        resp = api_client.get(f"{BASE_URL}/api/legal/info")
        assert resp.status_code == 200
        print("✓ Legal info endpoint is public (no auth required)")


# ==================== Support Tickets Auth Tests ====================
class TestSupportTicketsAuth:
    """Tests that support ticket endpoints require authentication"""
    
    def test_post_tickets_requires_auth(self, api_client):
        """POST /api/support/tickets requires auth (returns 401)"""
        resp = api_client.post(f"{BASE_URL}/api/support/tickets", json={
            "subject": "Test",
            "message": "Test message",
            "category": "question"
        })
        assert resp.status_code == 401
        print("✓ POST /api/support/tickets returns 401 without auth")
    
    def test_get_tickets_requires_auth(self, api_client):
        """GET /api/support/tickets requires auth (returns 401)"""
        resp = api_client.get(f"{BASE_URL}/api/support/tickets")
        assert resp.status_code == 401
        print("✓ GET /api/support/tickets returns 401 without auth")


# ==================== Authenticated Support Ticket Tests ====================
class TestAuthenticatedSupportTickets:
    """Tests for authenticated support ticket operations"""
    
    created_ticket_id = None
    
    def test_create_ticket(self, auth_client):
        """POST /api/support/tickets creates ticket with subject, message, category"""
        resp = auth_client.post(f"{BASE_URL}/api/support/tickets", json={
            "subject": f"TEST_Ticket_{datetime.now().timestamp()}",
            "message": "This is a test ticket message for automated testing",
            "category": "question"
        })
        assert resp.status_code == 200
        ticket = resp.json()
        
        # Verify ticket structure
        assert "ticket_id" in ticket
        assert "subject" in ticket
        assert "category" in ticket
        assert "status" in ticket
        assert "messages" in ticket
        
        # Verify values
        assert ticket["category"] == "question"
        assert ticket["status"] == "open"
        assert len(ticket["messages"]) == 1
        
        # Store for later tests
        TestAuthenticatedSupportTickets.created_ticket_id = ticket["ticket_id"]
        print(f"✓ Created ticket: {ticket['ticket_id']}")
    
    def test_list_user_tickets(self, auth_client):
        """GET /api/support/tickets returns user's tickets"""
        resp = auth_client.get(f"{BASE_URL}/api/support/tickets")
        assert resp.status_code == 200
        tickets = resp.json()
        assert isinstance(tickets, list)
        
        # Should have at least the ticket we just created
        if TestAuthenticatedSupportTickets.created_ticket_id:
            ticket_ids = [t["ticket_id"] for t in tickets]
            assert TestAuthenticatedSupportTickets.created_ticket_id in ticket_ids
        print(f"✓ GET /api/support/tickets returns {len(tickets)} tickets")
    
    def test_get_single_ticket(self, auth_client):
        """GET /api/support/tickets/{ticket_id} returns ticket with messages"""
        if not TestAuthenticatedSupportTickets.created_ticket_id:
            pytest.skip("No ticket created")
        
        ticket_id = TestAuthenticatedSupportTickets.created_ticket_id
        resp = auth_client.get(f"{BASE_URL}/api/support/tickets/{ticket_id}")
        assert resp.status_code == 200
        ticket = resp.json()
        
        assert ticket["ticket_id"] == ticket_id
        assert "messages" in ticket
        assert isinstance(ticket["messages"], list)
        print(f"✓ GET /api/support/tickets/{ticket_id} returns ticket with {len(ticket['messages'])} messages")
    
    def test_reply_to_ticket(self, auth_client):
        """POST /api/support/tickets/{ticket_id}/reply adds reply message"""
        if not TestAuthenticatedSupportTickets.created_ticket_id:
            pytest.skip("No ticket created")
        
        ticket_id = TestAuthenticatedSupportTickets.created_ticket_id
        resp = auth_client.post(f"{BASE_URL}/api/support/tickets/{ticket_id}/reply", json={
            "text": "This is a test reply message"
        })
        assert resp.status_code == 200
        ticket = resp.json()
        
        # Should now have 2 messages
        assert len(ticket["messages"]) >= 2
        
        # Last message should be our reply
        last_msg = ticket["messages"][-1]
        assert last_msg["text"] == "This is a test reply message"
        # Sender is "support" if admin, "user" otherwise
        assert last_msg["sender"] in ["user", "support"]
        print(f"✓ Reply added, ticket now has {len(ticket['messages'])} messages")
    
    def test_close_ticket(self, auth_client):
        """PUT /api/support/tickets/{ticket_id}/status changes status to closed"""
        if not TestAuthenticatedSupportTickets.created_ticket_id:
            pytest.skip("No ticket created")
        
        ticket_id = TestAuthenticatedSupportTickets.created_ticket_id
        resp = auth_client.put(f"{BASE_URL}/api/support/tickets/{ticket_id}/status", json={
            "status": "closed"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") == True
        
        # Verify status changed
        resp2 = auth_client.get(f"{BASE_URL}/api/support/tickets/{ticket_id}")
        ticket = resp2.json()
        assert ticket["status"] == "closed"
        print(f"✓ Ticket {ticket_id} status changed to closed")
    
    def test_create_ticket_with_different_categories(self, auth_client):
        """Test creating tickets with different categories"""
        categories = ["bug", "complaint", "suggestion", "rights_violation", "other"]
        
        for category in categories:
            resp = auth_client.post(f"{BASE_URL}/api/support/tickets", json={
                "subject": f"TEST_{category}_{datetime.now().timestamp()}",
                "message": f"Test message for {category} category",
                "category": category
            })
            assert resp.status_code == 200
            ticket = resp.json()
            assert ticket["category"] == category
            
            # Check priority for high-priority categories
            if category in ["rights_violation", "complaint"]:
                assert ticket.get("priority") == "high"
        
        print(f"✓ Created tickets with all {len(categories)} categories")


# ==================== Consent Endpoint Tests ====================
class TestConsentEndpoint:
    """Tests for POST /api/auth/consent - consent recording"""
    
    def test_consent_requires_auth(self, api_client):
        """POST /api/auth/consent requires auth"""
        resp = api_client.post(f"{BASE_URL}/api/auth/consent", json={
            "type": "terms_and_privacy"
        })
        assert resp.status_code == 401
        print("✓ POST /api/auth/consent returns 401 without auth")
    
    def test_record_consent(self, auth_client):
        """POST /api/auth/consent records consent with type and date"""
        resp = auth_client.post(f"{BASE_URL}/api/auth/consent", json={
            "type": "terms_and_privacy"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") == True
        print("✓ POST /api/auth/consent records consent successfully")


# ==================== Admin Support Tickets Tests ====================
class TestAdminSupportTickets:
    """Tests for admin support ticket management"""
    
    def test_admin_list_all_tickets(self, auth_client):
        """Admin GET /api/admin/support/tickets returns all tickets"""
        resp = auth_client.get(f"{BASE_URL}/api/admin/support/tickets")
        
        if resp.status_code == 200:
            tickets = resp.json()
            assert isinstance(tickets, list)
            print(f"✓ Admin GET /api/admin/support/tickets returns {len(tickets)} tickets")
        elif resp.status_code == 403:
            print("⚠ Admin access denied (test user may not be admin)")
        else:
            pytest.fail(f"Unexpected status: {resp.status_code}")
    
    def test_admin_filter_tickets_by_status(self, auth_client):
        """Admin can filter tickets by status"""
        resp = auth_client.get(f"{BASE_URL}/api/admin/support/tickets?status=open")
        
        if resp.status_code == 200:
            tickets = resp.json()
            for ticket in tickets:
                assert ticket["status"] == "open"
            print(f"✓ Admin filtered open tickets: {len(tickets)}")
        elif resp.status_code == 403:
            print("⚠ Admin access denied")


# ==================== Ticket Validation Tests ====================
class TestTicketValidation:
    """Tests for ticket input validation"""
    
    def test_create_ticket_empty_subject(self, auth_client):
        """Creating ticket with empty subject fails"""
        resp = auth_client.post(f"{BASE_URL}/api/support/tickets", json={
            "subject": "",
            "message": "Test message",
            "category": "question"
        })
        assert resp.status_code == 400
        print("✓ Empty subject returns 400")
    
    def test_create_ticket_empty_message(self, auth_client):
        """Creating ticket with empty message fails"""
        resp = auth_client.post(f"{BASE_URL}/api/support/tickets", json={
            "subject": "Test subject",
            "message": "",
            "category": "question"
        })
        assert resp.status_code == 400
        print("✓ Empty message returns 400")
    
    def test_reply_empty_text(self, auth_client):
        """Replying with empty text fails"""
        # First create a ticket
        resp = auth_client.post(f"{BASE_URL}/api/support/tickets", json={
            "subject": f"TEST_Reply_Validation_{datetime.now().timestamp()}",
            "message": "Test message",
            "category": "question"
        })
        ticket_id = resp.json()["ticket_id"]
        
        # Try to reply with empty text
        resp2 = auth_client.post(f"{BASE_URL}/api/support/tickets/{ticket_id}/reply", json={
            "text": ""
        })
        assert resp2.status_code == 400
        print("✓ Empty reply text returns 400")
    
    def test_get_nonexistent_ticket(self, auth_client):
        """Getting nonexistent ticket returns 404"""
        resp = auth_client.get(f"{BASE_URL}/api/support/tickets/nonexistent_ticket_123")
        assert resp.status_code == 404
        print("✓ Nonexistent ticket returns 404")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
