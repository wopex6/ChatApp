"""
Playwright test to debug password change functionality
Run this test while watching browser console for detailed logs
"""
from playwright.sync_api import sync_playwright
import time

def test_password_change():
    with sync_playwright() as p:
        # Launch browser with visible UI
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        context = browser.new_context()
        
        # Enable console logging
        page = context.new_page()
        
        # Listen to console messages
        def handle_console(msg):
            print(f"[BROWSER CONSOLE] {msg.type.upper()}: {msg.text}")
        
        page.on("console", handle_console)
        
        print("\n" + "="*70)
        print("🔍 PASSWORD CHANGE DEBUG TEST")
        print("="*70)
        
        # Go to the app
        print("\n1. Loading application...")
        page.goto("http://localhost:5001")
        time.sleep(2)
        
        # Login as test user
        print("\n2. Logging in as test user...")
        page.fill("#login-username", "testuser1")
        page.fill("#login-password", "password123")
        page.click("button[type='submit']:has-text('Login')")
        time.sleep(3)
        
        # Check if logged in
        if page.is_visible("#chat-section"):
            print("✅ Login successful!")
        else:
            print("❌ Login failed!")
            browser.close()
            return
        
        # Open settings
        print("\n3. Opening Settings...")
        page.click("button:has-text('Settings')")
        time.sleep(1)
        
        if page.is_visible("#settings-modal.show"):
            print("✅ Settings modal opened!")
        else:
            print("❌ Settings modal not visible!")
            browser.close()
            return
        
        # Fill password fields
        print("\n4. Filling password fields...")
        page.fill("#current-password", "password123")
        print("   Current password: ********")
        
        page.fill("#new-password", "newpass123")
        print("   New password: ********")
        
        page.fill("#confirm-password", "newpass123")
        print("   Confirm password: ********")
        
        time.sleep(1)
        
        # Click Change Password button
        print("\n5. Clicking 'Change Password' button...")
        print("   ⚠️  WATCH THE BROWSER CONSOLE FOR DETAILED LOGS!")
        
        # Get the form
        form = page.locator("#change-password-form")
        submit_button = form.locator("button[type='submit']")
        
        print(f"   Form found: {form.count() > 0}")
        print(f"   Submit button found: {submit_button.count() > 0}")
        
        if submit_button.count() > 0:
            submit_button.click()
            print("   ✅ Submit button clicked!")
        else:
            print("   ❌ Submit button not found!")
            browser.close()
            return
        
        # Wait for response
        print("\n6. Waiting for response...")
        time.sleep(5)
        
        # Check for success or error message
        if page.is_visible(".success-message"):
            print("✅ SUCCESS message appeared!")
        elif page.is_visible(".error-message"):
            error_text = page.locator(".error-message").inner_text()
            print(f"❌ ERROR message: {error_text}")
        else:
            print("⚠️  No success or error message visible")
        
        # Check if modal is closed
        if not page.is_visible("#settings-modal.show"):
            print("✅ Settings modal closed (indicates success)")
        else:
            print("⚠️  Settings modal still open")
        
        print("\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70)
        print("Check the browser console output above for detailed debugging info")
        print("Look for lines starting with '🔐 [Password Change]'")
        print("="*70)
        
        # Keep browser open for inspection
        print("\n⏸️  Browser will stay open for 30 seconds for inspection...")
        time.sleep(30)
        
        browser.close()

if __name__ == "__main__":
    print("Starting Playwright password change debug test...")
    print("Make sure the server is running on http://localhost:5001")
    print("\n")
    
    test_password_change()
