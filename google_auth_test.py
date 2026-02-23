import requests
import sys
from datetime import datetime

class GoogleAuthTester:
    def __init__(self, base_url="https://community-voice-17.preview.emergentagent.com"):
        self.base_url = base_url
        self.test_session_token = "test_session_1771462961642"  # From test credentials
        self.test_user_id = "test-user-1771462961642"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def run_test(self, name, method, endpoint, expected_status, data=None, cookies=None, headers=None):
        """Run a single API test with detailed logging"""
        url = f"{self.base_url}/api/{endpoint}" if not endpoint.startswith('http') else endpoint
        
        # Default headers
        default_headers = {'Content-Type': 'application/json'}
        if headers:
            default_headers.update(headers)
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        print(f"   Method: {method}")
        print(f"   Expected: {expected_status}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=default_headers, cookies=cookies, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=default_headers, cookies=cookies, timeout=10)

            print(f"   Status: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - {name}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 300:
                        print(f"   Response: {response_data}")
                except:
                    pass
                
                # Return response and cookies for chaining
                return success, response.json() if response.status_code < 500 else {}, response.cookies
            else:
                self.failed_tests.append(f"{name}: Expected {expected_status}, got {response.status_code}")
                print(f"❌ Failed - {name}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Raw response: {response.text[:200]}")
                return False, {}, None

        except requests.exceptions.Timeout:
            print(f"❌ Failed - {name} (Timeout)")
            self.failed_tests.append(f"{name}: Request timeout")
            return False, {}, None
        except Exception as e:
            print(f"❌ Failed - {name} (Error: {str(e)})")
            self.failed_tests.append(f"{name}: {str(e)}")
            return False, {}, None

    def test_auth_session_endpoint(self):
        """Test POST /api/auth/session endpoint with test session token"""
        print("\n=== TESTING AUTH/SESSION ENDPOINT ===")
        
        # Test session creation with test token
        session_data = {"session_id": self.test_session_token}
        success, response_data, cookies = self.run_test(
            "Create Session", "POST", "auth/session", 200, 
            data=session_data
        )
        
        if success and response_data:
            print(f"   Session created for user: {response_data.get('email', 'Unknown')}")
            print(f"   User ID: {response_data.get('user_id', 'Unknown')}")
            print(f"   User role: {response_data.get('role', 'Unknown')}")
            
            # Check if cookie was set
            if cookies and 'session_token' in cookies:
                print(f"   ✅ Session cookie set successfully")
                return cookies
            else:
                print(f"   ❌ Session cookie NOT set")
                self.failed_tests.append("Session cookie was not set in response")
                
        return None

    def test_auth_me_with_cookie(self, cookies):
        """Test GET /api/auth/me with session cookie"""
        print("\n=== TESTING AUTH/ME WITH COOKIE ===")
        
        if not cookies:
            print("   ⚠️  No cookies available from session creation")
            return False
            
        success, response_data, _ = self.run_test(
            "Get Current User with Cookie", "GET", "auth/me", 200, 
            cookies=cookies
        )
        
        if success and response_data:
            print(f"   Authenticated user: {response_data.get('email', 'Unknown')}")
            print(f"   User points: {response_data.get('points', 0)}")
            return True
        return False

    def test_auth_me_without_auth(self):
        """Test GET /api/auth/me without authentication (should fail)"""
        print("\n=== TESTING AUTH/ME WITHOUT AUTH ===")
        
        success, _, _ = self.run_test(
            "Get Current User without Auth", "GET", "auth/me", 401
        )
        
        if success:
            print("   ✅ Correctly returns 401 when not authenticated")
        return success

    def test_auth_logout(self, cookies):
        """Test POST /api/auth/logout"""
        print("\n=== TESTING AUTH/LOGOUT ===")
        
        if not cookies:
            print("   ⚠️  No cookies available for logout test")
            # Still test logout without cookies
            success, _, _ = self.run_test(
                "Logout without Cookie", "POST", "auth/logout", 200
            )
            return success
            
        success, response_data, _ = self.run_test(
            "Logout with Cookie", "POST", "auth/logout", 200,
            cookies=cookies
        )
        
        if success and response_data:
            print(f"   Logout successful: {response_data.get('success', False)}")
        return success

    def test_protected_endpoint_with_cookie(self, cookies):
        """Test a protected endpoint with session cookie"""
        print("\n=== TESTING PROTECTED ENDPOINT WITH COOKIE ===")
        
        if not cookies:
            print("   ⚠️  No cookies available for protected endpoint test")
            return False
            
        success, response_data, _ = self.run_test(
            "Get Profile with Cookie", "GET", "profile", 200,
            cookies=cookies
        )
        
        if success and response_data:
            print(f"   Profile access successful for: {response_data.get('name', 'Unknown')}")
            return True
        return False

    def test_protected_endpoint_without_auth(self):
        """Test protected endpoint without authentication (should fail)"""
        print("\n=== TESTING PROTECTED ENDPOINT WITHOUT AUTH ===")
        
        success, _, _ = self.run_test(
            "Get Profile without Auth", "GET", "profile", 401
        )
        
        if success:
            print("   ✅ Correctly returns 401 when not authenticated")
        return success

    def test_cookie_attributes(self):
        """Test that cookie is set with proper attributes (SameSite=lax)"""
        print("\n=== TESTING COOKIE ATTRIBUTES ===")
        
        session_data = {"session_id": self.test_session_token}
        url = f"{self.base_url}/api/auth/session"
        
        print(f"   Testing cookie attributes at {url}")
        
        try:
            response = requests.post(url, json=session_data, timeout=10)
            self.tests_run += 1
            
            if response.status_code == 200:
                # Check Set-Cookie header
                set_cookie_header = response.headers.get('Set-Cookie', '')
                print(f"   Set-Cookie header: {set_cookie_header}")
                
                # Check for SameSite=lax (the key fix)
                if 'SameSite=lax' in set_cookie_header or 'SameSite=Lax' in set_cookie_header:
                    self.tests_passed += 1
                    print("   ✅ Cookie has SameSite=lax (correct)")
                    
                    # Check other attributes
                    if 'HttpOnly' in set_cookie_header:
                        print("   ✅ Cookie is HttpOnly (secure)")
                    if 'Secure' in set_cookie_header:
                        print("   ✅ Cookie is Secure (HTTPS)")
                        
                else:
                    self.failed_tests.append("Cookie does not have SameSite=lax attribute")
                    print("   ❌ Cookie missing SameSite=lax attribute")
                    
            else:
                self.failed_tests.append(f"Cookie test: Expected 200, got {response.status_code}")
                print(f"   ❌ Failed to create session for cookie test")
                
        except Exception as e:
            self.failed_tests.append(f"Cookie test error: {str(e)}")
            print(f"   ❌ Cookie test error: {str(e)}")

def main():
    print("🚀 Testing Google Auth Flow Components...")
    print("📍 Backend URL: https://community-voice-17.preview.emergentagent.com")
    print("🔑 Using test session token: test_session_1771462961642")
    print("📝 Testing auth endpoints mentioned in bug fix...")
    
    tester = GoogleAuthTester()
    
    # Test auth endpoints in order
    cookies = tester.test_auth_session_endpoint()
    tester.test_cookie_attributes()
    tester.test_auth_me_with_cookie(cookies)
    tester.test_auth_me_without_auth()
    tester.test_protected_endpoint_with_cookie(cookies)
    tester.test_protected_endpoint_without_auth()
    tester.test_auth_logout(cookies)
    
    # Test that logout actually cleared the session
    if cookies:
        print("\n=== TESTING POST-LOGOUT ACCESS ===")
        success, _, _ = tester.run_test(
            "Access after Logout", "GET", "auth/me", 401,
            cookies=cookies
        )
        if success:
            print("   ✅ Session properly cleared after logout")
    
    # Print final results
    print(f"\n{'='*60}")
    print(f"📊 GOOGLE AUTH TEST RESULTS")
    print(f"{'='*60}")
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed / tester.tests_run * 100):.1f}%")
    
    if tester.failed_tests:
        print(f"\n❌ FAILED TESTS:")
        for i, failure in enumerate(tester.failed_tests, 1):
            print(f"  {i}. {failure}")
    else:
        print(f"\n✅ All Google Auth backend components working correctly!")
    
    return 0 if len(tester.failed_tests) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())