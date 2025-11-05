from playwright.sync_api import sync_playwright
import time

def test_both_routes():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=400)
        page = browser.new_page()
        
        print("\n" + "="*80)
        print("TESTING: TWO ROUTES - SIGNUP vs LOGIN-ONLY")
        print("="*80)
        
        # ====== TEST ROUTE 1: localhost:5001/ (WITH SIGNUP) ======
        print("\n" + "="*80)
        print("ROUTE 1: localhost:5001/ (WITH SIGNUP)")
        print("="*80)
        
        try:
            response = page.goto('http://localhost:5001/')
            print(f"\n📍 Accessing: http://localhost:5001/")
            print(f"   Status: {response.status}")
            
            if response.status != 200:
                print(f"   ❌ Route returned: {response.status}")
                browser.close()
                return
            else:
                print(f"   ✅ Route accessible")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            browser.close()
            return
        
        page.wait_for_timeout(1000)
        
        # Check for tabs
        print(f"\n🔍 Checking for tabs...")
        login_tab = page.locator('.tabs button.tab:has-text("Login")')
        signup_tab = page.locator('.tabs button.tab:has-text("Sign Up")')
        
        if login_tab.count() > 0:
            print(f"   ✅ Login tab found")
        else:
            print(f"   ❌ Login tab missing")
        
        if signup_tab.count() > 0:
            print(f"   ✅ Sign Up tab found")
        else:
            print(f"   ❌ Sign Up tab missing")
        
        # Check for signup form
        print(f"\n📝 Checking for signup form...")
        signup_form = page.locator('#signup-form')
        email_field = page.locator('#signup-email')
        
        if signup_form.count() > 0:
            print(f"   ✅ Signup form exists")
        else:
            print(f"   ❌ Signup form missing")
        
        if email_field.count() > 0:
            print(f"   ✅ Email field exists (signup feature)")
        else:
            print(f"   ❌ Email field missing")
        
        # Test clicking signup tab
        print(f"\n🖱️  Testing Sign Up tab click...")
        if signup_tab.count() > 0:
            signup_tab.click()
            page.wait_for_timeout(500)
            
            # Check if signup form is visible
            signup_visible = signup_form.is_visible()
            login_visible = page.locator('#login-form').is_visible()
            
            print(f"   After clicking Sign Up tab:")
            print(f"   - Login form visible: {login_visible}")
            print(f"   - Signup form visible: {signup_visible}")
            
            if signup_visible and not login_visible:
                print(f"   ✅ Tab switching works correctly")
            else:
                print(f"   ⚠️  Tab switching may not be working")
        
        # Screenshot
        page.screenshot(path='test_screenshots/route_with_signup.png', full_page=False)
        print(f"\n📸 Screenshot: test_screenshots/route_with_signup.png")
        
        # ====== TEST ROUTE 2: localhost:5001/user_logon (LOGIN-ONLY) ======
        print("\n" + "="*80)
        print("ROUTE 2: localhost:5001/user_logon (LOGIN-ONLY)")
        print("="*80)
        
        try:
            response = page.goto('http://localhost:5001/user_logon')
            print(f"\n📍 Accessing: http://localhost:5001/user_logon")
            print(f"   Status: {response.status}")
            
            if response.status != 200:
                print(f"   ❌ Route returned: {response.status}")
                print(f"   ⚠️  Server may need restart!")
            else:
                print(f"   ✅ Route accessible")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            browser.close()
            return
        
        page.wait_for_timeout(1000)
        
        # Check for NO tabs
        print(f"\n🔍 Checking for NO tabs...")
        login_tab2 = page.locator('.tabs button.tab:has-text("Login")')
        signup_tab2 = page.locator('.tabs button.tab:has-text("Sign Up")')
        tabs_container = page.locator('.tabs')
        
        if signup_tab2.count() == 0:
            print(f"   ✅ NO Sign Up tab (correct)")
        else:
            print(f"   ❌ Sign Up tab found ({signup_tab2.count()}) - should be 0")
        
        if tabs_container.count() == 0:
            print(f"   ✅ NO tabs container (correct)")
        else:
            visible_tabs = tabs_container.filter(has=page.locator(':visible'))
            if visible_tabs.count() == 0:
                print(f"   ✅ Tabs container exists but not visible")
            else:
                print(f"   ⚠️  Tabs may be visible")
        
        # Check for login title
        print(f"\n📄 Checking for login title...")
        login_title = page.locator('h1:has-text("ChatApp Login")')
        
        if login_title.count() > 0:
            print(f"   ✅ 'ChatApp Login' title found")
            title_text = login_title.inner_text()
            print(f"   Title: '{title_text}'")
        else:
            print(f"   ❌ Login title not found")
        
        # Check for NO signup form
        print(f"\n🚫 Checking for NO signup elements...")
        signup_form2 = page.locator('#signup-form')
        email_field2 = page.locator('#signup-email')
        
        if signup_form2.count() == 0:
            print(f"   ✅ NO signup form (correct)")
        else:
            print(f"   ❌ Signup form found - should not exist")
        
        if email_field2.count() == 0:
            print(f"   ✅ NO email field (correct)")
        else:
            print(f"   ❌ Email field found - should not exist")
        
        # Check login form exists
        print(f"\n✅ Checking login form exists...")
        login_form2 = page.locator('#login-form')
        username_field2 = page.locator('#login-username')
        password_field2 = page.locator('#login-password')
        
        if login_form2.count() > 0:
            print(f"   ✅ Login form present")
        
        if username_field2.count() > 0:
            print(f"   ✅ Username field present")
        
        if password_field2.count() > 0:
            print(f"   ✅ Password field present")
        
        # Screenshot
        page.screenshot(path='test_screenshots/route_login_only.png', full_page=False)
        print(f"\n📸 Screenshot: test_screenshots/route_login_only.png")
        
        # ====== SUMMARY ======
        print("\n" + "="*80)
        print("SUMMARY: TWO ROUTES COMPARISON")
        print("="*80)
        
        print("\n📊 ROUTE 1: localhost:5001/ (WITH SIGNUP)")
        route1_checks = [
            ("Route accessible (200)", response.status == 200),
            ("Login tab present", login_tab.count() > 0),
            ("Sign Up tab present", signup_tab.count() > 0),
            ("Signup form exists", signup_form.count() > 0),
            ("Email field exists", email_field.count() > 0),
        ]
        
        for check, passed in route1_checks:
            icon = "✅" if passed else "❌"
            print(f"   {icon} {check}")
        
        print("\n📊 ROUTE 2: localhost:5001/user_logon (LOGIN-ONLY)")
        route2_checks = [
            ("Route accessible (200)", response.status == 200),
            ("Login title present", login_title.count() > 0),
            ("NO Sign Up tab", signup_tab2.count() == 0),
            ("NO signup form", signup_form2.count() == 0),
            ("NO email field", email_field2.count() == 0),
            ("Login form present", login_form2.count() > 0),
        ]
        
        for check, passed in route2_checks:
            icon = "✅" if passed else "❌"
            print(f"   {icon} {check}")
        
        # Overall results
        route1_passed = sum(1 for _, p in route1_checks if p)
        route2_passed = sum(1 for _, p in route2_checks if p)
        
        print(f"\n📈 RESULTS:")
        print(f"   Route 1 (WITH signup): {route1_passed}/{len(route1_checks)} checks passed")
        print(f"   Route 2 (LOGIN-only): {route2_passed}/{len(route2_checks)} checks passed")
        
        if route1_passed == len(route1_checks) and route2_passed == len(route2_checks):
            print(f"\n🎉 SUCCESS! Both routes working correctly!")
            print(f"   ✅ localhost:5001/ has signup option")
            print(f"   ✅ localhost:5001/user_logon is login-only")
        else:
            print(f"\n⚠️  Some checks failed - review above")
        
        print(f"\n📸 Screenshots saved:")
        print(f"   - test_screenshots/route_with_signup.png")
        print(f"   - test_screenshots/route_login_only.png")
        
        print("\nBrowser will stay open for 20 seconds...")
        page.wait_for_timeout(20000)
        
        browser.close()

if __name__ == '__main__':
    print("\n" + "="*80)
    print("PLAYWRIGHT TEST: Two Routes - Signup vs Login-Only")
    print("="*80)
    print("\n⚠️  PREREQUISITES:")
    print("   1. Server must be running: python chatapp_simple.py")
    print("   2. Server should be on: http://localhost:5001")
    print("   3. Both routes should be available:")
    print("      - localhost:5001/ (with signup)")
    print("      - localhost:5001/user_logon (login-only)")
    print("\nStarting test in 3 seconds...")
    time.sleep(3)
    
    test_both_routes()
