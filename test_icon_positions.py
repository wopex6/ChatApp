from playwright.sync_api import sync_playwright

def test_icon_positions():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        page = browser.new_page()
        
        page.goto('file:///c:/Users/trabc/CascadeProjects/ChatApp/chatapp_frontend.html')
        page.wait_for_selector('body')
        page.wait_for_timeout(500)
        
        print("\n" + "="*80)
        print("ICON POSITION TEST - FORCING ICONS TO SHOW")
        print("="*80)
        
        # Inject messages and force icons to show
        page.evaluate('''() => {
            const loginSection = document.querySelector('.login-section');
            const chatSection = document.getElementById('chat-section');
            const messageInput = document.getElementById('message-input-section');
            
            if (loginSection) loginSection.style.display = 'none';
            if (chatSection) chatSection.style.display = 'flex';
            if (messageInput) messageInput.style.display = 'flex';
            
            const container = document.getElementById('messages-container');
            container.innerHTML = '';
            
            container.innerHTML = `
                <div class="message-wrapper sent-by-other">
                    <div class="message sent-by-other">
                        <div>
                            Wow
                            <span class="message-time">2:30pm</span>
                        </div>
                        <div class="message-actions" style="display: flex !important;">
                            <button>↩</button>
                        </div>
                    </div>
                </div>
                
                <div class="message-wrapper sent-by-me">
                    <div class="message sent-by-me">
                        <div>
                            Test from right
                            <span class="message-time">2:31pm<span class="message-tick">✓</span></span>
                        </div>
                        <div class="message-actions" style="display: flex !important;">
                            <button>↩</button>
                            <button>🗑</button>
                        </div>
                    </div>
                </div>
            `;
        }''')
        
        page.wait_for_timeout(1000)
        print("✓ Messages with visible icons injected")
        
        # Take screenshot with icons showing
        page.screenshot(path='test_screenshots/icons_forced_visible.png', full_page=True)
        print("✓ Screenshot saved")
        
        # Check actual icon positions
        positions = page.evaluate('''() => {
            const results = [];
            const messages = document.querySelectorAll('.message');
            
            messages.forEach((msg, i) => {
                const actions = msg.querySelector('.message-actions');
                if (!actions) return;
                
                const msgRect = msg.getBoundingClientRect();
                const actRect = actions.getBoundingClientRect();
                const isSent = msg.classList.contains('sent-by-me');
                
                results.push({
                    index: i,
                    type: isSent ? 'SENT' : 'RECEIVED',
                    messageLeft: Math.round(msgRect.left),
                    messageRight: Math.round(msgRect.right),
                    messageWidth: Math.round(msgRect.width),
                    actionsLeft: Math.round(actRect.left),
                    actionsRight: Math.round(actRect.right),
                    actionsWidth: Math.round(actRect.width),
                    gap: isSent 
                        ? Math.round(msgRect.left - actRect.right)
                        : Math.round(actRect.left - msgRect.right)
                });
            });
            
            return results;
        }''')
        
        print("\n📏 ACTUAL ICON POSITIONS:")
        for pos in positions:
            print(f"\n  Message {pos['index'] + 1} ({pos['type']}):")
            print(f"    Message: {pos['messageLeft']}px to {pos['messageRight']}px (width: {pos['messageWidth']}px)")
            print(f"    Actions: {pos['actionsLeft']}px to {pos['actionsRight']}px (width: {pos['actionsWidth']}px)")
            print(f"    Gap: {pos['gap']}px")
            
            if pos['type'] == 'RECEIVED':
                if pos['actionsLeft'] > pos['messageRight']:
                    print(f"    ✅ Icons are to the RIGHT of message (correct)")
                    if abs(pos['gap'] - 5) <= 3:
                        print(f"    ✅ Gap is ~5px (correct)")
                    else:
                        print(f"    ⚠️  Gap should be ~5px")
                else:
                    print(f"    ❌ Icons NOT to the right of message!")
            else:  # SENT
                if pos['actionsRight'] < pos['messageLeft']:
                    print(f"    ✅ Icons are to the LEFT of message (correct)")
                    if abs(pos['gap'] - 5) <= 3:
                        print(f"    ✅ Gap is ~5px (correct)")
                    else:
                        print(f"    ⚠️  Gap should be ~5px")
                else:
                    print(f"    ❌ Icons NOT to the left of message!")
        
        print("\n" + "="*80)
        print("Browser will stay open for 20 seconds...")
        page.wait_for_timeout(20000)
        
        browser.close()

if __name__ == '__main__':
    test_icon_positions()
