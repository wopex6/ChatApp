from playwright.sync_api import sync_playwright
import subprocess
import time
import os
import signal

def test_chat_ui_with_messages():
    # Start the backend server
    print("\n🚀 Starting backend server...")
    server_process = subprocess.Popen(
        ['python', 'app.py'],
        cwd=r'c:\Users\trabc\CascadeProjects\ChatApp',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
    )
    
    # Wait for server to start
    time.sleep(3)
    print("✓ Server started")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=500)
            page = browser.new_page()
            
            # Open the application
            page.goto('http://localhost:5000')
            page.wait_for_timeout(2000)
            
            print("\n" + "="*80)
            print("TESTING CHAT UI WITH REAL MESSAGES")
            print("="*80)
            
            # Login as Ken Tse
            print("\n📝 Logging in as Ken Tse...")
            page.fill('#login-username', 'Ken Tse')
            page.fill('#login-password', '123')
            page.click('button:has-text("Login")')
            page.wait_for_timeout(3000)
            
            # Click on first user in the list
            print("👤 Selecting a user...")
            user_items = page.locator('.user-item').all()
            if len(user_items) > 0:
                user_items[0].click()
                page.wait_for_timeout(2000)
                print(f"✓ Selected user")
            
            # Count messages
            messages = page.locator('.message').all()
            print(f"\n📨 Found {len(messages)} existing messages")
            
            # Send a test message
            print("\n✉️  Sending test messages...")
            page.fill('#message-input', 'Test message from right side')
            page.click('.btn-send')
            page.wait_for_timeout(1500)
            
            # Take screenshot after sending
            page.screenshot(path='test_screenshots/ui_with_messages.png', full_page=True)
            print("✓ Screenshot taken")
            
            # Check actual CSS
            print("\n🔍 Checking ACTUAL applied CSS...")
            
            css_check = page.evaluate('''() => {
                const results = {};
                
                // Check container
                const container = document.querySelector('.messages-container');
                if (container) {
                    const cs = window.getComputedStyle(container);
                    results.container = {
                        padding: cs.padding,
                        paddingLeft: cs.paddingLeft,
                        paddingRight: cs.paddingRight,
                        overflowX: cs.overflowX
                    };
                }
                
                // Check messages
                const messages = document.querySelectorAll('.message');
                results.messageCount = messages.length;
                results.messages = [];
                
                messages.forEach((msg, i) => {
                    if (i < 3) {  // First 3 messages
                        const cs = window.getComputedStyle(msg);
                        const wrapper = msg.closest('.message-wrapper');
                        const ws = wrapper ? window.getComputedStyle(wrapper) : null;
                        const actions = wrapper ? wrapper.querySelector('.message-actions') : null;
                        const as = actions ? window.getComputedStyle(actions) : null;
                        
                        results.messages.push({
                            index: i,
                            class: msg.className,
                            float: cs.float,
                            maxWidth: cs.maxWidth,
                            background: cs.backgroundColor,
                            wrapperDisplay: ws ? ws.display : null,
                            wrapperTextAlign: ws ? ws.textAlign : null,
                            hasActions: actions !== null,
                            actionsPosition: as ? as.position : null,
                            actionsLeft: as ? as.left : null,
                            actionsRight: as ? as.right : null,
                            actionsDisplay: as ? as.display : null
                        });
                    }
                });
                
                // Check send button
                const sendBtn = document.querySelector('.btn-send');
                if (sendBtn) {
                    const cs = window.getComputedStyle(sendBtn);
                    results.sendButton = {
                        content: sendBtn.textContent.trim(),
                        background: cs.background,
                        border: cs.border,
                        padding: cs.padding
                    };
                }
                
                // Check textarea
                const textarea = document.querySelector('#message-input');
                if (textarea) {
                    const cs = window.getComputedStyle(textarea);
                    results.textarea = {
                        tagName: textarea.tagName,
                        minHeight: cs.minHeight,
                        maxHeight: cs.maxHeight,
                        overflowY: cs.overflowY
                    };
                }
                
                return results;
            }''')
            
            # Print results
            print("\n📋 Container:")
            print(f"  Padding: {css_check['container']['padding']}")
            print(f"  Padding Left/Right: {css_check['container']['paddingLeft']} / {css_check['container']['paddingRight']}")
            print(f"  Overflow-X: {css_check['container']['overflowX']}")
            
            print(f"\n📨 Messages ({css_check['messageCount']} total):")
            for msg in css_check['messages']:
                print(f"\n  Message {msg['index'] + 1} ({msg['class']}):")
                print(f"    Float: {msg['float']}")
                print(f"    Max-width: {msg['maxWidth']}")
                print(f"    Background: {msg['background']}")
                print(f"    Wrapper display: {msg['wrapperDisplay']}")
                print(f"    Wrapper text-align: {msg['wrapperTextAlign']}")
                if msg['hasActions']:
                    print(f"    ✓ Has action icons")
                    print(f"      Position: {msg['actionsPosition']}")
                    print(f"      Left: {msg['actionsLeft']}")
                    print(f"      Right: {msg['actionsRight']}")
                    print(f"      Display: {msg['actionsDisplay']}")
                else:
                    print(f"    ✗ No action icons found")
            
            print(f"\n🔘 Send Button:")
            if 'sendButton' in css_check:
                print(f"  Content: '{css_check['sendButton']['content']}'")
                print(f"  Background: {css_check['sendButton']['background'][:80]}")
                print(f"  Border: {css_check['sendButton']['border']}")
                print(f"  Padding: {css_check['sendButton']['padding']}")
            
            print(f"\n📝 Textarea:")
            if 'textarea' in css_check:
                print(f"  Tag: {css_check['textarea']['tagName']}")
                print(f"  Min-height: {css_check['textarea']['minHeight']}")
                print(f"  Max-height: {css_check['textarea']['maxHeight']}")
                print(f"  Overflow-Y: {css_check['textarea']['overflowY']}")
            
            # Hover over a message to see icons
            if len(messages) > 0:
                print("\n🖱️  Hovering over last message to check icon positioning...")
                messages[-1].hover()
                page.wait_for_timeout(1000)
                page.screenshot(path='test_screenshots/ui_hover_icons.png')
                print("✓ Hover screenshot saved")
                
                # Check icon position when hovering
                icon_position = page.evaluate('''() => {
                    const wrappers = document.querySelectorAll('.message-wrapper');
                    const lastWrapper = wrappers[wrappers.length - 1];
                    const message = lastWrapper.querySelector('.message');
                    const actions = lastWrapper.querySelector('.message-actions');
                    
                    if (!message || !actions) return null;
                    
                    const msgRect = message.getBoundingClientRect();
                    const actRect = actions.getBoundingClientRect();
                    const cs = window.getComputedStyle(actions);
                    
                    return {
                        messageClass: message.className,
                        messageLeft: Math.round(msgRect.left),
                        messageRight: Math.round(msgRect.right),
                        actionsLeft: Math.round(actRect.left),
                        actionsRight: Math.round(actRect.right),
                        actionsDisplay: cs.display,
                        gap: message.className.includes('sent-by-me') 
                            ? Math.round(msgRect.left - actRect.right)
                            : Math.round(actRect.left - msgRect.right)
                    };
                }''')
                
                if icon_position:
                    print(f"\n  Icon position details:")
                    print(f"    Message class: {icon_position['messageClass']}")
                    print(f"    Message: {icon_position['messageLeft']}px to {icon_position['messageRight']}px")
                    print(f"    Actions: {icon_position['actionsLeft']}px to {icon_position['actionsRight']}px")
                    print(f"    Actions display: {icon_position['actionsDisplay']}")
                    print(f"    Gap between message and icons: {icon_position['gap']}px")
            
            print("\n" + "="*80)
            print("TEST COMPLETE")
            print("="*80)
            print("\nScreenshots saved:")
            print("  - test_screenshots/ui_with_messages.png")
            print("  - test_screenshots/ui_hover_icons.png")
            
            # Keep browser open
            print("\nBrowser will stay open for 20 seconds...")
            page.wait_for_timeout(20000)
            
            browser.close()
    
    finally:
        # Stop the server
        print("\n🛑 Stopping server...")
        os.kill(server_process.pid, signal.CTRL_BREAK_EVENT)
        server_process.wait()
        print("✓ Server stopped")

if __name__ == '__main__':
    test_chat_ui_with_messages()
