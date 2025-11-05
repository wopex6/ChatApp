from playwright.sync_api import sync_playwright

def test_fixed_layout():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        page = browser.new_page()
        
        page.goto('file:///c:/Users/trabc/CascadeProjects/ChatApp/chatapp_frontend.html')
        page.wait_for_selector('body')
        page.wait_for_timeout(500)
        
        print("\n" + "="*80)
        print("TESTING: FIXED HEADER/INPUT, SCROLLABLE MESSAGES, HIDDEN SUBTITLE")
        print("="*80)
        
        # Setup the page
        page.evaluate('''() => {
            const loginSection = document.querySelector('.login-section');
            const chatSection = document.getElementById('chat-section');
            const messageInput = document.getElementById('message-input-section');
            
            if (loginSection) loginSection.style.display = 'none';
            if (chatSection) chatSection.style.display = 'flex';
            if (messageInput) messageInput.style.display = 'flex';
            
            // Add many messages to test scrolling
            const container = document.getElementById('messages-container');
            let html = '';
            for (let i = 1; i <= 20; i++) {
                const isMe = i % 2 === 0;
                const className = isMe ? 'sent-by-me' : 'sent-by-other';
                html += `
                    <div class="message-wrapper ${className}">
                        <div class="message ${className}">
                            <div>
                                Message ${i} - Testing scrolling
                                <span class="message-time">${i}:00pm</span>
                            </div>
                        </div>
                    </div>
                `;
            }
            container.innerHTML = html;
        }''')
        
        page.wait_for_timeout(1000)
        
        # Test 1: Check header subtitle is hidden
        print("\n📋 TEST 1: HEADER SUBTITLE (Chat with Ken)")
        subtitle_check = page.evaluate('''() => {
            const subtitle = document.getElementById('header-subtitle');
            if (!subtitle) return { exists: false };
            
            const style = window.getComputedStyle(subtitle);
            return {
                exists: true,
                display: style.display,
                visibility: style.visibility,
                text: subtitle.textContent
            };
        }''')
        
        if subtitle_check['exists']:
            print(f"  Element exists: Yes")
            print(f"  Text: '{subtitle_check['text']}'")
            print(f"  Display: {subtitle_check['display']}")
            print(f"  Visibility: {subtitle_check['visibility']}")
            
            if subtitle_check['display'] == 'none':
                print(f"  ✅ Subtitle hidden (display: none)")
            else:
                print(f"  ❌ Subtitle still visible")
        else:
            print(f"  Element not found")
        
        # Test 2: Check header position
        print("\n📌 TEST 2: HEADER FIXED POSITION")
        header_check = page.evaluate('''() => {
            const header = document.querySelector('.chat-header');
            if (!header) return { exists: false };
            
            const style = window.getComputedStyle(header);
            return {
                exists: true,
                position: style.position,
                top: style.top,
                zIndex: style.zIndex,
                flexShrink: style.flexShrink,
                background: style.backgroundColor
            };
        }''')
        
        if header_check['exists']:
            print(f"  Position: {header_check['position']}")
            print(f"  Top: {header_check['top']}")
            print(f"  Z-index: {header_check['zIndex']}")
            print(f"  Flex-shrink: {header_check['flexShrink']}")
            print(f"  Background: {header_check['background']}")
            
            if header_check['position'] == 'sticky':
                print(f"  ✅ Header is sticky (fixed to top)")
            else:
                print(f"  ❌ Header not sticky")
        
        # Test 3: Check messages container scrollability
        print("\n📜 TEST 3: MESSAGES CONTAINER (Scrollable)")
        messages_check = page.evaluate('''() => {
            const container = document.getElementById('messages-container');
            if (!container) return { exists: false };
            
            const style = window.getComputedStyle(container);
            return {
                exists: true,
                overflowY: style.overflowY,
                flex: style.flex,
                height: style.height,
                scrollHeight: container.scrollHeight,
                clientHeight: container.clientHeight,
                isScrollable: container.scrollHeight > container.clientHeight
            };
        }''')
        
        if messages_check['exists']:
            print(f"  Overflow-Y: {messages_check['overflowY']}")
            print(f"  Flex: {messages_check['flex']}")
            print(f"  Height: {messages_check['height']}")
            print(f"  Scroll height: {messages_check['scrollHeight']}px")
            print(f"  Client height: {messages_check['clientHeight']}px")
            print(f"  Is scrollable: {messages_check['isScrollable']}")
            
            if messages_check['overflowY'] == 'auto' and messages_check['isScrollable']:
                print(f"  ✅ Messages container is scrollable")
            elif messages_check['overflowY'] == 'auto':
                print(f"  ⚠️  Has overflow-y: auto but content fits")
            else:
                print(f"  ❌ Messages container not scrollable")
        
        # Test 4: Check input section position
        print("\n⌨️  TEST 4: INPUT SECTION FIXED POSITION")
        input_check = page.evaluate('''() => {
            const inputSection = document.getElementById('message-input-section');
            if (!inputSection) return { exists: false };
            
            const style = window.getComputedStyle(inputSection);
            return {
                exists: true,
                position: style.position,
                bottom: style.bottom,
                zIndex: style.zIndex,
                flexShrink: style.flexShrink,
                background: style.backgroundColor
            };
        }''')
        
        if input_check['exists']:
            print(f"  Position: {input_check['position']}")
            print(f"  Bottom: {input_check['bottom']}")
            print(f"  Z-index: {input_check['zIndex']}")
            print(f"  Flex-shrink: {input_check['flexShrink']}")
            print(f"  Background: {input_check['background']}")
            
            if input_check['position'] == 'sticky':
                print(f"  ✅ Input section is sticky (fixed to bottom)")
            else:
                print(f"  ❌ Input section not sticky")
        
        # Test 5: Scroll test
        print("\n🖱️  TEST 5: SCROLL BEHAVIOR")
        
        # Get initial scroll position
        initial_scroll = page.evaluate('''() => {
            const container = document.getElementById('messages-container');
            return container.scrollTop;
        }''')
        print(f"  Initial scroll position: {initial_scroll}px")
        
        # Scroll down
        page.evaluate('''() => {
            const container = document.getElementById('messages-container');
            container.scrollTop = 500;
        }''')
        page.wait_for_timeout(500)
        
        # Check scroll position
        after_scroll = page.evaluate('''() => {
            const container = document.getElementById('messages-container');
            return container.scrollTop;
        }''')
        print(f"  After scrolling: {after_scroll}px")
        
        if after_scroll > initial_scroll:
            print(f"  ✅ Messages container scrolls correctly")
        else:
            print(f"  ❌ Messages container doesn't scroll")
        
        # Check if header/input moved
        positions_after_scroll = page.evaluate('''() => {
            const header = document.querySelector('.chat-header');
            const input = document.getElementById('message-input-section');
            
            return {
                headerTop: header.getBoundingClientRect().top,
                inputBottom: window.innerHeight - input.getBoundingClientRect().bottom
            };
        }''')
        
        print(f"  Header top position: {positions_after_scroll['headerTop']}px")
        print(f"  Input bottom gap: {positions_after_scroll['inputBottom']}px")
        
        if positions_after_scroll['headerTop'] >= 0:
            print(f"  ✅ Header stayed at top")
        
        if positions_after_scroll['inputBottom'] <= 10:
            print(f"  ✅ Input stayed at bottom")
        
        # Take screenshots
        page.screenshot(path='test_screenshots/fixed_layout.png', full_page=True)
        print("\n✓ Screenshot saved: fixed_layout.png")
        
        # Scroll to middle and take another screenshot
        page.evaluate('''() => {
            const container = document.getElementById('messages-container');
            container.scrollTop = container.scrollHeight / 2;
        }''')
        page.wait_for_timeout(500)
        page.screenshot(path='test_screenshots/fixed_layout_scrolled.png', full_page=True)
        print("✓ Screenshot saved: fixed_layout_scrolled.png")
        
        print("\n" + "="*80)
        print("SUMMARY:")
        print("="*80)
        
        print("\n1. HEADER SUBTITLE (Chat with Ken):")
        if subtitle_check['exists'] and subtitle_check['display'] == 'none':
            print("   ✅ Hidden to save space")
        else:
            print("   ❌ Still visible")
        
        print("\n2. HEADER SECTION:")
        if header_check['exists'] and header_check['position'] == 'sticky':
            print("   ✅ Fixed at top (sticky)")
        else:
            print("   ❌ Not fixed")
        
        print("\n3. MESSAGES CONTAINER:")
        if messages_check['exists'] and messages_check['isScrollable']:
            print("   ✅ Scrollable (fills middle space)")
        else:
            print("   ⚠️  Not scrollable or no content")
        
        print("\n4. INPUT SECTION:")
        if input_check['exists'] and input_check['position'] == 'sticky':
            print("   ✅ Fixed at bottom (sticky)")
        else:
            print("   ❌ Not fixed")
        
        print("\n📊 LAYOUT STRUCTURE:")
        print("   ┌─────────────────────┐")
        print("   │ HEADER (Fixed)      │ ← Sticky top")
        print("   ├─────────────────────┤")
        print("   │                     │")
        print("   │   MESSAGES          │ ← Scrollable")
        print("   │   (Scrollable)      │")
        print("   │                     │")
        print("   ├─────────────────────┤")
        print("   │ INPUT (Fixed)       │ ← Sticky bottom")
        print("   └─────────────────────┘")
        
        print("\n⚠️ REMEMBER TO CLEAR CACHE (Ctrl+F5)!")
        print("\nBrowser will stay open for 30 seconds...")
        page.wait_for_timeout(30000)
        
        browser.close()

if __name__ == '__main__':
    test_fixed_layout()
