import requests
import sys
from datetime import datetime

class ComprehensiveAPITester:
    def __init__(self, base_url="https://community-voice-17.preview.emergentagent.com"):
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

    def test_upload_endpoints(self):
        """Test file upload endpoints (Feature 1)"""
        print("\n=== TESTING FILE UPLOAD ENDPOINTS ===")
        
        # Test upload endpoint with mock file data
        import tempfile
        import os
        
        # Create a small test image file
        test_file_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDAT\x08\x1dc\xf8\x00\x00\x00\x01\x00\x01'
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            f.write(test_file_content)
            temp_path = f.name
        
        try:
            # Test file upload
            url = f"{self.base_url}/api/upload"
            files = {'file': ('test.png', open(temp_path, 'rb'), 'image/png')}
            headers = {'Authorization': f'Bearer {self.session_token}'}
            
            print(f"\n🔍 Testing File Upload...")
            response = requests.post(url, files=files, headers=headers, timeout=10)
            self.tests_run += 1
            
            if response.status_code == 200:
                self.tests_passed += 1
                print(f"✅ Passed - File Upload")
                upload_data = response.json()
                
                # Test serving the uploaded file
                if 'url' in upload_data:
                    file_url = f"{self.base_url}{upload_data['url']}"
                    self.run_test("Serve Uploaded File", "GET", file_url, 200)
                    
            else:
                self.failed_tests.append(f"File Upload: Expected 200, got {response.status_code}")
                print(f"❌ Failed - File Upload")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Raw response: {response.text[:200]}")
                    
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass

    def test_rating_endpoints(self):
        """Test rating system endpoints (Feature 4)"""
        print("\n=== TESTING RATING SYSTEM ENDPOINTS ===")
        
        success, status_data = self.run_test("Get Rating Status", "GET", "rating/status", 200, auth_required=True)
        if success and status_data:
            print(f"   Current status: {status_data.get('current', {}).get('name', 'Unknown')}")
            print(f"   Level: {status_data.get('level', 0)}")
            print(f"   All statuses count: {len(status_data.get('all_statuses', []))}")
            
            # Check if we have the expected 7 statuses
            all_statuses = status_data.get('all_statuses', [])
            if len(all_statuses) == 7:
                print("   ✅ Found expected 7 rating statuses")
            else:
                print(f"   ⚠️  Expected 7 statuses, found {len(all_statuses)}")
        
        success, leaderboard = self.run_test("Get Leaderboard", "GET", "rating/leaderboard", 200)
        if success and leaderboard:
            print(f"   Leaderboard entries: {len(leaderboard)}")

    def test_referral_endpoints(self):
        """Test referral system endpoints (Feature 6)"""
        print("\n=== TESTING REFERRAL SYSTEM ENDPOINTS ===")
        
        # Get referral stats
        success, stats = self.run_test("Get Referral Stats", "GET", "referral/stats", 200, auth_required=True)
        if success and stats:
            print(f"   Referral code: {stats.get('referral_code', 'None')}")
            print(f"   Referred count: {stats.get('referred_count', 0)}")
        
        # Test applying referral code (should fail if already applied or using own code)
        referral_data = {"code": "TESTCODE"}
        self.run_test("Apply Referral Code", "POST", "referral/apply", 400, data=referral_data, auth_required=True)

    def test_admin_endpoints(self):
        """Test admin panel endpoints (Feature 3) - Admin role required"""
        print("\n=== TESTING ADMIN ENDPOINTS (ADMIN ROLE REQUIRED) ===")
        
        # Test admin stats
        success, stats = self.run_test("Admin Stats", "GET", "admin/stats", 200, auth_required=True)
        if success and stats:
            print(f"   Total users: {stats.get('total_users', 0)}")
            print(f"   Total reviews: {stats.get('total_reviews', 0)}")
            print(f"   Pending reviews: {stats.get('pending_reviews', 0)}")
            print(f"   Expired reviews: {stats.get('expired_reviews', 0)}")
        
        # Test admin reviews list
        success, reviews = self.run_test("Admin Reviews List", "GET", "admin/reviews", 200, auth_required=True)
        if success and reviews:
            print(f"   Admin found {len(reviews)} reviews")
        
        # Test admin reviews with status filter
        self.run_test("Admin Pending Reviews", "GET", "admin/reviews?status=pending", 200, auth_required=True)
        
        # Test admin users list
        success, users = self.run_test("Admin Users List", "GET", "admin/users", 200, auth_required=True)
        if success and users:
            print(f"   Admin found {len(users)} users")
        
        # Test admin approve/reject review (need a pending review ID)
        success, pending_reviews = self.run_test("Get Pending for Admin Action", "GET", "admin/reviews?status=pending", 200, auth_required=True)
        if success and pending_reviews and len(pending_reviews) > 0:
            review_id = pending_reviews[0]['review_id']
            
            # Test reject with reason
            reject_data = {"reason": "Test rejection by admin"}
            self.run_test("Admin Reject Review", "PUT", f"admin/reviews/{review_id}/reject", 200, 
                         data=reject_data, auth_required=True)

    def test_non_admin_blocked(self):
        """Test that non-admin users get 403 on admin routes"""
        print("\n=== TESTING NON-ADMIN ACCESS BLOCKED ===")
        
        # Create a session without admin role (we'll simulate this by using invalid token)
        temp_token = "invalid_token_should_fail"
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {temp_token}'}
        
        url = f"{self.base_url}/api/admin/stats"
        print(f"\n🔍 Testing Non-Admin Blocked Access...")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            self.tests_run += 1
            
            if response.status_code == 401 or response.status_code == 403:
                self.tests_passed += 1
                print(f"✅ Passed - Non-Admin Blocked (Status: {response.status_code})")
            else:
                self.failed_tests.append(f"Non-Admin Block: Expected 401/403, got {response.status_code}")
                print(f"❌ Failed - Non-Admin should be blocked")
        except Exception as e:
            self.failed_tests.append(f"Non-Admin Block test error: {str(e)}")
            print(f"❌ Failed - Non-Admin Block test error: {str(e)}")

    def test_pwa_manifest(self):
        """Test PWA manifest exists (Feature 2)"""
        print("\n=== TESTING PWA MANIFEST ===")
        
        # Test manifest.json accessibility
        manifest_url = f"{self.base_url.replace('/api', '')}/manifest.json"
        print(f"\n🔍 Testing PWA Manifest at {manifest_url}...")
        
        try:
            response = requests.get(manifest_url, timeout=10)
            self.tests_run += 1
            
            if response.status_code == 200:
                self.tests_passed += 1
                print(f"✅ Passed - PWA Manifest exists")
                try:
                    manifest_data = response.json()
                    print(f"   App name: {manifest_data.get('name', 'Unknown')}")
                    print(f"   Short name: {manifest_data.get('short_name', 'Unknown')}")
                    print(f"   Display: {manifest_data.get('display', 'Unknown')}")
                except:
                    pass
            else:
                self.failed_tests.append(f"PWA Manifest: Expected 200, got {response.status_code}")
                print(f"❌ Failed - PWA Manifest not accessible")
                
        except Exception as e:
            self.failed_tests.append(f"PWA Manifest error: {str(e)}")
            print(f"❌ Failed - PWA Manifest error: {str(e)}")

    def test_review_expiry(self):
        """Test review expiry functionality (Feature 5)"""
        print("\n=== TESTING REVIEW EXPIRY SYSTEM ===")
        
        # Check for expired reviews in the system
        success, reviews = self.run_test("List All Reviews", "GET", "reviews", 200)
        if success and reviews:
            expired_reviews = [r for r in reviews if r.get('status') == 'expired']
            pending_reviews = [r for r in reviews if r.get('status') == 'pending']
            
            print(f"   Found {len(expired_reviews)} expired reviews")
            print(f"   Found {len(pending_reviews)} pending reviews")
            
            # Check if any reviews have expires_at field
            reviews_with_expiry = [r for r in reviews if r.get('expires_at')]
            print(f"   Reviews with expiry timestamps: {len(reviews_with_expiry)}")
            
            if reviews_with_expiry:
                print("   ✅ Review expiry system appears to be implemented")
            else:
                print("   ⚠️  No reviews found with expiry timestamps")

def main():
    print("🚀 Starting comprehensive API testing...")
    print("📍 Backend URL: https://community-voice-17.preview.emergentagent.com")
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
    
    # NEW FEATURES TESTING (6 enhancement features)
    tester.test_upload_endpoints()           # Feature 1: File upload
    tester.test_pwa_manifest()              # Feature 2: PWA manifest  
    tester.test_admin_endpoints()           # Feature 3: Admin panel
    tester.test_rating_endpoints()          # Feature 4: Rating system
    tester.test_review_expiry()             # Feature 5: Review expiry
    tester.test_referral_endpoints()        # Feature 6: Referral system
    tester.test_non_admin_blocked()         # Security: Non-admin blocked
    
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