import requests
import sys
from datetime import datetime

class ComprehensiveAPITester:
    def __init__(self, base_url="https://rebuild-engine-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.session_token = "test_session_1771462961642"  # From test credentials
        self.user_id = "test-user-1771462961642"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def run_test(self, name, method, endpoint, expected_status, data=None, auth_required=False):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}" if not endpoint.startswith('http') else endpoint
        headers = {'Content-Type': 'application/json'}
        
        if auth_required:
            headers['Authorization'] = f'Bearer {self.session_token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - {name}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 200:
                        print(f"   Response: {response_data}")
                except:
                    pass
            else:
                self.failed_tests.append(f"{name}: Expected {expected_status}, got {response.status_code}")
                print(f"❌ Failed - {name}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Raw response: {response.text[:200]}")

            return success, response.json() if response.status_code < 500 else {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - {name} (Timeout)")
            self.failed_tests.append(f"{name}: Request timeout")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - {name} (Error: {str(e)})")
            self.failed_tests.append(f"{name}: {str(e)}")
            return False, {}

    def test_health_endpoints(self):
        """Test basic health endpoints"""
        print("\n=== TESTING HEALTH ENDPOINTS ===")
        self.run_test("API Root", "GET", "", 200)
        self.run_test("API Health", "GET", "health", 200)

    def test_auth_endpoints(self):
        """Test authentication endpoints"""
        print("\n=== TESTING AUTH ENDPOINTS ===")
        
        # Test auth/me with valid session
        self.run_test("Get Current User", "GET", "auth/me", 200, auth_required=True)
        
        # Test logout (should work even if already logged out)
        self.run_test("Logout", "POST", "auth/logout", 200, auth_required=True)

    def test_organizations_endpoints(self):
        """Test organizations endpoints"""
        print("\n=== TESTING ORGANIZATIONS ENDPOINTS ===")
        
        success, orgs = self.run_test("List Organizations", "GET", "organizations", 200)
        if success and orgs:
            print(f"   Found {len(orgs)} organizations")
            if len(orgs) > 0:
                org_id = orgs[0].get('org_id')
                if org_id:
                    self.run_test("Get Organization", "GET", f"organizations/{org_id}", 200)

    def test_reviews_endpoints(self):
        """Test reviews endpoints"""
        print("\n=== TESTING REVIEWS ENDPOINTS ===")
        
        success, reviews = self.run_test("List Reviews", "GET", "reviews", 200)
        if success and reviews:
            print(f"   Found {len(reviews)} reviews")
            if len(reviews) > 0:
                review_id = reviews[0].get('review_id')
                if review_id:
                    self.run_test("Get Review", "GET", f"reviews/{review_id}", 200)
        
        # Test creating a review (requires auth and org_id)
        success, orgs = self.run_test("List Orgs for Review", "GET", "organizations", 200)
        if success and orgs and len(orgs) > 0:
            org_id = orgs[0]['org_id']
            review_data = {
                "org_id": org_id,
                "title": f"Test Review {datetime.now().strftime('%H:%M:%S')}",
                "content": "This is a test review created by automated testing.",
                "rating": 3,
                "photos": [],
                "latitude": 43.023,
                "longitude": 44.682
            }
            self.run_test("Create Review", "POST", "reviews", 201, data=review_data, auth_required=True)

    def test_rewards_endpoints(self):
        """Test rewards endpoints"""
        print("\n=== TESTING REWARDS ENDPOINTS ===")
        
        success, rewards = self.run_test("List Rewards", "GET", "rewards", 200)
        if success and rewards:
            print(f"   Found {len(rewards)} rewards")
            
            # Try to redeem a low-cost reward
            cheap_reward = None
            for reward in rewards:
                if reward.get('price', 999) <= 50:  # User has 250 points
                    cheap_reward = reward
                    break
            
            if cheap_reward:
                reward_id = cheap_reward['reward_id']
                print(f"   Attempting to redeem: {cheap_reward['name']} ({cheap_reward['price']} points)")
                self.run_test("Redeem Reward", "POST", f"rewards/{reward_id}/redeem", 200, auth_required=True)

    def test_notifications_endpoints(self):
        """Test notifications endpoints"""
        print("\n=== TESTING NOTIFICATIONS ENDPOINTS ===")
        
        self.run_test("List Notifications", "GET", "notifications", 200, auth_required=True)
        self.run_test("Mark All Read", "PUT", "notifications/read-all", 200, auth_required=True)

    def test_verifications_endpoints(self):
        """Test verification endpoints"""
        print("\n=== TESTING VERIFICATIONS ENDPOINTS ===")
        
        # Get reviews to find one we can verify
        success, reviews = self.run_test("Get Reviews for Verification", "GET", "reviews", 200)
        if success and reviews:
            # Find a review not created by test user
            other_review = None
            for review in reviews:
                if review.get('user_id') != self.user_id and review.get('status') == 'pending':
                    other_review = review
                    break
            
            if other_review:
                verification_data = {
                    "review_id": other_review['review_id'],
                    "comment": "Test verification comment",
                    "photos": []
                }
                self.run_test("Create Verification", "POST", "verifications", 200, 
                            data=verification_data, auth_required=True)

    def test_profile_endpoints(self):
        """Test profile endpoints"""
        print("\n=== TESTING PROFILE ENDPOINTS ===")
        
        self.run_test("Get Profile", "GET", "profile", 200, auth_required=True)
        
        # Update profile
        profile_data = {
            "age_group": "18-25",
            "theme": "dark"
        }
        self.run_test("Update Profile", "PUT", "profile", 200, data=profile_data, auth_required=True)

    def test_points_endpoints(self):
        """Test points endpoints"""
        print("\n=== TESTING POINTS ENDPOINTS ===")
        
        self.run_test("Get Points Balance", "GET", "points/balance", 200, auth_required=True)
        self.run_test("Get Points History", "GET", "points/history", 200, auth_required=True)

def main():
    print("🚀 Starting comprehensive API testing...")
    print("📍 Backend URL: https://rebuild-engine-1.preview.emergentagent.com")
    print("🔑 Using test session token: test_session_1771462961642")
    
    tester = ComprehensiveAPITester()
    
    # Run all test suites
    tester.test_health_endpoints()
    tester.test_auth_endpoints()
    tester.test_organizations_endpoints()
    tester.test_reviews_endpoints() 
    tester.test_rewards_endpoints()
    tester.test_notifications_endpoints()
    tester.test_verifications_endpoints()
    tester.test_profile_endpoints()
    tester.test_points_endpoints()
    
    # Print final results
    print(f"\n{'='*50}")
    print(f"📊 FINAL RESULTS")
    print(f"{'='*50}")
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed / tester.tests_run * 100):.1f}%")
    
    if tester.failed_tests:
        print(f"\n❌ FAILED TESTS:")
        for i, failure in enumerate(tester.failed_tests, 1):
            print(f"  {i}. {failure}")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())