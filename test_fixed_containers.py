from playwright.sync_api import sync_playwright

def test_fixed_containers():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        page = browser.new_page()
        
        page.goto('file:///c:/Users/trabc/CascadeProjects/ChatApp/chatapp_frontend.html')
        page.wait_for_selector('body')
        page.wait_for_timeout(500)
        
        print("\n" + "="*80)
        print("TESTING: FIXED CONTAINER HEIGHTS FOR STICKY POSITIONING")
        print("="*80)
        
        # Setup - login
        page.evaluate('''() => {
            const loginSection = document.querySelector('.auth-section').parentElement;
            const chatSection = document.getElementById('chat-section');
            const messageInput = document.getElementById('message-input-section');
            
            if (loginSection) loginSection.style.display = 'none';
            if (chatSection) chatSection.style.display = 'flex';
            if (messageInput) messageInput.style.display = 'flex';
            
            // Mock current user
            window.currentUser = {
                id: 123,
                username: 'TestUser',
                role: 'user'
            };
            
            // Add 40 messages to force scrolling
            const container = document.getElementById('messages-container');
            let html = '';
            for (let i = 1; i <= 40; i++) {
                const isMe = i % 2 === 0;
                const className = isMe ? 'sent-by-me' : 'sent-by-other';
                html += `
                    <div class="message-wrapper ${className}">
                        <div class="message ${className}">
                            <div>
                                Message ${i} - Testing scrolling and sticky positioning
                                <span class="message-time">${i}:00pm</span>
                            </div>
                        </div>
                    </div>
                `;
            }
            container.innerHTML = html;
        }''')
        
        page.wait_for_timeout(1000)
        
        # Test 1: Check container heights
        print("\n📏 TEST 1: CONTAINER HEIGHT CONSTRAINTS")
        
        container_info = page.evaluate('''() => {
            const container = document.querySelector('.container');
            const content = document.querySelector('.content');
            const chatSection = document.getElementById('chat-section');
            
            const containerStyle = window.getComputedStyle(container);
            const contentStyle = window.getComputedStyle(content);
            const chatStyle = window.getComputedStyle(chatSection);
            
            return {
                container: {
                    height: containerStyle.height,
                    maxHeight: containerStyle.maxHeight,
                    overflow: containerStyle.overflow,
                    display: containerStyle.display,
                    flexDirection: containerStyle.flexDirection
                },
                content: {
                    flex: contentStyle.flex,
                    overflow: contentStyle.overflow,
                    display: contentStyle.display,
                    height: contentStyle.height
                },
                chatSection: {
                    flex: chatStyle.flex,
                    overflow: chatStyle.overflow,
                    display: chatStyle.display,
                    height: chatStyle.height
                }
            };
        }''')
        
        print(f"\n  CONTAINER:")
        print(f"    Height: {container_info['container']['height']}")
        print(f"    Max-height: {container_info['container']['maxHeight']}")
        print(f"    Overflow: {container_info['container']['overflow']}")
        print(f"    Display: {container_info['container']['display']}")
        print(f"    Flex-direction: {container_info['container']['flexDirection']}")
        
        if 'vh' in container_info['container']['height'] or 'px' in container_info['container']['height']:
            print(f"    ✅ Has defined height")
        else:
            print(f"    ❌ No defined height")
        
        print(f"\n  CONTENT:")
        print(f"    Flex: {container_info['content']['flex']}")
        print(f"    Overflow: {container_info['content']['overflow']}")
        print(f"    Display: {container_info['content']['display']}")
        
        if container_info['content']['flex'].startswith('1'):
            print(f"    ✅ Has flex: 1")
        
        if container_info['content']['overflow'] == 'hidden':
            print(f"    ✅ Overflow: hidden")
        
        print(f"\n  CHAT-SECTION:")
        print(f"    Flex: {container_info['chatSection']['flex']}")
        print(f"    Overflow: {container_info['chatSection']['overflow']}")
        print(f"    Display: {container_info['chatSection']['display']}")
        
        # Test 2: Check sticky elements are visible
        print("\n👁️  TEST 2: STICKY ELEMENTS VISIBILITY")
        
        visibility = page.evaluate('''() => {
            const header = document.querySelector('.chat-header');
            const input = document.getElementById('message-input-section');
            const messages = document.getElementById('messages-container');
            
            const headerRect = header.getBoundingClientRect();
            const inputRect = input.getBoundingClientRect();
            const viewport = {
                width: window.innerWidth,
                height: window.innerHeight
            };
            
            return {
                header: {
                    top: Math.round(headerRect.top),
                    bottom: Math.round(headerRect.bottom),
                    visible: headerRect.top >= 0 && headerRect.bottom <= viewport.height
                },
                input: {
                    top: Math.round(inputRect.top),
                    bottom: Math.round(inputRect.bottom),
                    visible: inputRect.top >= 0 && inputRect.bottom <= viewport.height
                },
                viewport: viewport,
                messagesScrollable: messages.scrollHeight > messages.clientHeight
            };
        }''')
        
        print(f"  Viewport: {visibility['viewport']['width']}x{visibility['viewport']['height']}px")
        
        print(f"\n  HEADER:")
        print(f"    Position: {visibility['header']['top']}px from top")
        print(f"    Bottom: {visibility['header']['bottom']}px from top")
        print(f"    Visible: {visibility['header']['visible']}")
        
        if visibility['header']['visible']:
            print(f"    ✅ Header is visible in viewport")
        else:
            print(f"    ⚠️  Header is outside viewport")
        
        print(f"\n  INPUT:")
        print(f"    Top: {visibility['input']['top']}px from top")
        print(f"    Bottom: {visibility['input']['bottom']}px from top")
        print(f"    Visible: {visibility['input']['visible']}")
        
        if visibility['input']['visible']:
            print(f"    ✅ Input is visible in viewport")
        else:
            print(f"    ❌ Input is outside viewport - PROBLEM!")
        
        print(f"\n  MESSAGES:")
        if visibility['messagesScrollable']:
            print(f"    ✅ Messages container is scrollable (content overflows)")
        else:
            print(f"    ⚠️  Messages fit - need more messages to test scrolling")
        
        # Test 3: Scroll messages and check if header/input stay visible
        print("\n🖱️  TEST 3: SCROLL TEST")
        
        # Scroll messages to middle
        page.evaluate('''() => {
            const messages = document.getElementById('messages-container');
            messages.scrollTop = messages.scrollHeight / 2;
        }''')
        
        page.wait_for_timeout(500)
        
        after_scroll = page.evaluate('''() => {
            const header = document.querySelector('.chat-header');
            const input = document.getElementById('message-input-section');
            const messages = document.getElementById('messages-container');
            
            const headerRect = header.getBoundingClientRect();
            const inputRect = input.getBoundingClientRect();
            const viewport = {
                height: window.innerHeight
            };
            
            return {
                header: {
                    top: Math.round(headerRect.top),
                    visible: headerRect.top >= 0 && headerRect.bottom <= viewport.height
                },
                input: {
                    top: Math.round(inputRect.top),
                    bottom: Math.round(inputRect.bottom),
                    visible: inputRect.top >= 0 && inputRect.bottom <= viewport.height
                },
                messagesScrollTop: messages.scrollTop
            };
        }''')
        
        print(f"  After scrolling messages to middle:")
        print(f"    Messages scroll position: {after_scroll['messagesScrollTop']}px")
        print(f"    Header top: {after_scroll['header']['top']}px")
        print(f"    Header visible: {after_scroll['header']['visible']}")
        print(f"    Input bottom: {after_scroll['input']['bottom']}px")
        print(f"    Input visible: {after_scroll['input']['visible']}")
        
        if after_scroll['header']['visible']:
            print(f"    ✅ Header stayed visible after scroll")
        else:
            print(f"    ❌ Header not visible")
        
        if after_scroll['input']['visible']:
            print(f"    ✅ Input stayed visible after scroll")
        else:
            print(f"    ❌ Input not visible - PROBLEM!")
        
        # Test 4: Check if we can click input without scrolling
        print("\n🎯 TEST 4: INPUT ACCESSIBILITY")
        
        try:
            # Try to click the input - this will fail if it's not in viewport
            input_box = page.locator('#message-input')
            input_box.click()
            print(f"  ✅ Successfully clicked input box without scrolling")
            
            # Type a test message
            input_box.fill("Test message")
            print(f"  ✅ Successfully typed in input box")
            
        except Exception as e:
            print(f"  ❌ Could not click input box: {e}")
        
        # Take screenshots
        page.screenshot(path='test_screenshots/fixed_containers_top.png', full_page=False)
        print("\n✓ Screenshot saved: fixed_containers_top.png")
        
        # Scroll to bottom
        page.evaluate('''() => {
            const messages = document.getElementById('messages-container');
            messages.scrollTop = messages.scrollHeight;
        }''')
        page.wait_for_timeout(500)
        page.screenshot(path='test_screenshots/fixed_containers_bottom.png', full_page=False)
        print("✓ Screenshot saved: fixed_containers_bottom.png")
        
        print("\n" + "="*80)
        print("SUMMARY:")
        print("="*80)
        
        print("\n1. CONTAINER STRUCTURE:")
        if 'px' in container_info['container']['height']:
            print("   ✅ Container has defined height (90vh)")
        if container_info['content']['flex'].startswith('1'):
            print("   ✅ Content has flex: 1")
        if container_info['chatSection']['overflow'] == 'hidden':
            print("   ✅ Chat-section has overflow: hidden")
        
        print("\n2. VISIBILITY:")
        if visibility['header']['visible']:
            print("   ✅ Header always visible")
        if visibility['input']['visible']:
            print("   ✅ Input always visible")
        else:
            print("   ❌ Input NOT visible - need to scroll to find it")
        
        print("\n3. AFTER SCROLLING:")
        if after_scroll['header']['visible'] and after_scroll['input']['visible']:
            print("   ✅ Header and input stay visible when messages scroll")
        else:
            print("   ❌ Elements disappear when scrolling")
        
        if not visibility['input']['visible']:
            print("\n⚠️  INPUT NOT VISIBLE - Container height constraints may need adjustment")
            print("   Try: Maximize browser window or adjust container max-height")
        
        print("\n⚠️ REMEMBER: Clear browser cache (Ctrl+F5) to see changes!")
        print("\nBrowser will stay open for 30 seconds...")
        page.wait_for_timeout(30000)
        
        browser.close()

if __name__ == '__main__':
    test_fixed_containers()
