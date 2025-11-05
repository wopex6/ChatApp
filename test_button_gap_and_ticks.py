from playwright.sync_api import sync_playwright

def test_button_gap_and_ticks():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        page = browser.new_page()
        
        page.goto('file:///c:/Users/trabc/CascadeProjects/ChatApp/chatapp_frontend.html')
        page.wait_for_selector('body')
        page.wait_for_timeout(500)
        
        print("\n" + "="*80)
        print("TESTING: BUTTON GAP & TICK COLORS")
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
                    <div class="message sent-by-me">
                        <div>
                            Unread message (single tick - should be light yellow)
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
                            Read message (double tick - should be blue)
                            <span class="message-time">2:31pm<span class="message-tick read">✓✓</span></span>
                        </div>
                        <div class="message-actions">
                            <button>↩</button>
                            <button>🗑</button>
                        </div>
                    </div>
                </div>
            `;
        }''')
        
        page.wait_for_timeout(1000)
        
        # Test 1: Check button gap
        print("\n🔘 BUTTON GAP TEST:")
        button_gap = page.evaluate('''() => {
            const container = document.querySelector('.input-actions');
            const style = window.getComputedStyle(container);
            const buttons = container.querySelectorAll('button');
            
            const gaps = [];
            for (let i = 0; i < buttons.length - 1; i++) {
                const rect1 = buttons[i].getBoundingClientRect();
                const rect2 = buttons[i + 1].getBoundingClientRect();
                gaps.push(Math.round(rect2.left - rect1.right));
            }
            
            return {
                cssGap: style.gap,
                actualGaps: gaps,
                buttonCount: buttons.length
            };
        }''')
        
        print(f"  CSS gap: {button_gap['cssGap']}")
        print(f"  Button count: {button_gap['buttonCount']}")
        print(f"  Actual gaps between buttons:")
        for i, gap in enumerate(button_gap['actualGaps']):
            print(f"    Gap {i+1}: {gap}px")
        
        if button_gap['cssGap'] == '2.5px':
            print(f"  ✅ Gap reduced to 2.5px (was 5px - halved)")
        else:
            print(f"  ❌ Gap should be 2.5px, found: {button_gap['cssGap']}")
        
        # Test 2: Check tick colors
        print("\n✓ TICK COLOR TEST:")
        tick_colors = page.evaluate('''() => {
            const ticks = document.querySelectorAll('.message-tick');
            return Array.from(ticks).map((tick, i) => {
                const style = window.getComputedStyle(tick);
                const isRead = tick.classList.contains('read');
                return {
                    index: i,
                    text: tick.textContent.trim(),
                    isRead: isRead,
                    color: style.color,
                    class: tick.className
                };
            });
        }''')
        
        for tick in tick_colors:
            print(f"\n  Tick {tick['index'] + 1}:")
            print(f"    Content: '{tick['text']}'")
            print(f"    Class: {tick['class']}")
            print(f"    Color: {tick['color']}")
            
            # Convert rgb to hex for comparison
            rgb = tick['color']
            if 'rgb(255, 215, 0)' in rgb or '#FFD700' in rgb:
                print(f"    ✅ Light yellow (#FFD700) - Unread/Delivered state")
            elif 'rgb(79, 195, 247)' in rgb or '#4FC3F7' in rgb:
                print(f"    ✅ Blue (#4FC3F7) - Read state")
            else:
                print(f"    ⚠️  Unexpected color")
            
            if tick['isRead']:
                if 'rgb(79, 195, 247)' in rgb:
                    print(f"    ✅ Read message has blue double tick (correct)")
                else:
                    print(f"    ❌ Read message should be blue")
            else:
                if 'rgb(255, 215, 0)' in rgb:
                    print(f"    ✅ Unread message has yellow single tick (correct)")
                else:
                    print(f"    ❌ Unread message should be yellow")
        
        # Take screenshots
        page.screenshot(path='test_screenshots/button_gap_and_ticks.png', full_page=True)
        print("\n✓ Screenshot saved: button_gap_and_ticks.png")
        
        # Visual comparison of buttons
        print("\n🔍 BUTTON SPACING VISUAL:")
        button_positions = page.evaluate('''() => {
            const buttons = document.querySelectorAll('.input-actions button');
            return Array.from(buttons).map((btn, i) => {
                const rect = btn.getBoundingClientRect();
                return {
                    index: i,
                    emoji: btn.textContent.trim(),
                    left: Math.round(rect.left),
                    right: Math.round(rect.right),
                    width: Math.round(rect.width)
                };
            });
        }''')
        
        for i, btn in enumerate(button_positions):
            gap_text = ""
            if i < len(button_positions) - 1:
                gap = button_positions[i + 1]['left'] - btn['right']
                gap_text = f" → gap: {gap}px →"
            print(f"  [{btn['emoji']}] {btn['left']}-{btn['right']} (width: {btn['width']}px){gap_text}")
        
        print("\n" + "="*80)
        print("SUMMARY:")
        print("="*80)
        
        print("\n1. BUTTON GAP:")
        if button_gap['cssGap'] == '2.5px':
            print("   ✅ Gap reduced from 5px to 2.5px (50% reduction)")
            print("   ✅ Buttons packed closer together")
        else:
            print(f"   ❌ Gap should be 2.5px, found: {button_gap['cssGap']}")
        
        print("\n2. TICK COLORS:")
        has_yellow = any('255, 215, 0' in t['color'] for t in tick_colors if not t['isRead'])
        has_blue = any('79, 195, 247' in t['color'] for t in tick_colors if t['isRead'])
        
        if has_yellow:
            print("   ✅ Single tick (unread) = Light yellow (#FFD700)")
        else:
            print("   ❌ Single tick should be yellow")
        
        if has_blue:
            print("   ✅ Double tick (read) = Blue (#4FC3F7)")
        else:
            print("   ❌ Double tick should be blue")
        
        print("\n⚠️ REMEMBER TO HARD REFRESH (Ctrl+F5)!")
        print("\nBrowser will stay open for 20 seconds...")
        page.wait_for_timeout(20000)
        
        browser.close()

if __name__ == '__main__':
    test_button_gap_and_ticks()
