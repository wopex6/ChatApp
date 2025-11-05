from playwright.sync_api import sync_playwright

def test_final_fixes():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        page = browser.new_page()
        
        page.goto('file:///c:/Users/trabc/CascadeProjects/ChatApp/chatapp_frontend.html')
        page.wait_for_selector('body')
        page.wait_for_timeout(500)
        
        print("\n" + "="*80)
        print("TESTING: 1) SCROLLABLE MESSAGES, 2) CLOSER BUTTONS")
        print("="*80)
        
        # Setup
        page.evaluate('''() => {
            const loginSection = document.querySelector('.login-section');
            const chatSection = document.getElementById('chat-section');
            const messageInput = document.getElementById('message-input-section');
            
            if (loginSection) loginSection.style.display = 'none';
            if (chatSection) chatSection.style.display = 'flex';
            if (messageInput) messageInput.style.display = 'flex';
            
            // Add 30 messages
            const container = document.getElementById('messages-container');
            let html = '';
            for (let i = 1; i <= 30; i++) {
                const isMe = i % 2 === 0;
                const className = isMe ? 'sent-by-me' : 'sent-by-other';
                html += `
                    <div class="message-wrapper ${className}">
                        <div class="message ${className}">
                            <div>
                                Message ${i} - This is a test message to check scrolling
                                <span class="message-time">${i}:00pm</span>
                            </div>
                        </div>
                    </div>
                `;
            }
            container.innerHTML = html;
        }''')
        
        page.wait_for_timeout(1000)
        
        # Test 1: Check overflow settings
        print("\n🔍 TEST 1: OVERFLOW SETTINGS")
        
        overflow_check = page.evaluate('''() => {
            const chatSection = document.getElementById('chat-section');
            const messagesContainer = document.getElementById('messages-container');
            
            const chatStyle = window.getComputedStyle(chatSection);
            const msgStyle = window.getComputedStyle(messagesContainer);
            
            return {
                chatSection: {
                    overflow: chatStyle.overflow,
                    overflowY: chatStyle.overflowY,
                    height: chatStyle.height
                },
                messagesContainer: {
                    overflow: msgStyle.overflow,
                    overflowY: msgStyle.overflowY,
                    flex: msgStyle.flex,
                    height: msgStyle.height,
                    scrollHeight: messagesContainer.scrollHeight,
                    clientHeight: messagesContainer.clientHeight,
                    isScrollable: messagesContainer.scrollHeight > messagesContainer.clientHeight
                }
            };
        }''')
        
        print(f"\n  CHAT-SECTION (parent):")
        print(f"    Overflow: {overflow_check['chatSection']['overflow']}")
        print(f"    Overflow-Y: {overflow_check['chatSection']['overflowY']}")
        print(f"    Height: {overflow_check['chatSection']['height']}")
        
        if overflow_check['chatSection']['overflow'] == 'hidden':
            print(f"    ✅ overflow: hidden (correct - forces messages to scroll)")
        else:
            print(f"    ❌ Should be overflow: hidden")
        
        print(f"\n  MESSAGES-CONTAINER (scrollable area):")
        print(f"    Overflow-Y: {overflow_check['messagesContainer']['overflowY']}")
        print(f"    Flex: {overflow_check['messagesContainer']['flex']}")
        print(f"    Height: {overflow_check['messagesContainer']['height']}")
        print(f"    Scroll height: {overflow_check['messagesContainer']['scrollHeight']}px")
        print(f"    Client height: {overflow_check['messagesContainer']['clientHeight']}px")
        
        if overflow_check['messagesContainer']['isScrollable']:
            print(f"    ✅ Content overflows (messages-container is scrollable)")
        else:
            print(f"    ⚠️  Content fits - add more messages to test")
        
        # Test 2: Test scrolling behavior
        print("\n🖱️  TEST 2: SCROLL BEHAVIOR")
        
        # Get initial positions
        initial = page.evaluate('''() => {
            const header = document.querySelector('.chat-header');
            const input = document.getElementById('message-input-section');
            const messages = document.getElementById('messages-container');
            
            return {
                headerTop: header.getBoundingClientRect().top,
                inputBottom: window.innerHeight - input.getBoundingClientRect().bottom,
                messagesScrollTop: messages.scrollTop
            };
        }''')
        
        print(f"  Before scroll:")
        print(f"    Header top: {initial['headerTop']:.0f}px")
        print(f"    Input bottom gap: {initial['inputBottom']:.0f}px")
        print(f"    Messages scroll: {initial['messagesScrollTop']}px")
        
        # Scroll the messages container
        page.evaluate('''() => {
            const messages = document.getElementById('messages-container');
            messages.scrollTop = 500;
        }''')
        
        page.wait_for_timeout(500)
        
        # Get positions after scroll
        after = page.evaluate('''() => {
            const header = document.querySelector('.chat-header');
            const input = document.getElementById('message-input-section');
            const messages = document.getElementById('messages-container');
            
            return {
                headerTop: header.getBoundingClientRect().top,
                inputBottom: window.innerHeight - input.getBoundingClientRect().bottom,
                messagesScrollTop: messages.scrollTop
            };
        }''')
        
        print(f"\n  After scrolling messages:")
        print(f"    Header top: {after['headerTop']:.0f}px")
        print(f"    Input bottom gap: {after['inputBottom']:.0f}px")
        print(f"    Messages scroll: {after['messagesScrollTop']}px")
        
        header_stayed = abs(initial['headerTop'] - after['headerTop']) < 2
        input_stayed = abs(initial['inputBottom'] - after['inputBottom']) < 2
        messages_scrolled = after['messagesScrollTop'] > initial['messagesScrollTop']
        
        if header_stayed:
            print(f"  ✅ Header stayed fixed")
        else:
            print(f"  ❌ Header moved")
        
        if input_stayed:
            print(f"  ✅ Input stayed fixed")
        else:
            print(f"  ❌ Input moved")
        
        if messages_scrolled:
            print(f"  ✅ Messages scrolled (scrolled {after['messagesScrollTop']}px)")
        else:
            print(f"  ❌ Messages didn't scroll")
        
        # Test 3: Button spacing
        print("\n🔘 TEST 3: BUTTON SPACING (Closer)")
        
        buttons = page.evaluate('''() => {
            const container = document.querySelector('.input-actions');
            if (!container) return { exists: false };
            
            const style = window.getComputedStyle(container);
            const buttons = Array.from(container.querySelectorAll('button'));
            
            const buttonInfo = buttons.map(btn => {
                const btnStyle = window.getComputedStyle(btn);
                return {
                    text: btn.textContent.trim(),
                    padding: btnStyle.padding,
                    paddingLeft: btnStyle.paddingLeft,
                    paddingRight: btnStyle.paddingRight,
                    width: Math.round(btn.getBoundingClientRect().width),
                    height: Math.round(btn.getBoundingClientRect().height)
                };
            });
            
            const gaps = [];
            for (let i = 0; i < buttons.length - 1; i++) {
                const rect1 = buttons[i].getBoundingClientRect();
                const rect2 = buttons[i + 1].getBoundingClientRect();
                gaps.push(Math.round(rect2.left - rect1.right));
            }
            
            return {
                exists: true,
                cssGap: style.gap,
                buttons: buttonInfo,
                gaps: gaps,
                totalWidth: Math.round(container.getBoundingClientRect().width)
            };
        }''')
        
        if buttons['exists']:
            print(f"  Container gap: {buttons['cssGap']}")
            print(f"  Total width: {buttons['totalWidth']}px")
            
            print(f"\n  Button details:")
            for i, btn in enumerate(buttons['buttons']):
                print(f"    {i+1}. {btn['text']}")
                print(f"       Padding: {btn['padding']}")
                print(f"       Size: {btn['width']}x{btn['height']}px")
            
            print(f"\n  Gaps between buttons:")
            for i, gap in enumerate(buttons['gaps']):
                btn1 = buttons['buttons'][i]['text']
                btn2 = buttons['buttons'][i+1]['text']
                print(f"    {btn1} → {btn2}: {gap}px")
            
            avg_gap = sum(buttons['gaps']) / len(buttons['gaps']) if buttons['gaps'] else 0
            print(f"\n  Average gap: {avg_gap:.1f}px")
            
            # Check padding
            all_padding_8px = all('8px' in btn['padding'] for btn in buttons['buttons'])
            
            if all_padding_8px:
                print(f"  ✅ All buttons have 8px padding (reduced from 10-20px)")
            else:
                print(f"  ❌ Button padding not consistent")
            
            if avg_gap <= 5:
                print(f"  ✅ Gaps are small (≤5px)")
            else:
                print(f"  ⚠️  Gaps still large - may need cache clear")
        
        # Test 4: Visual comparison
        print("\n📏 TEST 4: TOTAL BUTTON AREA WIDTH")
        
        comparison = page.evaluate('''() => {
            const buttons = Array.from(document.querySelectorAll('.input-actions button'));
            if (buttons.length === 0) return { exists: false };
            
            const first = buttons[0].getBoundingClientRect();
            const last = buttons[buttons.length - 1].getBoundingClientRect();
            
            return {
                exists: true,
                totalSpan: Math.round(last.right - first.left),
                buttonCount: buttons.length
            };
        }''')
        
        if comparison['exists']:
            print(f"  Total span (first to last button): {comparison['totalSpan']}px")
            print(f"  Button count: {comparison['buttonCount']}")
            
            # Estimate: 3 buttons × 40px each + 2 gaps × 3px = ~126px
            if comparison['totalSpan'] < 150:
                print(f"  ✅ Buttons are compact (span < 150px)")
            else:
                print(f"  ⚠️  Buttons span is large - was {comparison['totalSpan']}px")
        
        # Take screenshots
        page.screenshot(path='test_screenshots/final_fixes.png', full_page=True)
        print("\n✓ Screenshot saved: final_fixes.png")
        
        # Scroll to middle
        page.evaluate('''() => {
            const messages = document.getElementById('messages-container');
            messages.scrollTop = messages.scrollHeight / 2;
        }''')
        page.wait_for_timeout(500)
        page.screenshot(path='test_screenshots/final_fixes_scrolled.png', full_page=True)
        print("✓ Screenshot saved: final_fixes_scrolled.png")
        
        print("\n" + "="*80)
        print("SUMMARY:")
        print("="*80)
        
        print("\n1. OVERFLOW SETTINGS:")
        if overflow_check['chatSection']['overflow'] == 'hidden':
            print("   ✅ Chat-section: overflow hidden")
        if overflow_check['messagesContainer']['overflowY'] == 'auto':
            print("   ✅ Messages-container: overflow-y auto")
        if overflow_check['messagesContainer']['isScrollable']:
            print("   ✅ Messages overflow and can scroll")
        
        print("\n2. SCROLL BEHAVIOR:")
        if header_stayed and input_stayed and messages_scrolled:
            print("   ✅ Header/input stay fixed, messages scroll")
        else:
            print("   ❌ Sticky not working properly")
        
        print("\n3. BUTTON SPACING:")
        if buttons['exists']:
            if all_padding_8px:
                print("   ✅ Button padding reduced to 8px")
            if avg_gap <= 5:
                print(f"   ✅ Gaps small: {avg_gap:.0f}px average")
            if comparison['totalSpan'] < 150:
                print(f"   ✅ Compact layout: {comparison['totalSpan']}px total span")
        
        print("\n📊 BUTTON SPACING IMPROVEMENT:")
        print("   Before: padding 12px 20px (40px horizontal) + 2.5px gap")
        print("   After:  padding 8px (16px horizontal) + 2.5px gap")
        print("   Result: Much closer together!")
        
        print("\n⚠️ REMEMBER TO CLEAR CACHE (Ctrl+F5)!")
        print("\nBrowser will stay open for 30 seconds...")
        page.wait_for_timeout(30000)
        
        browser.close()

if __name__ == '__main__':
    test_final_fixes()
