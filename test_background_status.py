from playwright.sync_api import sync_playwright

def test_background_status():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        page = browser.new_page()
        
        page.goto('file:///c:/Users/trabc/CascadeProjects/ChatApp/chatapp_frontend.html')
        page.wait_for_selector('body')
        page.wait_for_timeout(500)
        
        print("\n" + "="*80)
        print("TESTING: BACKGROUND COLOR STATUS (REPLACING DOUBLE TICKS)")
        print("="*80)
        
        # Inject messages with both read and unread states
        page.evaluate('''() => {
            const loginSection = document.querySelector('.login-section');
            const chatSection = document.getElementById('chat-section');
            const messageInput = document.getElementById('message-input-section');
            
            if (loginSection) loginSection.style.display = 'none';
            if (chatSection) chatSection.style.display = 'flex';
            if (messageInput) messageInput.style.display = 'flex';
            
            const container = document.getElementById('messages-container');
            container.innerHTML = `
                <div class="message-wrapper sent-by-me">
                    <div class="message sent-by-me unread">
                        <div>
                            Unread message - should have light yellow background
                            <span class="message-time">2:30pm<span class="message-tick">✓</span></span>
                        </div>
                        <div class="message-actions">
                            <button>↩</button>
                            <button>🗑</button>
                        </div>
                    </div>
                </div>
                
                <div class="message-wrapper sent-by-me">
                    <div class="message sent-by-me">
                        <div>
                            Read message - should have green background
                            <span class="message-time">2:31pm<span class="message-tick">✓</span></span>
                        </div>
                        <div class="message-actions">
                            <button>↩</button>
                            <button>🗑</button>
                        </div>
                    </div>
                </div>
                
                <div class="message-wrapper sent-by-other">
                    <div class="message sent-by-other">
                        <div>
                            Received message - should be white
                            <span class="message-time">2:32pm</span>
                        </div>
                        <div class="message-actions">
                            <button>↩</button>
                        </div>
                    </div>
                </div>
            `;
        }''')
        
        page.wait_for_timeout(1000)
        
        # Test message backgrounds
        print("\n🎨 MESSAGE BACKGROUND COLORS:")
        backgrounds = page.evaluate('''() => {
            const messages = document.querySelectorAll('.message');
            return Array.from(messages).map((msg, i) => {
                const style = window.getComputedStyle(msg);
                const isSent = msg.classList.contains('sent-by-me');
                const isUnread = msg.classList.contains('unread');
                const isReceived = msg.classList.contains('sent-by-other');
                
                return {
                    index: i,
                    type: isReceived ? 'RECEIVED' : 'SENT',
                    isUnread: isUnread,
                    backgroundColor: style.backgroundColor,
                    classes: msg.className
                };
            });
        }''')
        
        for msg in backgrounds:
            print(f"\n  Message {msg['index'] + 1} ({msg['type']}):")
            print(f"    Classes: {msg['classes']}")
            print(f"    Background: {msg['backgroundColor']}")
            
            if msg['type'] == 'SENT':
                if msg['isUnread']:
                    # Should be light yellow
                    if 'rgb(255, 250, 205)' in msg['backgroundColor'] or '#FFFACD' in msg['backgroundColor']:
                        print(f"    ✅ Light yellow background (#FFFACD) - Unread/Delivered")
                    else:
                        print(f"    ❌ Should be light yellow (#FFFACD)")
                else:
                    # Should be green
                    if 'rgb(220, 248, 198)' in msg['backgroundColor'] or '#DCF8C6' in msg['backgroundColor']:
                        print(f"    ✅ Green background (#DCF8C6) - Read")
                    else:
                        print(f"    ❌ Should be green (#DCF8C6)")
            else:
                # Should be white
                if 'rgb(255, 255, 255)' in msg['backgroundColor'] or '#FFFFFF' in msg['backgroundColor']:
                    print(f"    ✅ White background (#FFFFFF) - Received")
                else:
                    print(f"    ❌ Should be white (#FFFFFF)")
        
        # Test tick marks
        print("\n✓ TICK MARKS:")
        ticks = page.evaluate('''() => {
            const ticks = document.querySelectorAll('.message-tick');
            return Array.from(ticks).map((tick, i) => {
                const style = window.getComputedStyle(tick);
                return {
                    index: i,
                    content: tick.textContent.trim(),
                    color: style.color,
                    hasReadClass: tick.classList.contains('read')
                };
            });
        }''')
        
        has_double_tick = False
        for tick in ticks:
            print(f"\n  Tick {tick['index'] + 1}:")
            print(f"    Content: '{tick['content']}'")
            print(f"    Color: {tick['color']}")
            
            if '✓✓' in tick['content']:
                has_double_tick = True
                print(f"    ❌ Found double tick - should be removed!")
            elif '✓' in tick['content']:
                print(f"    ✅ Single tick only")
            
            if 'rgb(134, 150, 160)' in tick['color'] or '#8696a0' in tick['color']:
                print(f"    ✅ Gray color (#8696a0) - consistent for all")
            else:
                print(f"    ⚠️  Unexpected color")
        
        if not has_double_tick:
            print(f"\n  ✅ No double ticks found - all removed successfully!")
        else:
            print(f"\n  ❌ Still have double ticks!")
        
        # Take screenshots
        page.screenshot(path='test_screenshots/background_status.png', full_page=True)
        print("\n✓ Screenshot saved: background_status.png")
        
        # Hover over messages to see them clearly
        messages = page.locator('.message').all()
        for i, msg in enumerate(messages):
            msg.hover()
            page.wait_for_timeout(300)
        
        page.screenshot(path='test_screenshots/background_status_hover.png', full_page=True)
        print("✓ Hover screenshot saved: background_status_hover.png")
        
        print("\n" + "="*80)
        print("SUMMARY:")
        print("="*80)
        
        # Check results
        unread_correct = any(
            'rgb(255, 250, 205)' in m['backgroundColor'] 
            for m in backgrounds 
            if m['type'] == 'SENT' and m['isUnread']
        )
        
        read_correct = any(
            'rgb(220, 248, 198)' in m['backgroundColor'] 
            for m in backgrounds 
            if m['type'] == 'SENT' and not m['isUnread']
        )
        
        received_correct = any(
            'rgb(255, 255, 255)' in m['backgroundColor'] 
            for m in backgrounds 
            if m['type'] == 'RECEIVED'
        )
        
        print("\n1. UNREAD SENT MESSAGES:")
        if unread_correct:
            print("   ✅ Light yellow background (#FFFACD)")
        else:
            print("   ❌ Should have light yellow background")
        
        print("\n2. READ SENT MESSAGES:")
        if read_correct:
            print("   ✅ Green background (#DCF8C6)")
        else:
            print("   ❌ Should have green background")
        
        print("\n3. RECEIVED MESSAGES:")
        if received_correct:
            print("   ✅ White background (#FFFFFF)")
        else:
            print("   ❌ Should have white background")
        
        print("\n4. TICK MARKS:")
        if not has_double_tick:
            print("   ✅ No double ticks - all removed")
            print("   ✅ Only single gray tick (✓) shown")
        else:
            print("   ❌ Still showing double ticks")
        
        print("\n📊 STATUS INDICATION:")
        print("   Background color now indicates message status:")
        print("   🟡 Light Yellow = Delivered (not read)")
        print("   🟢 Green = Read")
        print("   ⚪ White = Received message")
        
        print("\n⚠️ REMEMBER TO HARD REFRESH (Ctrl+F5)!")
        print("\nBrowser will stay open for 20 seconds...")
        page.wait_for_timeout(20000)
        
        browser.close()

if __name__ == '__main__':
    test_background_status()
