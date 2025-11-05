from playwright.sync_api import sync_playwright

def test_is_and_minheight():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        page = browser.new_page()
        
        page.goto('file:///c:/Users/trabc/CascadeProjects/ChatApp/chatapp_frontend.html')
        page.wait_for_selector('body')
        page.wait_for_timeout(500)
        
        print("\n" + "="*80)
        print("TESTING: 1) ADD 'IS' AFTER ADMIN, 2) MIN-HEIGHT 50VH FOR MESSAGES")
        print("="*80)
        
        # Setup
        page.evaluate('''() => {
            const loginSection = document.querySelector('.login-section');
            const chatSection = document.getElementById('chat-section');
            const messageInput = document.getElementById('message-input-section');
            
            if (loginSection) loginSection.style.display = 'none';
            if (chatSection) chatSection.style.display = 'flex';
            if (messageInput) messageInput.style.display = 'flex';
            
            // Mock user
            window.currentUser = {
                id: 123,
                username: 'JohnDoe',
                role: 'user'
            };
            window.adminId = 1;
            localStorage.setItem('admin_name_for_user_123', 'Ken');
            
            // Add some messages
            const container = document.getElementById('messages-container');
            container.innerHTML = `
                <div class="message-wrapper sent-by-other">
                    <div class="message sent-by-other">
                        <div>
                            Hello!
                            <span class="message-time">2:30pm</span>
                        </div>
                    </div>
                </div>
            `;
        }''')
        
        page.wait_for_timeout(1000)
        
        # Test 1: Check "is" is added for online status
        print("\n📝 TEST 1: WELCOME MESSAGE WITH 'IS'")
        
        print("\n  Testing ONLINE status (should show 'is'):")
        msg_online = page.evaluate('''async () => {
            window.getUserStatus = async function() {
                return { status: 'online' };
            };
            
            await updateUserWelcomeMessage();
            
            const userInfo = document.getElementById('user-info');
            return userInfo ? userInfo.textContent : 'Element not found';
        }''')
        
        print(f"    Text: '{msg_online}'")
        
        expected_online = "Welcome JohnDoe, Ken is"
        if msg_online == expected_online:
            print(f"    ✅ Correct: '{expected_online}'")
        else:
            print(f"    ❌ Expected: '{expected_online}'")
        
        # Check components
        has_welcome = 'Welcome' in msg_online
        has_username = 'JohnDoe' in msg_online
        has_admin = 'Ken' in msg_online
        has_is = msg_online.endswith(' is')
        
        print(f"\n    Components:")
        print(f"      'Welcome': {has_welcome} {'✅' if has_welcome else '❌'}")
        print(f"      Username 'JohnDoe': {has_username} {'✅' if has_username else '❌'}")
        print(f"      Admin 'Ken': {has_admin} {'✅' if has_admin else '❌'}")
        print(f"      Ends with ' is': {has_is} {'✅' if has_is else '❌'}")
        
        # Test offline
        print("\n  Testing OFFLINE status:")
        msg_offline = page.evaluate('''async () => {
            window.getUserStatus = async function() {
                return { status: 'offline' };
            };
            
            await updateUserWelcomeMessage();
            
            const userInfo = document.getElementById('user-info');
            return userInfo ? userInfo.textContent : 'Element not found';
        }''')
        
        print(f"    Text: '{msg_offline}'")
        expected_offline = "Welcome JohnDoe, Ken is Offline"
        if msg_offline == expected_offline:
            print(f"    ✅ Correct: '{expected_offline}'")
        else:
            print(f"    ❌ Expected: '{expected_offline}'")
        
        # Test not available
        print("\n  Testing NOT AVAILABLE status:")
        msg_busy = page.evaluate('''async () => {
            window.getUserStatus = async function() {
                return { status: 'in_call' };
            };
            
            await updateUserWelcomeMessage();
            
            const userInfo = document.getElementById('user-info');
            return userInfo ? userInfo.textContent : 'Element not found';
        }''')
        
        print(f"    Text: '{msg_busy}'")
        expected_busy = "Welcome JohnDoe, Ken is Not Available"
        if msg_busy == expected_busy:
            print(f"    ✅ Correct: '{expected_busy}'")
        else:
            print(f"    ❌ Expected: '{expected_busy}'")
        
        # Test 2: Check messages container min-height
        print("\n📏 TEST 2: MESSAGES CONTAINER MIN-HEIGHT")
        
        container_props = page.evaluate('''() => {
            const container = document.getElementById('messages-container');
            if (!container) return { exists: false };
            
            const style = window.getComputedStyle(container);
            const rect = container.getBoundingClientRect();
            const viewportHeight = window.innerHeight;
            const halfViewportHeight = viewportHeight / 2;
            
            return {
                exists: true,
                minHeight: style.minHeight,
                actualHeight: Math.round(rect.height),
                viewportHeight: Math.round(viewportHeight),
                halfViewportHeight: Math.round(halfViewportHeight),
                meetsMinimum: rect.height >= halfViewportHeight
            };
        }''')
        
        if container_props['exists']:
            print(f"  Min-height CSS: {container_props['minHeight']}")
            print(f"  Viewport height: {container_props['viewportHeight']}px")
            print(f"  Half viewport (50vh): {container_props['halfViewportHeight']}px")
            print(f"  Actual container height: {container_props['actualHeight']}px")
            
            if container_props['minHeight'] == '50vh':
                print(f"  ✅ CSS min-height is 50vh")
            else:
                print(f"  ❌ CSS min-height should be 50vh, found: {container_props['minHeight']}")
            
            if container_props['meetsMinimum']:
                print(f"  ✅ Container meets minimum height (≥50% of screen)")
            else:
                print(f"  ⚠️  Container is smaller than 50% of screen")
        
        # Test 3: Test resizing window
        print("\n🔄 TEST 3: WINDOW RESIZE BEHAVIOR")
        
        # Get current size
        original_size = page.viewport_size
        print(f"  Original window size: {original_size['width']}x{original_size['height']}px")
        
        # Resize to smaller
        page.set_viewport_size({"width": 800, "height": 600})
        page.wait_for_timeout(500)
        
        print(f"  Resized to: 800x600px")
        
        # Check container still meets minimum
        container_after_resize = page.evaluate('''() => {
            const container = document.getElementById('messages-container');
            const rect = container.getBoundingClientRect();
            const viewportHeight = window.innerHeight;
            const halfViewportHeight = viewportHeight / 2;
            
            return {
                height: Math.round(rect.height),
                halfViewportHeight: Math.round(halfViewportHeight),
                meetsMinimum: rect.height >= halfViewportHeight,
                percentage: Math.round((rect.height / viewportHeight) * 100)
            };
        }''')
        
        print(f"  New viewport height: 600px")
        print(f"  New half viewport: {container_after_resize['halfViewportHeight']}px")
        print(f"  Container height: {container_after_resize['height']}px")
        print(f"  Percentage of screen: {container_after_resize['percentage']}%")
        
        if container_after_resize['meetsMinimum']:
            print(f"  ✅ Container still ≥50% of screen height")
        else:
            print(f"  ❌ Container smaller than 50% after resize")
        
        # Test 4: Check fixed positioning
        print("\n📌 TEST 4: FIXED HEADER AND INPUT")
        
        fixed_check = page.evaluate('''() => {
            const header = document.querySelector('.chat-header');
            const input = document.getElementById('message-input-section');
            
            const headerStyle = header ? window.getComputedStyle(header) : null;
            const inputStyle = input ? window.getComputedStyle(input) : null;
            
            return {
                header: {
                    exists: !!header,
                    position: headerStyle ? headerStyle.position : 'N/A',
                    top: headerStyle ? headerStyle.top : 'N/A',
                    zIndex: headerStyle ? headerStyle.zIndex : 'N/A'
                },
                input: {
                    exists: !!input,
                    position: inputStyle ? inputStyle.position : 'N/A',
                    bottom: inputStyle ? inputStyle.bottom : 'N/A',
                    zIndex: inputStyle ? inputStyle.zIndex : 'N/A'
                }
            };
        }''')
        
        print(f"\n  Header (1st section):")
        print(f"    Position: {fixed_check['header']['position']}")
        print(f"    Top: {fixed_check['header']['top']}")
        print(f"    Z-index: {fixed_check['header']['zIndex']}")
        if fixed_check['header']['position'] == 'sticky':
            print(f"    ✅ Fixed to top")
        else:
            print(f"    ⚠️  Should be sticky")
        
        print(f"\n  Input (3rd section):")
        print(f"    Position: {fixed_check['input']['position']}")
        print(f"    Bottom: {fixed_check['input']['bottom']}")
        print(f"    Z-index: {fixed_check['input']['zIndex']}")
        if fixed_check['input']['position'] == 'sticky':
            print(f"    ✅ Fixed to bottom")
        else:
            print(f"    ⚠️  Should be sticky")
        
        # Take screenshots
        page.screenshot(path='test_screenshots/is_and_minheight.png', full_page=True)
        print("\n✓ Screenshot saved: is_and_minheight.png")
        
        print("\n" + "="*80)
        print("SUMMARY:")
        print("="*80)
        
        print("\n1. WELCOME MESSAGE FORMAT:")
        print(f"   Online:        '{msg_online}'")
        print(f"   Offline:       '{msg_offline}'")
        print(f"   Not Available: '{msg_busy}'")
        
        if has_is and msg_online.endswith(' is'):
            print(f"   ✅ 'is' added after admin name when online")
        else:
            print(f"   ❌ 'is' not correctly added")
        
        print("\n2. MESSAGES CONTAINER:")
        print(f"   Min-height: {container_props['minHeight']}")
        print(f"   Height: {container_props['actualHeight']}px")
        print(f"   Viewport: {container_props['viewportHeight']}px")
        
        if container_props['minHeight'] == '50vh':
            print(f"   ✅ Min-height set to 50vh")
        else:
            print(f"   ❌ Min-height should be 50vh")
        
        print("\n3. FIXED SECTIONS:")
        print(f"   Header: {fixed_check['header']['position']}")
        print(f"   Input: {fixed_check['input']['position']}")
        
        if fixed_check['header']['position'] == 'sticky' and fixed_check['input']['position'] == 'sticky':
            print(f"   ✅ Both sections fixed (sticky)")
        else:
            print(f"   ⚠️  Sections should be sticky")
        
        print("\n⚠️ REMEMBER TO CLEAR CACHE (Ctrl+F5)!")
        print("\nBrowser will stay open for 30 seconds...")
        page.wait_for_timeout(30000)
        
        browser.close()

if __name__ == '__main__':
    test_is_and_minheight()
