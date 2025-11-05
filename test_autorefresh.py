"""
Playwright test for ChatApp auto-refresh functionality
Tests that messages appear automatically for receivers without manual refresh
"""

from playwright.sync_api import sync_playwright, expect
import time

BASE_URL = "http://localhost:5001"

def test_auto_refresh():
    """Test that receiver sees new messages automatically"""
    
    with sync_playwright() as p:
        print("\n🧪 Starting Auto-Refresh Test...")
        print("=" * 60)
        
        # Launch two browsers (two users)
        browser1 = p.chromium.launch(headless=False)
        browser2 = p.chromium.launch(headless=False)
        
        context1 = browser1.new_context()
        context2 = browser2.new_context()
        
        page_admin = context1.new_page()
        page_user = context2.new_page()
        
        try:
            # ==== Test 1: Regular User Auto-Refresh ====
            print("\n📝 Test 1: Regular User Should Auto-Refresh Messages")
            print("-" * 60)
            
            # User logs in
            print("1. User logging in...")
            page_user.goto(BASE_URL)
            page_user.fill("#login-username", "testuser1")
            page_user.fill("#login-password", "password123")
            page_user.click("button:has-text('Login')")
            time.sleep(2)
            
            # Get initial message count
            page_user.wait_for_selector("#messages-container")
            initial_messages = page_user.locator(".message").count()
            print(f"   Initial message count: {initial_messages}")
            
            # Admin logs in
            print("\n2. Admin (Ken Tse) logging in...")
            page_admin.goto(BASE_URL)
            page_admin.fill("#login-username", "Ken Tse")
            page_admin.fill("#login-password", "KenTse2025!")
            page_admin.click("button:has-text('Login')")
            time.sleep(2)
            
            # Admin selects the test user
            print("3. Admin selecting user...")
            page_admin.wait_for_selector(".user-item")
            user_items = page_admin.locator(".user-item")
            
            # Find and click testuser1
            for i in range(user_items.count()):
                item = user_items.nth(i)
                if "testuser1" in item.text_content().lower():
                    item.click()
                    break
            time.sleep(1)
            
            # Admin sends a message
            test_message = f"Test auto-refresh message at {time.time()}"
            print(f"4. Admin sending message: '{test_message}'")
            page_admin.fill("#message-input", test_message)
            page_admin.click("button:has-text('Send')")
            time.sleep(1)
            
            # Wait for auto-refresh (should happen within 5 seconds)
            print("5. Waiting for user to receive message (max 6 seconds)...")
            start_time = time.time()
            message_received = False
            
            for i in range(12):  # Check every 0.5 seconds for 6 seconds
                time.sleep(0.5)
                current_messages = page_user.locator(".message").count()
                if current_messages > initial_messages:
                    elapsed = time.time() - start_time
                    print(f"   ✅ Message received after {elapsed:.1f} seconds!")
                    message_received = True
                    
                    # Verify the message content
                    last_message = page_user.locator(".message").last
                    if test_message in last_message.text_content():
                        print(f"   ✅ Message content verified: '{test_message}'")
                    else:
                        print(f"   ⚠️  Message content mismatch")
                    break
                else:
                    print(f"   ⏳ Checking... ({i+1}/12) - Messages: {current_messages}")
            
            if not message_received:
                print(f"   ❌ FAIL: Message NOT received after 6 seconds!")
                print(f"   Initial: {initial_messages}, Current: {page_user.locator('.message').count()}")
            
            # ==== Test 2: Admin Side Auto-Refresh ====
            print("\n📝 Test 2: Admin Should See User Reply Auto-Refresh")
            print("-" * 60)
            
            # Get admin's initial message count
            admin_initial = page_admin.locator(".message").count()
            print(f"   Admin initial messages: {admin_initial}")
            
            # User sends reply
            user_reply = f"Reply from user at {time.time()}"
            print(f"1. User sending reply: '{user_reply}'")
            page_user.fill("#message-input", user_reply)
            page_user.click("button:has-text('Send')")
            time.sleep(1)
            
            # Check if admin receives it (admin has interval, but also refreshes on send)
            print("2. Checking if admin receives reply (max 6 seconds)...")
            admin_received = False
            
            for i in range(12):
                time.sleep(0.5)
                current_admin_messages = page_admin.locator(".message").count()
                if current_admin_messages > admin_initial:
                    elapsed = time.time() - start_time
                    print(f"   ✅ Admin received message after {elapsed:.1f} seconds!")
                    admin_received = True
                    break
                else:
                    print(f"   ⏳ Checking... ({i+1}/12) - Messages: {current_admin_messages}")
            
            if not admin_received:
                print(f"   ❌ FAIL: Admin did NOT receive message!")
            
            # ==== Test 3: Check Interval Times ====
            print("\n📝 Test 3: Verify Auto-Refresh Intervals")
            print("-" * 60)
            
            # Admin sends another message
            test_message2 = f"Second test message at {time.time()}"
            print(f"1. Admin sending second message: '{test_message2}'")
            page_admin.fill("#message-input", test_message2)
            page_admin.click("button:has-text('Send')")
            
            # Track refresh timing
            print("2. Monitoring refresh timing...")
            user_msg_count = page_user.locator(".message").count()
            refresh_detected = False
            
            for i in range(11):  # Check for ~5.5 seconds
                time.sleep(0.5)
                new_count = page_user.locator(".message").count()
                if new_count > user_msg_count:
                    print(f"   ✅ Refresh detected at {(i+1)*0.5} seconds")
                    refresh_detected = True
                    break
            
            if refresh_detected and (i+1)*0.5 <= 5.5:
                print(f"   ✅ Auto-refresh working within expected time (< 5.5s)")
            else:
                print(f"   ❌ Auto-refresh too slow or not working")
            
            # ==== Summary ====
            print("\n" + "=" * 60)
            print("📊 TEST SUMMARY")
            print("=" * 60)
            print(f"Test 1 (User Auto-Refresh): {'✅ PASS' if message_received else '❌ FAIL'}")
            print(f"Test 2 (Admin Auto-Refresh): {'✅ PASS' if admin_received else '❌ FAIL'}")
            print(f"Test 3 (Timing Check): {'✅ PASS' if refresh_detected else '❌ FAIL'}")
            
            if message_received and admin_received and refresh_detected:
                print("\n🎉 ALL TESTS PASSED!")
            else:
                print("\n⚠️  SOME TESTS FAILED - Auto-refresh needs fixing")
            
            print("\n💡 Keeping browsers open for 5 seconds for visual inspection...")
            time.sleep(5)
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(5)
        
        finally:
            print("\n🔚 Closing browsers...")
            browser1.close()
            browser2.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 ChatApp Auto-Refresh Test Suite")
    print("=" * 60)
    print("\n⚠️  Requirements:")
    print("   1. ChatApp server running on http://localhost:5001")
    print("   2. User 'testuser1' with password 'password123' exists")
    print("   3. Admin 'Ken Tse' with password 'KenTse2025!'")
    print("   4. Playwright installed: pip install playwright")
    print("   5. Browsers installed: playwright install")
    print("\nStarting tests in 2 seconds...")
    time.sleep(2)
    
    test_auto_refresh()
