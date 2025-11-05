"""
Playwright test to verify the 4 specific fixes reported on Nov 3 afternoon
1. Message alignment (admin messages on correct side)
2. No auto-login (login screen shows)
3. Larger conversation box
4. Layout improvements
"""

from playwright.sync_api import sync_playwright
import time

BASE_URL = "http://localhost:5001"
ADMIN_USER = "Ken Tse"
ADMIN_PASSWORD = "KenTse2025!"

# Use an existing user for testing
TEST_USER = "nu1"  # Assuming this user exists from screenshot
TEST_PASSWORD = "test"  # You may need to adjust

def test_fixes():
    with sync_playwright() as p:
        print("\n" + "="*70)
        print("🧪 TESTING 4 REPORTED FIXES")
        print("="*70)
        
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        results = {'passed': 0, 'failed': 0}
        
        try:
            # ========== TEST 1: No Auto-Login (Issue #2) ==========
            print("\n📝 TEST 1: No Auto-Login - Login Screen Shows")
            print("-"*70)
            
            print("1. Opening ChatApp...")
            page.goto(BASE_URL)
            time.sleep(2)
            
            # Check if login form is visible (not auto-logged in)
            login_visible = page.locator("#login-form").is_visible()
            auth_section_visible = page.locator("#auth-section").is_visible()
            chat_hidden = not page.locator("#chat-section").is_visible()
            
            if login_visible and auth_section_visible and chat_hidden:
                print("   ✅ PASS: Login screen is showing (no auto-login)")
                results['passed'] += 1
            else:
                print("   ❌ FAIL: Auto-login occurred or login not visible")
                print(f"      Login visible: {login_visible}")
                print(f"      Auth visible: {auth_section_visible}")
                print(f"      Chat hidden: {chat_hidden}")
                results['failed'] += 1
            
            # ========== TEST 2: Admin Login & Layout ==========
            print("\n📝 TEST 2: Admin Login & Layout Size (Issue #3)")
            print("-"*70)
            
            print("2. Logging in as Ken Tse...")
            page.fill("#login-username", ADMIN_USER)
            page.fill("#login-password", ADMIN_PASSWORD)
            page.click("button:has-text('Login')")
            time.sleep(3)
            
            # Check if admin panel is visible
            admin_panel_visible = page.locator("#admin-panel").is_visible()
            
            if admin_panel_visible:
                print("   ✅ Admin dashboard loaded")
                results['passed'] += 1
                
                # Check admin panel width (should be ~300-350px)
                admin_panel = page.locator("#admin-panel")
                box = admin_panel.bounding_box()
                
                if box:
                    width = box['width']
                    print(f"   Admin panel width: {width}px")
                    
                    if 280 <= width <= 380:
                        print("   ✅ PASS: Admin panel has correct fixed width")
                        results['passed'] += 1
                    else:
                        print(f"   ⚠️  WARNING: Width {width}px outside expected range")
                        results['failed'] += 1
                else:
                    print("   ⚠️  Could not measure admin panel")
                    results['failed'] += 1
                
                # Check messages container
                messages_container = page.locator("#messages-container")
                if messages_container.is_visible():
                    msg_box = messages_container.bounding_box()
                    if msg_box:
                        msg_width = msg_box['width']
                        print(f"   Messages container width: {msg_width}px")
                        
                        # Messages should be significantly wider than admin panel
                        if msg_width > width * 1.5:
                            print("   ✅ PASS: Messages area is much larger than sidebar")
                            results['passed'] += 1
                        else:
                            print("   ❌ FAIL: Messages area not large enough")
                            results['failed'] += 1
            else:
                print("   ❌ FAIL: Admin panel not visible after login")
                results['failed'] += 1
            
            # ========== TEST 3: Message Alignment (Manual Check) ==========
            print("\n📝 TEST 3: Message Alignment Check (Issue #1)")
            print("-"*70)
            print("   ℹ️  This requires manual verification:")
            print("   1. In the browser window that opened:")
            print("   2. Select a user from the list")
            print("   3. Send a message")
            print("   4. Verify YOUR message appears on the RIGHT (blue)")
            print("   5. Verify USER's messages appear on the LEFT (white)")
            print()
            print("   Pausing for 15 seconds for visual inspection...")
            
            # Take screenshot for documentation
            page.screenshot(path="test_admin_layout.png")
            print("   📸 Screenshot saved: test_admin_layout.png")
            
            time.sleep(15)
            
            # Check if message classes exist
            sent_by_me = page.locator(".message.sent-by-me").count()
            sent_by_other = page.locator(".message.sent-by-other").count()
            
            print(f"   Messages with 'sent-by-me' class: {sent_by_me}")
            print(f"   Messages with 'sent-by-other' class: {sent_by_other}")
            
            if sent_by_me > 0 or sent_by_other > 0:
                print("   ✅ PASS: New message classes are in use")
                results['passed'] += 1
            else:
                print("   ℹ️  No messages found (may need to send some)")
            
            # ========== TEST 4: Logout ==========
            print("\n📝 TEST 4: Logout & Return to Login Screen")
            print("-"*70)
            
            print("4. Logging out...")
            page.click("button:has-text('Logout')")
            time.sleep(2)
            
            # Verify back at login screen
            login_visible_again = page.locator("#login-form").is_visible()
            chat_hidden_again = not page.locator("#chat-section").is_visible()
            
            if login_visible_again and chat_hidden_again:
                print("   ✅ PASS: Returned to login screen")
                results['passed'] += 1
            else:
                print("   ❌ FAIL: Did not return to login screen properly")
                results['failed'] += 1
            
            # ========== SUMMARY ==========
            print("\n" + "="*70)
            print("📊 TEST SUMMARY")
            print("="*70)
            
            total = results['passed'] + results['failed']
            print(f"\nTotal Tests: {total}")
            print(f"✅ Passed: {results['passed']}")
            print(f"❌ Failed: {results['failed']}")
            
            if results['failed'] == 0:
                print("\n🎉 ALL AUTOMATED TESTS PASSED!")
            else:
                print(f"\n⚠️  {results['failed']} test(s) need attention")
            
            print("\n💡 Manual verification still recommended for message alignment")
            print("   Open the browser and visually confirm messages are on correct sides")
            
            print("\n⏱️  Keeping browser open for 5 more seconds...")
            time.sleep(5)
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(5)
        
        finally:
            print("\n🔚 Closing browser...")
            browser.close()

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════╗
║           CHATAPP FIXES VERIFICATION TEST                         ║
╚══════════════════════════════════════════════════════════════════╝

Tests the 4 fixes from Nov 3 afternoon:
  1. No auto-login (login screen shows)
  2. Larger conversation box (admin panel ~300px)
  3. Message alignment (sent-by-me classes used)
  4. Logout returns to login screen

⚠️  Requirements:
   - Server running on http://localhost:5001
   - Admin account: Ken Tse / KenTse2025!
   - Playwright installed

Starting in 2 seconds...
""")
    
    time.sleep(2)
    test_fixes()
