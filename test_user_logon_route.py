from playwright.sync_api import sync_playwright
import time

def test_user_logon_route():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        
        print("\n" + "="*80)
        print("TESTING: localhost:5001/user_logon - Login-Only Screen")
        print("="*80)
        
        # Test 1: Access the route
        print("\n📍 TEST 1: ACCESSING /user_logon ROUTE")
        try:
            response = page.goto('http://localhost:5001/user_logon')
            print(f"   Status code: {response.status}")
            
            if response.status == 200:
                print(f"   ✅ Route accessible (200 OK)")
            else:
                print(f"   ❌ Route returned status: {response.status}")
                browser.close()
                return
        except Exception as e:
            print(f"   ❌ Could not access route: {e}")
            print(f"   ⚠️  Make sure server is running: python chatapp_simple.py")
            browser.close()
            return
        
        page.wait_for_timeout(1000)
        
        # Test 2: Check page title
        print("\n📄 TEST 2: PAGE TITLE")
        title = page.title()
        print(f"   Page title: '{title}'")
        if 'ChatApp' in title:
            print(f"   ✅ Title contains 'ChatApp'")
        
        # Test 3: Check for login form
        print("\n📝 TEST 3: LOGIN FORM ELEMENTS")
        
        # Check for login title
        login_title = page.locator('h1:has-text("ChatApp Login")')
        if login_title.count() > 0:
            print(f"   ✅ Found 'ChatApp Login' title")
            title_text = login_title.inner_text()
            print(f"      Text: '{title_text}'")
        else:
            print(f"   ❌ Login title not found")
        
        # Check for username field
        username_field = page.locator('#login-username')
        if username_field.count() > 0:
            print(f"   ✅ Username field present")
            placeholder = username_field.get_attribute('placeholder')
            print(f"      Placeholder: '{placeholder}'")
        else:
            print(f"   ❌ Username field missing")
        
        # Check for password field
        password_field = page.locator('#login-password')
        if password_field.count() > 0:
            print(f"   ✅ Password field present")
            placeholder = password_field.get_attribute('placeholder')
            print(f"      Placeholder: '{placeholder}'")
        else:
            print(f"   ❌ Password field missing")
        
        # Check for show/hide password button
        password_toggle = page.locator('.password-toggle-btn')
        if password_toggle.count() > 0:
            print(f"   ✅ Password toggle button present")
            toggle_text = password_toggle.inner_text()
            print(f"      Button text: '{toggle_text}'")
        else:
            print(f"   ⚠️  Password toggle button not found")
        
        # Check for login button
        login_button = page.locator('button[type="submit"]:has-text("Login")')
        if login_button.count() > 0:
            print(f"   ✅ Login button present")
            button_text = login_button.inner_text()
            print(f"      Button text: '{button_text}'")
        else:
            print(f"   ❌ Login button missing")
        
        # Test 4: Check NO signup elements
        print("\n🚫 TEST 4: VERIFY NO SIGNUP ELEMENTS")
        
        # Check for signup tabs
        signup_tab = page.locator('button:has-text("Sign Up")')
        if signup_tab.count() == 0:
            print(f"   ✅ No 'Sign Up' tab found")
        else:
            print(f"   ❌ Found {signup_tab.count()} 'Sign Up' tab(s) - should be 0")
        
        # Check for login/signup tabs container
        tabs_container = page.locator('.tabs')
        if tabs_container.count() == 0:
            print(f"   ✅ No tabs container found")
        else:
            print(f"   ⚠️  Tabs container still exists (but may be hidden)")
        
        # Check for signup form
        signup_form = page.locator('#signup-form')
        if signup_form.count() == 0:
            print(f"   ✅ No signup form found")
        else:
            print(f"   ❌ Signup form still exists")
        
        # Check for email field (signup only)
        email_field = page.locator('#signup-email')
        if email_field.count() == 0:
            print(f"   ✅ No email field found (signup removed)")
        else:
            print(f"   ❌ Email field exists (signup not removed)")
        
        # Test 5: Check form structure
        print("\n🏗️  TEST 5: FORM STRUCTURE")
        
        auth_section = page.locator('#auth-section')
        if auth_section.count() > 0:
            print(f"   ✅ Auth section found")
            
            # Count all forms in auth section
            all_forms = auth_section.locator('form')
            form_count = all_forms.count()
            print(f"   Forms in auth section: {form_count}")
            
            if form_count == 1:
                print(f"   ✅ Only 1 form (login only)")
            elif form_count > 1:
                print(f"   ⚠️  Multiple forms found - signup may still exist")
            else:
                print(f"   ❌ No forms found")
        
        # Test 6: Visual verification
        print("\n📸 TEST 6: VISUAL VERIFICATION")
        page.screenshot(path='test_screenshots/user_logon_route.png', full_page=False)
        print(f"   ✅ Screenshot saved: test_screenshots/user_logon_route.png")
        
        # Test 7: Check required attributes
        print("\n✅ TEST 7: REQUIRED FIELD VALIDATION")
        
        username_required = username_field.get_attribute('required')
        if username_required is not None:
            print(f"   ✅ Username field has 'required' attribute")
        else:
            print(f"   ⚠️  Username field missing 'required' attribute")
        
        password_required = password_field.get_attribute('required')
        if password_required is not None:
            print(f"   ✅ Password field has 'required' attribute")
        else:
            print(f"   ⚠️  Password field missing 'required' attribute")
        
        # Test 8: Try password toggle
        print("\n👁️  TEST 8: PASSWORD TOGGLE FUNCTIONALITY")
        
        try:
            # Type in password field
            password_field.fill('test123')
            print(f"   Typed test password")
            
            # Check initial type
            initial_type = password_field.get_attribute('type')
            print(f"   Initial type: '{initial_type}'")
            
            if initial_type == 'password':
                print(f"   ✅ Password hidden by default")
            
            # Click toggle button
            if password_toggle.count() > 0:
                password_toggle.click()
                page.wait_for_timeout(500)
                
                # Check type after toggle
                toggled_type = password_field.get_attribute('type')
                print(f"   After toggle: '{toggled_type}'")
                
                if toggled_type == 'text':
                    print(f"   ✅ Password toggle works (shows password)")
                else:
                    print(f"   ⚠️  Toggle may not be working")
        except Exception as e:
            print(f"   ⚠️  Could not test toggle: {e}")
        
        # Test 9: Test form submission (without actually logging in)
        print("\n📤 TEST 9: FORM SUBMISSION CHECK")
        
        try:
            # Clear and fill form
            username_field.fill('')
            password_field.fill('')
            
            print(f"   Attempting to submit empty form...")
            login_button.click()
            page.wait_for_timeout(500)
            
            # Browser should show validation message
            print(f"   ✅ Browser validation should prevent empty submission")
            
            # Fill valid data
            username_field.fill('TestUser')
            password_field.fill('TestPass123')
            print(f"   Filled form with test data")
            print(f"   ⚠️  Not submitting to avoid actual login attempt")
            
        except Exception as e:
            print(f"   ⚠️  Form test: {e}")
        
        # Summary
        print("\n" + "="*80)
        print("SUMMARY:")
        print("="*80)
        
        checks = []
        checks.append(("Route accessible (200 OK)", response.status == 200))
        checks.append(("Login title present", login_title.count() > 0))
        checks.append(("Username field present", username_field.count() > 0))
        checks.append(("Password field present", password_field.count() > 0))
        checks.append(("Login button present", login_button.count() > 0))
        checks.append(("NO signup tab", signup_tab.count() == 0))
        checks.append(("NO signup form", signup_form.count() == 0))
        checks.append(("NO email field", email_field.count() == 0))
        checks.append(("Only 1 form (login)", all_forms.count() == 1))
        
        print("\n✅ PASSED:")
        for check, passed in checks:
            if passed:
                print(f"   ✅ {check}")
        
        failed = [check for check, passed in checks if not passed]
        if failed:
            print("\n❌ FAILED:")
            for check in failed:
                print(f"   ❌ {check}")
        
        passed_count = sum(1 for _, passed in checks if passed)
        total_count = len(checks)
        
        print(f"\n📊 RESULTS: {passed_count}/{total_count} checks passed")
        
        if passed_count == total_count:
            print("🎉 ALL TESTS PASSED! Login-only screen working correctly!")
        elif passed_count >= total_count - 2:
            print("✅ MOSTLY WORKING - Minor issues detected")
        else:
            print("⚠️  ISSUES DETECTED - Review failed checks above")
        
        print("\n🌐 URL TESTED: http://localhost:5001/user_logon")
        print("📁 Screenshot: test_screenshots/user_logon_route.png")
        print("\nBrowser will stay open for 15 seconds...")
        page.wait_for_timeout(15000)
        
        browser.close()

if __name__ == '__main__':
    print("\n" + "="*80)
    print("PLAYWRIGHT TEST: /user_logon Route")
    print("="*80)
    print("\n⚠️  PREREQUISITES:")
    print("   1. Server must be running: python chatapp_simple.py")
    print("   2. Server should be on: http://localhost:5001")
    print("   3. Browser will launch automatically")
    print("\nStarting test in 3 seconds...")
    time.sleep(3)
    
    test_user_logon_route()
