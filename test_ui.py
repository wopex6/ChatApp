from playwright.sync_api import sync_playwright
import time

def test_chat_ui():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Open the HTML file directly
        page.goto('file:///c:/Users/trabc/CascadeProjects/ChatApp/chatapp_frontend.html')
        
        # Wait for page to load
        page.wait_for_timeout(2000)
        
        print("\n" + "="*80)
        print("TESTING CHAT UI")
        print("="*80)
        
        # Take initial screenshot
        page.screenshot(path='test_screenshots/ui_test_initial.png')
        print("✓ Initial screenshot saved")
        
        # Check if we need to login
        login_form = page.locator('#login-form')
        if login_form.is_visible():
            print("\n📝 Login required - logging in as Ken Tse...")
            page.fill('#login-username', 'Ken Tse')
            page.fill('#login-password', '123')
            page.click('button:has-text("Login")')
            page.wait_for_timeout(2000)
            page.screenshot(path='test_screenshots/ui_test_after_login.png')
            print("✓ Logged in successfully")
        
        # Wait for messages to load
        page.wait_for_timeout(2000)
        
        # Check message container
        print("\n🔍 Checking message container...")
        msg_container = page.locator('.messages-container')
        if msg_container.is_visible():
            container_style = page.evaluate('''() => {
                const container = document.querySelector('.messages-container');
                const style = window.getComputedStyle(container);
                return {
                    padding: style.padding,
                    overflow: style.overflow,
                    overflowX: style.overflowX,
                    overflowY: style.overflowY,
                    background: style.background
                };
            }''')
            print(f"  Container padding: {container_style['padding']}")
            print(f"  Overflow-X: {container_style['overflowX']}")
            print(f"  Overflow-Y: {container_style['overflowY']}")
            print(f"  Background: {container_style['background'][:50]}...")
        
        # Check send button
        print("\n🔍 Checking send button...")
        send_button = page.locator('.btn-send')
        if send_button.is_visible():
            btn_style = page.evaluate('''() => {
                const btn = document.querySelector('.btn-send');
                const style = window.getComputedStyle(btn);
                return {
                    content: btn.textContent,
                    background: style.background,
                    border: style.border,
                    padding: style.padding,
                    width: btn.offsetWidth
                };
            }''')
            print(f"  Button content: '{btn_style['content']}'")
            print(f"  Background: {btn_style['background'][:50]}")
            print(f"  Border: {btn_style['border']}")
            print(f"  Padding: {btn_style['padding']}")
            print(f"  Width: {btn_style['width']}px")
        
        # Check if there are messages
        messages = page.locator('.message').all()
        print(f"\n📨 Found {len(messages)} messages")
        
        if len(messages) > 0:
            print("\n🔍 Checking message positioning...")
            for i, msg in enumerate(messages[:3]):  # Check first 3 messages
                msg_info = page.evaluate('''(index) => {
                    const messages = document.querySelectorAll('.message');
                    const msg = messages[index];
                    if (!msg) return null;
                    
                    const wrapper = msg.closest('.message-wrapper');
                    const actions = wrapper ? wrapper.querySelector('.message-actions') : null;
                    const msgStyle = window.getComputedStyle(msg);
                    const wrapperStyle = wrapper ? window.getComputedStyle(wrapper) : null;
                    
                    return {
                        class: msg.className,
                        float: msgStyle.float,
                        textAlign: wrapperStyle ? wrapperStyle.textAlign : null,
                        display: wrapperStyle ? wrapperStyle.display : null,
                        maxWidth: msgStyle.maxWidth,
                        hasActions: actions !== null,
                        actionsVisible: actions ? window.getComputedStyle(actions).display : null
                    };
                }''', i)
                
                if msg_info:
                    print(f"\n  Message {i+1}:")
                    print(f"    Class: {msg_info['class']}")
                    print(f"    Float: {msg_info['float']}")
                    print(f"    Wrapper text-align: {msg_info['textAlign']}")
                    print(f"    Wrapper display: {msg_info['display']}")
                    print(f"    Max-width: {msg_info['maxWidth']}")
                    print(f"    Has action icons: {msg_info['hasActions']}")
            
            # Hover over first message to see icons
            if len(messages) > 0:
                print("\n🖱️  Hovering over first message to check icons...")
                messages[0].hover()
                page.wait_for_timeout(500)
                page.screenshot(path='test_screenshots/ui_test_hover_message.png')
                print("✓ Hover screenshot saved")
                
                # Check icon positioning
                icon_info = page.evaluate('''() => {
                    const wrapper = document.querySelector('.message-wrapper');
                    const actions = wrapper ? wrapper.querySelector('.message-actions') : null;
                    if (!actions) return null;
                    
                    const style = window.getComputedStyle(actions);
                    const rect = actions.getBoundingClientRect();
                    const msgRect = wrapper.querySelector('.message').getBoundingClientRect();
                    
                    return {
                        display: style.display,
                        position: style.position,
                        left: style.left,
                        right: style.right,
                        top: style.top,
                        transform: style.transform,
                        actualLeft: rect.left,
                        actualTop: rect.top,
                        messageRight: msgRect.right,
                        messageLeft: msgRect.left
                    };
                }''')
                
                if icon_info:
                    print("\n  Icon positioning:")
                    print(f"    Display: {icon_info['display']}")
                    print(f"    Position: {icon_info['position']}")
                    print(f"    CSS left: {icon_info['left']}")
                    print(f"    CSS right: {icon_info['right']}")
                    print(f"    CSS top: {icon_info['top']}")
                    print(f"    Transform: {icon_info['transform']}")
                    print(f"    Actual position: {icon_info['actualLeft']}px from left")
                    print(f"    Message edge: {icon_info['messageRight']}px")
        
        # Check textarea
        print("\n🔍 Checking message input...")
        textarea = page.locator('#message-input')
        if textarea.is_visible():
            textarea_info = page.evaluate('''() => {
                const textarea = document.getElementById('message-input');
                const style = window.getComputedStyle(textarea);
                return {
                    tagName: textarea.tagName,
                    minHeight: style.minHeight,
                    maxHeight: style.maxHeight,
                    overflowY: style.overflowY,
                    resize: style.resize
                };
            }''')
            print(f"  Element type: {textarea_info['tagName']}")
            print(f"  Min height: {textarea_info['minHeight']}")
            print(f"  Max height: {textarea_info['maxHeight']}")
            print(f"  Overflow-Y: {textarea_info['overflowY']}")
            print(f"  Resize: {textarea_info['resize']}")
        
        # Take final screenshot
        page.screenshot(path='test_screenshots/ui_test_final.png', full_page=True)
        print("\n✓ Final full-page screenshot saved")
        
        print("\n" + "="*80)
        print("TEST COMPLETE - Check test_screenshots folder for images")
        print("="*80)
        
        # Keep browser open for manual inspection
        print("\nBrowser will stay open for 30 seconds for manual inspection...")
        page.wait_for_timeout(30000)
        
        browser.close()

if __name__ == '__main__':
    test_chat_ui()
