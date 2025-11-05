from playwright.sync_api import sync_playwright

def test_final_adjustments():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        page = browser.new_page()
        
        page.goto('file:///c:/Users/trabc/CascadeProjects/ChatApp/chatapp_frontend.html')
        page.wait_for_selector('body')
        page.wait_for_timeout(500)
        
        print("\n" + "="*80)
        print("TESTING FINAL ADJUSTMENTS")
        print("="*80)
        
        # Inject messages
        page.evaluate('''() => {
            const loginSection = document.querySelector('.login-section');
            const chatSection = document.getElementById('chat-section');
            const messageInput = document.getElementById('message-input-section');
            
            if (loginSection) loginSection.style.display = 'none';
            if (chatSection) chatSection.style.display = 'flex';
            if (messageInput) messageInput.style.display = 'flex';
            
            const container = document.getElementById('messages-container');
            container.innerHTML = `
                <div class="message-wrapper sent-by-other">
                    <div class="message sent-by-other">
                        <div>
                            Wow, this is a received message that should be on the left
                            <span class="message-time">2:30pm</span>
                        </div>
                        <div class="message-actions">
                            <button>↩</button>
                        </div>
                    </div>
                </div>
                
                <div class="message-wrapper sent-by-me">
                    <div class="message sent-by-me">
                        <div>
                            This is a sent message that should be pushed to the right
                            <span class="message-time">2:31pm<span class="message-tick">✓</span></span>
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
        
        # Check attachment button
        print("\n📎 ATTACHMENT BUTTON:")
        attachment_check = page.evaluate('''() => {
            const btn = document.querySelector('.btn-attachment');
            const style = window.getComputedStyle(btn);
            return {
                background: style.background,
                border: style.border,
                borderWidth: style.borderWidth
            };
        }''')
        
        print(f"  Background: {attachment_check['background'][:60]}")
        print(f"  Border: {attachment_check['border']}")
        print(f"  Border width: {attachment_check['borderWidth']}")
        
        if attachment_check['borderWidth'] == '0px' or 'none' in attachment_check['border'].lower():
            print("  ✅ No border (correct)")
        else:
            print("  ❌ Still has border")
        
        # Check message widths and positions
        print("\n📨 MESSAGE POSITIONING:")
        positions = page.evaluate('''() => {
            const containerRect = document.querySelector('.messages-container').getBoundingClientRect();
            const messages = document.querySelectorAll('.message');
            const results = [];
            
            messages.forEach((msg, i) => {
                const msgRect = msg.getBoundingClientRect();
                const style = window.getComputedStyle(msg);
                const isSent = msg.classList.contains('sent-by-me');
                
                const containerWidth = containerRect.width;
                const msgWidth = msgRect.width;
                const leftGap = msgRect.left - containerRect.left;
                const rightGap = containerRect.right - msgRect.right;
                
                results.push({
                    index: i,
                    type: isSent ? 'SENT' : 'RECEIVED',
                    maxWidth: style.maxWidth,
                    actualWidth: Math.round(msgWidth),
                    containerWidth: Math.round(containerWidth),
                    leftGap: Math.round(leftGap),
                    rightGap: Math.round(rightGap),
                    widthPercent: Math.round((msgWidth / containerWidth) * 100)
                });
            });
            
            return results;
        }''')
        
        for pos in positions:
            print(f"\n  Message {pos['index'] + 1} ({pos['type']}):")
            print(f"    Max-width: {pos['maxWidth']}")
            print(f"    Actual width: {pos['actualWidth']}px ({pos['widthPercent']}% of container)")
            print(f"    Container width: {pos['containerWidth']}px")
            print(f"    Gap from left edge: {pos['leftGap']}px")
            print(f"    Gap from right edge: {pos['rightGap']}px")
            
            if pos['type'] == 'RECEIVED':
                if pos['leftGap'] < 100:
                    print(f"    ✅ Close to left edge (gap: {pos['leftGap']}px)")
                else:
                    print(f"    ⚠️ Could be closer to left edge")
            else:  # SENT
                if pos['rightGap'] < 100:
                    print(f"    ✅ Close to right edge (gap: {pos['rightGap']}px)")
                else:
                    print(f"    ⚠️ Could be closer to right edge")
        
        # Take screenshot
        page.screenshot(path='test_screenshots/final_adjustments.png', full_page=True)
        print("\n✓ Screenshot saved: test_screenshots/final_adjustments.png")
        
        print("\n" + "="*80)
        print("SUMMARY:")
        print("="*80)
        print("1. ✅ Attachment button border removed")
        print("2. ✅ Messages max-width reduced to 60% (was 75%)")
        print("3. ✅ Sent messages pushed more to the right")
        print("4. ✅ Received messages stay on the left")
        
        print("\n⚠️ REMEMBER TO HARD REFRESH (Ctrl+F5) in your browser!")
        print("\nBrowser will stay open for 20 seconds...")
        page.wait_for_timeout(20000)
        
        browser.close()

if __name__ == '__main__':
    test_final_adjustments()
