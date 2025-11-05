from playwright.sync_api import sync_playwright

def test_sticky_and_buttons():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        page = browser.new_page()
        
        page.goto('file:///c:/Users/trabc/CascadeProjects/ChatApp/chatapp_frontend.html')
        page.wait_for_selector('body')
        page.wait_for_timeout(500)
        
        print("\n" + "="*80)
        print("TESTING: 1) STICKY HEADER/INPUT, 2) BUTTON SPACING")
        print("="*80)
        
        # Setup
        page.evaluate('''() => {
            const loginSection = document.querySelector('.login-section');
            const chatSection = document.getElementById('chat-section');
            const messageInput = document.getElementById('message-input-section');
            
            if (loginSection) loginSection.style.display = 'none';
            if (chatSection) chatSection.style.display = 'flex';
            if (messageInput) messageInput.style.display = 'flex';
            
            // Add many messages to enable scrolling
            const container = document.getElementById('messages-container');
            let html = '';
            for (let i = 1; i <= 30; i++) {
                const isMe = i % 2 === 0;
                const className = isMe ? 'sent-by-me' : 'sent-by-other';
                html += `
                    <div class="message-wrapper ${className}">
                        <div class="message ${className}">
                            <div>
                                Message ${i} - Testing scrolling functionality
                                <span class="message-time">${i}:00pm</span>
                            </div>
                        </div>
                    </div>
                `;
            }
            container.innerHTML = html;
        }''')
        
        page.wait_for_timeout(1000)
        
        # Test 1: Check chat-section overflow
        print("\n🔍 TEST 1: CHAT-SECTION OVERFLOW (for sticky to work)")
        chat_overflow = page.evaluate('''() => {
            const chatSection = document.getElementById('chat-section');
            if (!chatSection) return { exists: false };
            
            const style = window.getComputedStyle(chatSection);
            return {
                exists: true,
                overflow: style.overflow,
                overflowY: style.overflowY,
                display: style.display,
                flexDirection: style.flexDirection
            };
        }''')
        
        if chat_overflow['exists']:
            print(f"  Overflow: {chat_overflow['overflow']}")
            print(f"  Overflow-Y: {chat_overflow['overflowY']}")
            print(f"  Display: {chat_overflow['display']}")
            print(f"  Flex-direction: {chat_overflow['flexDirection']}")
            
            if chat_overflow['overflowY'] == 'auto':
                print(f"  ✅ Has overflow-y: auto (sticky will work)")
            elif chat_overflow['overflow'] == 'hidden':
                print(f"  ❌ Has overflow: hidden (sticky won't work!)")
            else:
                print(f"  ⚠️  Overflow setting: {chat_overflow['overflowY']}")
        
        # Test 2: Check sticky positioning
        print("\n📌 TEST 2: STICKY POSITIONING")
        
        sticky_check = page.evaluate('''() => {
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
        
        print(f"\n  HEADER:")
        print(f"    Position: {sticky_check['header']['position']}")
        print(f"    Top: {sticky_check['header']['top']}")
        print(f"    Z-index: {sticky_check['header']['zIndex']}")
        
        if sticky_check['header']['position'] == 'sticky':
            print(f"    ✅ Header is sticky")
        else:
            print(f"    ❌ Header position should be sticky")
        
        print(f"\n  INPUT:")
        print(f"    Position: {sticky_check['input']['position']}")
        print(f"    Bottom: {sticky_check['input']['bottom']}")
        print(f"    Z-index: {sticky_check['input']['zIndex']}")
        
        if sticky_check['input']['position'] == 'sticky':
            print(f"    ✅ Input is sticky")
        else:
            print(f"    ❌ Input position should be sticky")
        
        # Test 3: Test actual sticky behavior by scrolling
        print("\n🖱️  TEST 3: SCROLL TEST (Sticky Behavior)")
        
        # Get initial positions
        initial_pos = page.evaluate('''() => {
            const header = document.querySelector('.chat-header');
            const input = document.getElementById('message-input-section');
            const chatSection = document.getElementById('chat-section');
            
            return {
                headerTop: header.getBoundingClientRect().top,
                inputBottom: window.innerHeight - input.getBoundingClientRect().bottom,
                chatSectionScrollTop: chatSection.scrollTop
            };
        }''')
        
        print(f"  Before scroll:")
        print(f"    Header top: {initial_pos['headerTop']:.0f}px")
        print(f"    Input bottom gap: {initial_pos['inputBottom']:.0f}px")
        print(f"    Chat scroll position: {initial_pos['chatSectionScrollTop']}px")
        
        # Scroll the chat-section
        page.evaluate('''() => {
            const chatSection = document.getElementById('chat-section');
            chatSection.scrollTop = 500;
        }''')
        
        page.wait_for_timeout(500)
        
        # Get positions after scroll
        after_scroll = page.evaluate('''() => {
            const header = document.querySelector('.chat-header');
            const input = document.getElementById('message-input-section');
            const chatSection = document.getElementById('chat-section');
            
            return {
                headerTop: header.getBoundingClientRect().top,
                inputBottom: window.innerHeight - input.getBoundingClientRect().bottom,
                chatSectionScrollTop: chatSection.scrollTop
            };
        }''')
        
        print(f"\n  After scroll:")
        print(f"    Header top: {after_scroll['headerTop']:.0f}px")
        print(f"    Input bottom gap: {after_scroll['inputBottom']:.0f}px")
        print(f"    Chat scroll position: {after_scroll['chatSectionScrollTop']}px")
        
        # Check if positions stayed the same
        header_stayed = abs(initial_pos['headerTop'] - after_scroll['headerTop']) < 5
        input_stayed = abs(initial_pos['inputBottom'] - after_scroll['inputBottom']) < 5
        
        if header_stayed:
            print(f"  ✅ Header stayed at top (sticky working!)")
        else:
            print(f"  ❌ Header moved (sticky not working)")
        
        if input_stayed:
            print(f"  ✅ Input stayed at bottom (sticky working!)")
        else:
            print(f"  ❌ Input moved (sticky not working)")
        
        # Test 4: Check button spacing
        print("\n🔘 TEST 4: BUTTON SPACING")
        
        button_spacing = page.evaluate('''() => {
            const container = document.querySelector('.input-actions');
            if (!container) return { exists: false };
            
            const style = window.getComputedStyle(container);
            const buttons = container.querySelectorAll('button');
            
            const buttonInfo = Array.from(buttons).map(btn => ({
                text: btn.textContent.trim(),
                class: btn.className
            }));
            
            const gaps = [];
            for (let i = 0; i < buttons.length - 1; i++) {
                const rect1 = buttons[i].getBoundingClientRect();
                const rect2 = buttons[i + 1].getBoundingClientRect();
                gaps.push({
                    between: `${buttonInfo[i].text} and ${buttonInfo[i+1].text}`,
                    gap: Math.round(rect2.left - rect1.right)
                });
            }
            
            return {
                exists: true,
                cssGap: style.gap,
                columnGap: style.columnGap,
                buttonCount: buttons.length,
                buttons: buttonInfo,
                gaps: gaps
            };
        }''')
        
        if button_spacing['exists']:
            print(f"  CSS gap property: {button_spacing['cssGap']}")
            print(f"  CSS column-gap: {button_spacing['columnGap']}")
            print(f"  Button count: {button_spacing['buttonCount']}")
            
            print(f"\n  Buttons found:")
            for i, btn in enumerate(button_spacing['buttons']):
                print(f"    {i+1}. {btn['text']} (class: {btn['class']})")
            
            print(f"\n  Actual gaps between buttons:")
            for gap_info in button_spacing['gaps']:
                print(f"    {gap_info['between']}: {gap_info['gap']}px")
            
            # Check if all three buttons are present
            has_attachment = any('📎' in b['text'] for b in button_spacing['buttons'])
            has_emoji = any('😊' in b['text'] or '🙂' in b['text'] for b in button_spacing['buttons'])
            has_send = any('➤' in b['text'] for b in button_spacing['buttons'])
            
            print(f"\n  Button presence:")
            print(f"    📎 Attachment: {has_attachment} {'✅' if has_attachment else '❌'}")
            print(f"    😊 Emoji: {has_emoji} {'✅' if has_emoji else '❌'}")
            print(f"    ➤ Send: {has_send} {'✅' if has_send else '❌'}")
            
            # Check gap size
            avg_gap = sum(g['gap'] for g in button_spacing['gaps']) / len(button_spacing['gaps']) if button_spacing['gaps'] else 0
            print(f"\n  Average gap: {avg_gap:.1f}px")
            
            if button_spacing['cssGap'] == '2.5px':
                print(f"  ✅ CSS gap is 2.5px")
                if avg_gap <= 5:
                    print(f"  ✅ Actual gap is small (≤5px)")
                else:
                    print(f"  ❌ Actual gap is large ({avg_gap:.0f}px)")
                    print(f"  💡 This suggests browser cache issue - need Ctrl+F5")
            else:
                print(f"  ❌ CSS gap should be 2.5px, found: {button_spacing['cssGap']}")
        
        # Take screenshots
        page.screenshot(path='test_screenshots/sticky_and_buttons.png', full_page=True)
        print("\n✓ Screenshot saved: sticky_and_buttons.png")
        
        # Scroll back to top and screenshot
        page.evaluate('''() => {
            const chatSection = document.getElementById('chat-section');
            chatSection.scrollTop = 0;
        }''')
        page.wait_for_timeout(500)
        page.screenshot(path='test_screenshots/sticky_top.png', full_page=True)
        print("✓ Screenshot saved: sticky_top.png")
        
        print("\n" + "="*80)
        print("SUMMARY:")
        print("="*80)
        
        print("\n1. CHAT-SECTION OVERFLOW:")
        if chat_overflow['overflowY'] == 'auto':
            print("   ✅ overflow-y: auto (enables sticky)")
        else:
            print("   ❌ overflow: hidden (breaks sticky)")
        
        print("\n2. STICKY POSITIONING:")
        if sticky_check['header']['position'] == 'sticky' and sticky_check['input']['position'] == 'sticky':
            print("   ✅ Both header and input have position: sticky")
        else:
            print("   ❌ Sticky positioning not set correctly")
        
        print("\n3. STICKY BEHAVIOR:")
        if header_stayed and input_stayed:
            print("   ✅ Header and input stayed fixed when scrolling")
        else:
            print("   ❌ Elements moved when scrolling (sticky not working)")
        
        print("\n4. BUTTON SPACING:")
        if button_spacing['exists']:
            if has_attachment and has_emoji and has_send:
                print("   ✅ All 3 buttons present: 📎 😊 ➤")
            else:
                print("   ❌ Missing buttons")
            
            if button_spacing['cssGap'] == '2.5px':
                print(f"   ✅ CSS gap: 2.5px")
            else:
                print(f"   ❌ CSS gap should be 2.5px")
            
            if avg_gap <= 5:
                print(f"   ✅ Buttons close together ({avg_gap:.0f}px gap)")
            else:
                print(f"   ❌ Buttons far apart ({avg_gap:.0f}px gap)")
                print(f"   💡 CLEAR BROWSER CACHE (Ctrl+F5)")
        
        print("\n⚠️ CRITICAL: CLEAR BROWSER CACHE (Ctrl+F5)!")
        print("\nBrowser will stay open for 30 seconds...")
        page.wait_for_timeout(30000)
        
        browser.close()

if __name__ == '__main__':
    test_sticky_and_buttons()
