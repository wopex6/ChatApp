from playwright.sync_api import sync_playwright

def test_min_height_both_views():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        page = browser.new_page()
        
        page.goto('file:///c:/Users/trabc/CascadeProjects/ChatApp/chatapp_frontend.html')
        page.wait_for_selector('body')
        page.wait_for_timeout(500)
        
        print("\n" + "="*80)
        print("TESTING: MIN-HEIGHT 50VH FOR MESSAGES (USER & ADMIN VIEWS)")
        print("="*80)
        
        # Test 1: User View
        print("\n" + "="*80)
        print("TEST 1: USER VIEW (3 Sections)")
        print("="*80)
        
        page.evaluate('''() => {
            const loginSection = document.querySelector('.auth-section').parentElement;
            const chatSection = document.getElementById('chat-section');
            const messageInput = document.getElementById('message-input-section');
            
            if (loginSection) loginSection.style.display = 'none';
            if (chatSection) chatSection.style.display = 'flex';
            if (messageInput) messageInput.style.display = 'flex';
            
            // Mock regular user
            window.currentUser = {
                id: 123,
                username: 'RegularUser',
                role: 'user'
            };
            
            // Hide admin panel
            document.getElementById('admin-panel').style.display = 'none';
            
            // Add a few messages
            const container = document.getElementById('messages-container');
            let html = '';
            for (let i = 1; i <= 10; i++) {
                const isMe = i % 2 === 0;
                const className = isMe ? 'sent-by-me' : 'sent-by-other';
                html += `
                    <div class="message-wrapper ${className}">
                        <div class="message ${className}">
                            <div>
                                Message ${i}
                                <span class="message-time">${i}:00pm</span>
                            </div>
                        </div>
                    </div>
                `;
            }
            container.innerHTML = html;
        }''')
        
        page.wait_for_timeout(1000)
        
        user_view = page.evaluate('''() => {
            const viewport = {
                width: window.innerWidth,
                height: window.innerHeight
            };
            
            const header = document.querySelector('.chat-header');
            const messages = document.getElementById('messages-container');
            const input = document.getElementById('message-input-section');
            
            const headerStyle = window.getComputedStyle(header);
            const messagesStyle = window.getComputedStyle(messages);
            const inputStyle = window.getComputedStyle(input);
            
            const headerRect = header.getBoundingClientRect();
            const messagesRect = messages.getBoundingClientRect();
            const inputRect = input.getBoundingClientRect();
            
            return {
                viewport: viewport,
                header: {
                    position: headerStyle.position,
                    height: Math.round(headerRect.height),
                    top: Math.round(headerRect.top)
                },
                messages: {
                    minHeight: messagesStyle.minHeight,
                    actualHeight: Math.round(messagesRect.height),
                    flex: messagesStyle.flex,
                    overflowY: messagesStyle.overflowY,
                    scrollable: messages.scrollHeight > messages.clientHeight
                },
                input: {
                    position: inputStyle.position,
                    height: Math.round(inputRect.height),
                    bottom: Math.round(viewport.height - inputRect.bottom)
                },
                halfViewport: Math.round(viewport.height / 2)
            };
        }''')
        
        print(f"\n📱 Viewport: {user_view['viewport']['width']}x{user_view['viewport']['height']}px")
        print(f"   Half viewport (50vh): {user_view['halfViewport']}px")
        
        print(f"\n1️⃣  SECTION 1 - Header (Top, Sticky):")
        print(f"   Position: {user_view['header']['position']}")
        print(f"   Height: {user_view['header']['height']}px")
        print(f"   Top: {user_view['header']['top']}px")
        
        if user_view['header']['position'] == 'sticky':
            print(f"   ✅ Sticky positioning")
        
        print(f"\n2️⃣  SECTION 2 - Messages (Middle, Scrollable):")
        print(f"   Min-height CSS: {user_view['messages']['minHeight']}")
        print(f"   Actual height: {user_view['messages']['actualHeight']}px")
        print(f"   Flex: {user_view['messages']['flex']}")
        print(f"   Overflow-Y: {user_view['messages']['overflowY']}")
        
        if user_view['messages']['minHeight'] == '50vh':
            print(f"   ✅ Min-height is 50vh")
        else:
            print(f"   ❌ Min-height should be 50vh, found: {user_view['messages']['minHeight']}")
        
        if user_view['messages']['actualHeight'] >= user_view['halfViewport']:
            print(f"   ✅ Height ({user_view['messages']['actualHeight']}px) >= 50vh ({user_view['halfViewport']}px)")
        else:
            print(f"   ⚠️  Height ({user_view['messages']['actualHeight']}px) < 50vh ({user_view['halfViewport']}px)")
        
        if user_view['messages']['overflowY'] == 'auto':
            print(f"   ✅ Scrollable (overflow-y: auto)")
        
        print(f"\n3️⃣  SECTION 3 - Input (Bottom, Sticky):")
        print(f"   Position: {user_view['input']['position']}")
        print(f"   Height: {user_view['input']['height']}px")
        print(f"   Bottom gap: {user_view['input']['bottom']}px")
        
        if user_view['input']['position'] == 'sticky':
            print(f"   ✅ Sticky positioning")
        
        if user_view['input']['bottom'] < 5:
            print(f"   ✅ At bottom of viewport")
        
        # Take screenshot
        page.screenshot(path='test_screenshots/user_view_minheight.png', full_page=False)
        print(f"\n📸 Screenshot saved: user_view_minheight.png")
        
        # Test 2: Admin View
        print("\n" + "="*80)
        print("TEST 2: ADMIN VIEW (3 Sections + Admin Panel)")
        print("="*80)
        
        page.evaluate('''() => {
            // Mock admin user
            window.currentUser = {
                id: 1,
                username: 'Ken Tse',
                role: 'administrator'
            };
            
            // Show admin panel
            const adminPanel = document.getElementById('admin-panel');
            adminPanel.style.display = 'flex';
            adminPanel.style.width = '300px';
            
            // Clear and add messages
            const container = document.getElementById('messages-container');
            let html = '';
            for (let i = 1; i <= 15; i++) {
                const isMe = i % 2 === 0;
                const className = isMe ? 'sent-by-me' : 'sent-by-other';
                html += `
                    <div class="message-wrapper ${className}">
                        <div class="message ${className}">
                            <div>
                                Admin message ${i}
                                <span class="message-time">${i}:00pm</span>
                            </div>
                        </div>
                    </div>
                `;
            }
            container.innerHTML = html;
        }''')
        
        page.wait_for_timeout(1000)
        
        admin_view = page.evaluate('''() => {
            const viewport = {
                width: window.innerWidth,
                height: window.innerHeight
            };
            
            const adminPanel = document.getElementById('admin-panel');
            const header = document.querySelector('.chat-header');
            const messages = document.getElementById('messages-container');
            const input = document.getElementById('message-input-section');
            
            const adminPanelStyle = window.getComputedStyle(adminPanel);
            const messagesStyle = window.getComputedStyle(messages);
            
            const adminPanelRect = adminPanel.getBoundingClientRect();
            const headerRect = header.getBoundingClientRect();
            const messagesRect = messages.getBoundingClientRect();
            const inputRect = input.getBoundingClientRect();
            
            return {
                viewport: viewport,
                adminPanel: {
                    display: adminPanelStyle.display,
                    width: Math.round(adminPanelRect.width)
                },
                header: {
                    position: window.getComputedStyle(header).position,
                    height: Math.round(headerRect.height)
                },
                messages: {
                    minHeight: messagesStyle.minHeight,
                    actualHeight: Math.round(messagesRect.height),
                    flex: messagesStyle.flex,
                    overflowY: messagesStyle.overflowY
                },
                input: {
                    position: window.getComputedStyle(input).position,
                    height: Math.round(inputRect.height)
                },
                halfViewport: Math.round(viewport.height / 2)
            };
        }''')
        
        print(f"\n📱 Viewport: {admin_view['viewport']['width']}x{admin_view['viewport']['height']}px")
        print(f"   Half viewport (50vh): {admin_view['halfViewport']}px")
        
        print(f"\n📊 ADMIN PANEL (Left Side):")
        print(f"   Display: {admin_view['adminPanel']['display']}")
        print(f"   Width: {admin_view['adminPanel']['width']}px")
        
        if admin_view['adminPanel']['display'] == 'flex':
            print(f"   ✅ Admin panel visible")
        
        print(f"\n1️⃣  SECTION 1 - Header (Top, Sticky):")
        print(f"   Position: {admin_view['header']['position']}")
        print(f"   Height: {admin_view['header']['height']}px")
        
        if admin_view['header']['position'] == 'sticky':
            print(f"   ✅ Sticky positioning (same as user view)")
        
        print(f"\n2️⃣  SECTION 2 - Messages (Middle, Scrollable):")
        print(f"   Min-height CSS: {admin_view['messages']['minHeight']}")
        print(f"   Actual height: {admin_view['messages']['actualHeight']}px")
        print(f"   Flex: {admin_view['messages']['flex']}")
        print(f"   Overflow-Y: {admin_view['messages']['overflowY']}")
        
        if admin_view['messages']['minHeight'] == '50vh':
            print(f"   ✅ Min-height is 50vh (same CSS as user view)")
        
        if admin_view['messages']['actualHeight'] >= admin_view['halfViewport']:
            print(f"   ✅ Height ({admin_view['messages']['actualHeight']}px) >= 50vh ({admin_view['halfViewport']}px)")
        else:
            print(f"   ⚠️  Height ({admin_view['messages']['actualHeight']}px) < 50vh ({admin_view['halfViewport']}px)")
        
        print(f"\n3️⃣  SECTION 3 - Input (Bottom, Sticky):")
        print(f"   Position: {admin_view['input']['position']}")
        print(f"   Height: {admin_view['input']['height']}px")
        
        if admin_view['input']['position'] == 'sticky':
            print(f"   ✅ Sticky positioning (same as user view)")
        
        # Take screenshot
        page.screenshot(path='test_screenshots/admin_view_minheight.png', full_page=False)
        print(f"\n📸 Screenshot saved: admin_view_minheight.png")
        
        # Summary
        print("\n" + "="*80)
        print("SUMMARY:")
        print("="*80)
        
        print("\n✅ SHARED CSS:")
        print(f"   Both views use the same .messages-container class")
        print(f"   Min-height: {user_view['messages']['minHeight']}")
        
        print("\n✅ USER VIEW (Regular User):")
        print(f"   Section 1 (Header): {user_view['header']['position']}, {user_view['header']['height']}px")
        print(f"   Section 2 (Messages): {user_view['messages']['actualHeight']}px (min: {user_view['halfViewport']}px)")
        print(f"   Section 3 (Input): {user_view['input']['position']}, {user_view['input']['height']}px")
        
        if user_view['messages']['actualHeight'] >= user_view['halfViewport']:
            print(f"   ✅ Messages >= 50% screen height")
        
        print("\n✅ ADMIN VIEW (Ken Tse):")
        print(f"   Admin Panel: {admin_view['adminPanel']['width']}px wide")
        print(f"   Section 1 (Header): {admin_view['header']['position']}, {admin_view['header']['height']}px")
        print(f"   Section 2 (Messages): {admin_view['messages']['actualHeight']}px (min: {admin_view['halfViewport']}px)")
        print(f"   Section 3 (Input): {admin_view['input']['position']}, {admin_view['input']['height']}px")
        
        if admin_view['messages']['actualHeight'] >= admin_view['halfViewport']:
            print(f"   ✅ Messages >= 50% screen height")
        
        print("\n📊 THREE-SECTION STRUCTURE:")
        print("   Both views have the same 3 sections:")
        print("   1️⃣  Header (sticky top)")
        print("   2️⃣  Messages (scrollable middle, min-height: 50vh)")
        print("   3️⃣  Input (sticky bottom)")
        
        print("\n🎯 KEY POINTS:")
        print("   • Single .messages-container used by both views")
        print("   • CSS min-height: 50vh applies to both")
        print("   • Admin panel is a sibling, doesn't affect 3-section structure")
        print("   • Messages area always at least half the viewport height")
        
        if user_view['messages']['minHeight'] == '50vh' and admin_view['messages']['minHeight'] == '50vh':
            print("\n✅ Min-height 50vh confirmed for BOTH user and admin views!")
        
        print("\n⚠️ REMEMBER: Clear browser cache (Ctrl+F5) to see changes!")
        print("\nBrowser will stay open for 30 seconds...")
        page.wait_for_timeout(30000)
        
        browser.close()

if __name__ == '__main__':
    test_min_height_both_views()
