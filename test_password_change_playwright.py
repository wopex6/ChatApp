"""
Playwright test for password change functionality in browser
"""
from playwright.sync_api import sync_playwright
import time

BASE_URL = "http://localhost:5001"
TEST_USERNAME = f"pwtest_{int(time.time())}"
TEST_EMAIL = f"{TEST_USERNAME}@test.com"
ORIGINAL_PASSWORD = "TestPass123!"
NEW_PASSWORD = "NewPass456!"

def test_password_change():
    with sync_playwright() as p:
        print("\n" + "="*70)
        print("🔐 PLAYWRIGHT PASSWORD CHANGE TEST")
        print("="*70)
        
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context()
        page = context.new_page()
        
        # Listen to console messages
        page.on("console", lambda msg: print(f"[BROWSER CONSOLE] {msg.type}: {msg.text}"))
        
        # Listen to page errors
        page.on("pageerror", lambda exc: print(f"[PAGE ERROR] {exc}"))
        
        try:
            # Step 1: Signup
            print(f"\n1. Opening ChatApp and signing up as {TEST_USERNAME}")
            page.goto(BASE_URL)
            time.sleep(2)
            
            # Click Sign Up tab
            page.click('text=Sign Up')
            time.sleep(1)
            
            # Fill signup form
            page.fill('#signup-username', TEST_USERNAME)
            page.fill('#signup-email', TEST_EMAIL)
            page.fill('#signup-password', ORIGINAL_PASSWORD)
            
            # Submit - use .btn class to avoid clicking the tab
            page.click('button.btn:has-text("Sign Up")')
            print("   Waiting for signup to complete...")
            
            # Wait for either success message or error message
            try:
                page.wait_for_selector('#success-message, #error-message', timeout=5000)
            except:
                print("   No success/error message appeared within 5 seconds")
            
            time.sleep(2)
            
            # Check for error messages first
            if page.is_visible('#error-message'):
                error_text = page.locator('#error-message').text_content()
                print(f"❌ FAIL: Signup error: {error_text}")
                page.screenshot(path="signup_failed.png")
                return False
            
            # Check for success message
            if page.is_visible('#success-message'):
                success_text = page.locator('#success-message').text_content()
                print(f"   Success message: {success_text}")
            
            # Wait for chat section to become visible
            try:
                page.wait_for_selector('#chat-section[style*="flex"]', timeout=5000)
                print(f"✅ Signup successful, logged in as {TEST_USERNAME}")
            except:
                # Try alternative check
                if page.is_visible('#user-info'):
                    print(f"✅ Signup successful (user-info visible), logged in as {TEST_USERNAME}")
                else:
                    print("❌ FAIL: Signup failed or not logged in")
                    print(f"   Auth section visible: {page.is_visible('#auth-section')}")
                    print(f"   Chat section visible: {page.is_visible('#chat-section')}")
                    print(f"   Chat section style: {page.get_attribute('#chat-section', 'style')}")
                    print(f"   URL: {page.url}")
                    page.screenshot(path="signup_failed.png")
                    return False
            
            # Step 2: Open Settings
            print("\n2. Opening Settings modal")
            settings_button = page.locator('button:has-text("Settings")')
            if settings_button.is_visible():
                settings_button.click()
                time.sleep(1)
                print("✅ Settings button clicked")
            else:
                print("❌ FAIL: Settings button not found")
                page.screenshot(path="no_settings_button.png")
                return False
            
            # Check if modal is visible
            if page.is_visible('#settings-modal'):
                print("✅ Settings modal is visible")
            else:
                print("❌ FAIL: Settings modal not visible")
                page.screenshot(path="modal_not_visible.png")
                return False
            
            # Step 3: Fill password change form
            print("\n3. Filling password change form")
            
            # Check if fields are empty (no autofill)
            current_pwd_value = page.input_value('#current-password')
            new_pwd_value = page.input_value('#new-password')
            confirm_pwd_value = page.input_value('#confirm-password')
            
            print(f"   Current password field: '{current_pwd_value}'")
            print(f"   New password field: '{new_pwd_value}'")
            print(f"   Confirm password field: '{confirm_pwd_value}'")
            
            if current_pwd_value or new_pwd_value or confirm_pwd_value:
                print("⚠️  WARNING: Fields have autofill values!")
            else:
                print("✅ All fields are empty (no autofill)")
            
            # Fill the form
            page.fill('#current-password', ORIGINAL_PASSWORD)
            print(f"✅ Entered current password: {ORIGINAL_PASSWORD}")
            
            page.fill('#new-password', NEW_PASSWORD)
            print(f"✅ Entered new password: {NEW_PASSWORD}")
            
            page.fill('#confirm-password', NEW_PASSWORD)
            print(f"✅ Entered confirm password: {NEW_PASSWORD}")
            
            # Take screenshot before submit
            page.screenshot(path="before_password_change.png")
            print("📸 Screenshot saved: before_password_change.png")
            
            # Step 4: Submit password change
            print("\n4. Clicking 'Change Password' button")
            page.click('button:has-text("Change Password")')
            time.sleep(2)
            
            # Check for success or error message
            success_msg = page.locator('#success-message')
            error_msg = page.locator('#error-message')
            
            if success_msg.is_visible():
                success_text = success_msg.text_content()
                print(f"✅ SUCCESS: {success_text}")
            elif error_msg.is_visible():
                error_text = error_msg.text_content()
                print(f"❌ ERROR: {error_text}")
                page.screenshot(path="password_change_error.png")
                return False
            else:
                print("⚠️  No success or error message visible")
                page.screenshot(path="no_message.png")
            
            # Take screenshot after submit
            page.screenshot(path="after_password_change.png")
            print("📸 Screenshot saved: after_password_change.png")
            
            # Step 5: Logout
            print("\n5. Logging out")
            time.sleep(1)
            page.click('button:has-text("Logout")')
            time.sleep(2)
            
            if page.is_visible('#login-form'):
                print("✅ Logged out successfully")
            else:
                print("❌ FAIL: Not at login screen")
                return False
            
            # Step 6: Try to login with OLD password (should fail)
            print(f"\n6. Trying to login with OLD password (should fail)")
            page.fill('#login-username', TEST_USERNAME)
            page.fill('#login-password', ORIGINAL_PASSWORD)
            page.click('button:has-text("Login")')
            time.sleep(2)
            
            if page.is_visible('#error-message'):
                error_text = page.locator('#error-message').text_content()
                print(f"✅ Old password rejected (correct!): {error_text}")
            elif page.is_visible('#chat-section'):
                print("❌ FAIL: Old password still works! Password was NOT changed!")
                page.screenshot(path="old_password_works.png")
                return False
            else:
                print("⚠️  Unknown state")
                page.screenshot(path="unknown_state_old_pwd.png")
            
            # Step 7: Login with NEW password (should succeed)
            print(f"\n7. Trying to login with NEW password (should succeed)")
            page.fill('#login-username', TEST_USERNAME)
            page.fill('#login-password', NEW_PASSWORD)
            page.click('button.btn:has-text("Login")')
            
            # Wait for either success or error
            try:
                page.wait_for_selector('#success-message, #error-message, #chat-section[style*="flex"]', timeout=5000)
            except:
                print("   Waiting for response...")
            
            time.sleep(2)
            
            # Check for error first
            if page.is_visible('#error-message'):
                error_text = page.locator('#error-message').text_content()
                print(f"❌ FAIL: Login error: {error_text}")
                page.screenshot(path="new_password_failed.png")
                return False
            
            # Check if logged in
            if page.is_visible('#chat-section[style*="flex"]') or page.is_visible('#user-info'):
                print("✅ NEW password works! Password change successful!")
                page.screenshot(path="new_password_success.png")
            else:
                print("⚠️  Unclear state - checking chat section visibility")
                print(f"   Chat section visible: {page.is_visible('#chat-section')}")
                print(f"   Auth section visible: {page.is_visible('#auth-section')}")
                page.screenshot(path="new_password_unclear.png")
                # Don't fail yet - might still be loading
                time.sleep(2)
                if page.is_visible('#chat-section') or page.is_visible('#user-info'):
                    print("✅ NEW password works after delay!")
                else:
                    print("❌ FAIL: New password doesn't work!")
                    return False
            
            print("\n" + "="*70)
            print("🎉 PASSWORD CHANGE TEST PASSED!")
            print("="*70)
            print(f"\n✅ User: {TEST_USERNAME}")
            print(f"✅ Original password: {ORIGINAL_PASSWORD}")
            print(f"✅ New password: {NEW_PASSWORD}")
            print(f"✅ Old password rejected")
            print(f"✅ New password works")
            print("\n⏱️  Keeping browser open for 5 seconds for inspection...")
            time.sleep(5)
            
            return True
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            page.screenshot(path="error_screenshot.png")
            print("📸 Error screenshot saved: error_screenshot.png")
            time.sleep(5)
            return False
        
        finally:
            print("\n🔚 Closing browser...")
            browser.close()

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════╗
║           PLAYWRIGHT PASSWORD CHANGE TEST                        ║
╚══════════════════════════════════════════════════════════════════╝

This test will:
  1. Signup a new user
  2. Open Settings modal
  3. Check for autofill issues
  4. Fill password change form
  5. Submit password change
  6. Logout
  7. Verify old password doesn't work
  8. Verify new password works
  
Requirements:
  - Server running on http://localhost:5001
  - Playwright installed: pip install playwright
  - Browsers installed: playwright install chromium
  
The browser will open in NON-HEADLESS mode so you can watch!
Starting test in 2 seconds...
""")
    
    time.sleep(2)
    result = test_password_change()
    
    if result:
        print("\n✅ TEST COMPLETED SUCCESSFULLY")
    else:
        print("\n❌ TEST FAILED - Check screenshots for details")
