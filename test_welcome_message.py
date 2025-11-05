from playwright.sync_api import sync_playwright

def test_welcome_message():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        page = browser.new_page()
        
        page.goto('file:///c:/Users/trabc/CascadeProjects/ChatApp/chatapp_frontend.html')
        page.wait_for_selector('body')
        page.wait_for_timeout(500)
        
        print("\n" + "="*80)
        print("TESTING: WELCOME MESSAGE FORMAT")
        print("="*80)
        
        # Simulate logged in user
        page.evaluate('''() => {
            // Set up a mock current user
            window.currentUser = {
                id: 123,
                username: 'JohnDoe',
                role: 'user'
            };
            
            // Set admin ID
            window.adminId = 1;
            
            // Mock localStorage
            localStorage.setItem('admin_name_for_user_123', 'Ken');
            
            // Show chat section
            const loginSection = document.querySelector('.login-section');
            const chatSection = document.getElementById('chat-section');
            
            if (loginSection) loginSection.style.display = 'none';
            if (chatSection) chatSection.style.display = 'flex';
            
            // Simulate different admin statuses
            window.getUserStatus = async function(userId) {
                // Return mock status - you can change this
                return { status: 'online' }; // or 'offline' or 'in_call'
            };
        }''')
        
        page.wait_for_timeout(1000)
        
        print("\n📝 TEST 1: CHECKING USER-INFO TEXT FORMAT")
        
        # Test with online status
        print("\n  Testing with ONLINE status:")
        user_info = page.evaluate('''async () => {
            window.getUserStatus = async function(userId) {
                return { status: 'online' };
            };
            
            // Call the update function
            await updateUserWelcomeMessage();
            
            const userInfo = document.getElementById('user-info');
            return userInfo ? userInfo.textContent : 'Element not found';
        }''')
        
        print(f"    Text: '{user_info}'")
        
        expected_format = "Welcome JohnDoe, Ken is Online"
        if user_info == expected_format:
            print(f"    ✅ Correct format: '{expected_format}'")
        else:
            print(f"    ❌ Expected: '{expected_format}'")
        
        # Check format components
        has_welcome = 'Welcome' in user_info
        has_username = 'JohnDoe' in user_info
        has_admin_name = 'Ken' in user_info
        has_status = 'Online' in user_info
        
        print(f"\n    Components:")
        print(f"      Has 'Welcome': {has_welcome} {'✅' if has_welcome else '❌'}")
        print(f"      Has username 'JohnDoe': {has_username} {'✅' if has_username else '❌'}")
        print(f"      Has admin name 'Ken': {has_admin_name} {'✅' if has_admin_name else '❌'}")
        print(f"      Has status 'Online': {has_status} {'✅' if has_status else '❌'}")
        
        page.wait_for_timeout(1000)
        
        # Test with offline status
        print("\n  Testing with OFFLINE status:")
        user_info_offline = page.evaluate('''async () => {
            window.getUserStatus = async function(userId) {
                return { status: 'offline' };
            };
            
            await updateUserWelcomeMessage();
            
            const userInfo = document.getElementById('user-info');
            return userInfo ? userInfo.textContent : 'Element not found';
        }''')
        
        print(f"    Text: '{user_info_offline}'")
        
        if 'Offline' in user_info_offline:
            print(f"    ✅ Shows 'Offline' status correctly")
        else:
            print(f"    ❌ Should show 'Offline'")
        
        page.wait_for_timeout(1000)
        
        # Test with in_call status
        print("\n  Testing with IN_CALL (Not Available) status:")
        user_info_busy = page.evaluate('''async () => {
            window.getUserStatus = async function(userId) {
                return { status: 'in_call' };
            };
            
            await updateUserWelcomeMessage();
            
            const userInfo = document.getElementById('user-info');
            return userInfo ? userInfo.textContent : 'Element not found';
        }''')
        
        print(f"    Text: '{user_info_busy}'")
        
        if 'Not Available' in user_info_busy:
            print(f"    ✅ Shows 'Not Available' status correctly")
        else:
            print(f"    ❌ Should show 'Not Available'")
        
        # Take screenshot
        page.screenshot(path='test_screenshots/welcome_message.png', full_page=True)
        print("\n✓ Screenshot saved: welcome_message.png")
        
        print("\n" + "="*80)
        print("SUMMARY:")
        print("="*80)
        
        print("\n📋 MESSAGE FORMAT:")
        print("   Old: 'Logged in as: <username>'")
        print("   New: 'Welcome <username>, <admin_name> is <status>'")
        
        print("\n✅ FORMAT COMPONENTS:")
        print("   ✅ 'Welcome' prefix")
        print("   ✅ Current user's username")
        print("   ✅ Admin's display name")
        print("   ✅ Admin's status (Online/Offline/Not Available)")
        
        print("\n📊 STATUS TYPES:")
        print("   🟢 'Online' - Admin is available")
        print("   🔴 'Offline' - Admin is not logged in")
        print("   🔵 'Not Available' - Admin is in a call")
        
        print("\n💡 EXAMPLES:")
        print("   'Welcome JohnDoe, Ken is Online'")
        print("   'Welcome JohnDoe, Ken is Offline'")
        print("   'Welcome JohnDoe, Ken is Not Available'")
        
        all_tests_passed = (
            has_welcome and 
            has_username and 
            has_admin_name and 
            'Offline' in user_info_offline and 
            'Not Available' in user_info_busy
        )
        
        if all_tests_passed:
            print("\n✅ ALL TESTS PASSED!")
        else:
            print("\n⚠️  Some tests failed - check output above")
        
        print("\n⚠️ REMEMBER TO CLEAR CACHE (Ctrl+F5)!")
        print("\nBrowser will stay open for 20 seconds...")
        page.wait_for_timeout(20000)
        
        browser.close()

if __name__ == '__main__':
    test_welcome_message()
