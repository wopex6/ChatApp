from playwright.sync_api import sync_playwright

def test_positioning():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        page = browser.new_page()
        
        # Open HTML file directly
        page.goto('file:///c:/Users/trabc/CascadeProjects/ChatApp/chatapp_frontend.html')
        page.wait_for_timeout(1000)
        
        print("\n" + "="*80)
        print("DIRECT CSS AND POSITIONING TEST")
        print("="*80)
        
        # Wait for page to be fully loaded
        page.wait_for_selector('body')
        page.wait_for_timeout(500)
        
        # Inject test messages directly into the DOM
        print("\n📝 Injecting test messages into DOM...")
        page.evaluate('''() => {
            // Hide login, show chat
            const loginSection = document.querySelector('.login-section');
            const chatSection = document.getElementById('chat-section');
            const messageInput = document.getElementById('message-input-section');
            
            if (loginSection) loginSection.style.display = 'none';
            if (chatSection) chatSection.style.display = 'flex';
            if (messageInput) messageInput.style.display = 'flex';
            
            // Get messages container
            const container = document.getElementById('messages-container');
            
            // Clear loading message
            container.innerHTML = '';
            
            // Add test messages with correct HTML structure (icons inside message)
            container.innerHTML = `
                <div class="message-wrapper sent-by-other">
                    <div class="message sent-by-other">
                        <div>
                            Wow
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
                            Test message from right side that is longer to see positioning
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
                            Another message from left
                            <span class="message-time">2:32pm</span>
                        </div>
                        <div class="message-actions">
                            <button>↩</button>
                        </div>
                    </div>
                </div>
                
                <div class="message-wrapper sent-by-me">
                    <div class="message sent-by-me">
                        <div>
                            Short reply
                            <span class="message-time">2:33pm<span class="message-tick read">✓✓</span></span>
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
        print("✓ Messages injected")
        
        # Take initial screenshot
        page.screenshot(path='test_screenshots/positioning_test_initial.png', full_page=True)
        print("✓ Initial screenshot saved")
        
        # Analyze CSS
        print("\n🔍 ANALYZING ACTUAL CSS...")
        
        analysis = page.evaluate('''() => {
            const results = {
                container: {},
                messages: [],
                sendButton: {},
                textarea: {}
            };
            
            // Container
            const container = document.querySelector('.messages-container');
            const containerStyle = window.getComputedStyle(container);
            results.container = {
                padding: containerStyle.padding,
                paddingLeft: containerStyle.paddingLeft,
                paddingRight: containerStyle.paddingRight,
                overflowX: containerStyle.overflowX,
                background: containerStyle.backgroundColor
            };
            
            // Messages
            const messages = document.querySelectorAll('.message');
            messages.forEach((msg, i) => {
                const msgStyle = window.getComputedStyle(msg);
                const wrapper = msg.closest('.message-wrapper');
                const wrapperStyle = window.getComputedStyle(wrapper);
                const actions = wrapper.querySelector('.message-actions');
                const actionsStyle = actions ? window.getComputedStyle(actions) : null;
                
                const msgRect = msg.getBoundingClientRect();
                const actRect = actions ? actions.getBoundingClientRect() : null;
                
                results.messages.push({
                    index: i,
                    class: msg.className,
                    // Message styles
                    float: msgStyle.float,
                    maxWidth: msgStyle.maxWidth,
                    background: msgStyle.backgroundColor,
                    borderRadius: msgStyle.borderRadius,
                    // Wrapper styles
                    wrapperDisplay: wrapperStyle.display,
                    wrapperTextAlign: wrapperStyle.textAlign,
                    wrapperOverflow: wrapperStyle.overflow,
                    // Position
                    msgLeft: Math.round(msgRect.left),
                    msgRight: Math.round(msgRect.right),
                    msgWidth: Math.round(msgRect.width),
                    // Actions
                    hasActions: actions !== null,
                    actionsPosition: actionsStyle ? actionsStyle.position : null,
                    actionsLeft: actionsStyle ? actionsStyle.left : null,
                    actionsRight: actionsStyle ? actionsStyle.right : null,
                    actionsTop: actionsStyle ? actionsStyle.top : null,
                    actionsTransform: actionsStyle ? actionsStyle.transform : null,
                    actionsDisplay: actionsStyle ? actionsStyle.display : null,
                    actRectLeft: actRect ? Math.round(actRect.left) : null,
                    actRectRight: actRect ? Math.round(actRect.right) : null
                });
            });
            
            // Send button
            const sendBtn = document.querySelector('.btn-send');
            const sendStyle = window.getComputedStyle(sendBtn);
            results.sendButton = {
                content: sendBtn ? sendBtn.textContent.trim() : 'NOT FOUND',
                background: sendStyle.background.substring(0, 100),
                border: sendStyle.border,
                padding: sendStyle.padding,
                fontSize: sendStyle.fontSize
            };
            
            // Textarea
            const textarea = document.querySelector('#message-input');
            const textareaStyle = window.getComputedStyle(textarea);
            results.textarea = {
                tagName: textarea.tagName,
                minHeight: textareaStyle.minHeight,
                maxHeight: textareaStyle.maxHeight,
                overflowY: textareaStyle.overflowY,
                resize: textareaStyle.resize
            };
            
            return results;
        }''')
        
        # Print analysis
        print("\n📦 CONTAINER:")
        print(f"  Background: {analysis['container']['background']}")
        print(f"  Padding: {analysis['container']['padding']}")
        print(f"  Padding L/R: {analysis['container']['paddingLeft']} / {analysis['container']['paddingRight']}")
        print(f"  Overflow-X: {analysis['container']['overflowX']}")
        
        print(f"\n📨 MESSAGES ({len(analysis['messages'])} total):")
        for msg in analysis['messages']:
            is_sent = 'sent-by-me' in msg['class']
            print(f"\n  Message {msg['index'] + 1} ({'SENT' if is_sent else 'RECEIVED'}):")
            print(f"    Class: {msg['class']}")
            print(f"    Float: {msg['float']}")
            print(f"    Max-width: {msg['maxWidth']}")
            print(f"    Background: {msg['background']}")
            print(f"    Wrapper display: {msg['wrapperDisplay']}")
            print(f"    Wrapper text-align: {msg['wrapperTextAlign']}")
            print(f"    Position: {msg['msgLeft']}px to {msg['msgRight']}px (width: {msg['msgWidth']}px)")
            
            if msg['hasActions']:
                print(f"    ✓ Action icons:")
                print(f"      CSS position: {msg['actionsPosition']}")
                print(f"      CSS left: {msg['actionsLeft']}")
                print(f"      CSS right: {msg['actionsRight']}")
                print(f"      CSS top: {msg['actionsTop']}")
                print(f"      CSS transform: {msg['actionsTransform']}")
                print(f"      Display: {msg['actionsDisplay']}")
                print(f"      Actual position: {msg['actRectLeft']}px to {msg['actRectRight']}px")
                
                # Calculate gap
                if is_sent and msg['actRectRight']:
                    gap = msg['msgLeft'] - msg['actRectRight']
                    print(f"      Gap from message: {gap}px (should be ~5px)")
                elif not is_sent and msg['actRectLeft']:
                    gap = msg['actRectLeft'] - msg['msgRight']
                    print(f"      Gap from message: {gap}px (should be ~5px)")
        
        print(f"\n🔘 SEND BUTTON:")
        print(f"  Content: '{analysis['sendButton']['content']}'")
        print(f"  Background: {analysis['sendButton']['background']}")
        print(f"  Border: {analysis['sendButton']['border']}")
        print(f"  Padding: {analysis['sendButton']['padding']}")
        print(f"  Font size: {analysis['sendButton']['fontSize']}")
        
        print(f"\n📝 TEXTAREA:")
        print(f"  Element: {analysis['textarea']['tagName']}")
        print(f"  Min-height: {analysis['textarea']['minHeight']}")
        print(f"  Max-height: {analysis['textarea']['maxHeight']}")
        print(f"  Overflow-Y: {analysis['textarea']['overflowY']}")
        print(f"  Resize: {analysis['textarea']['resize']}")
        
        # Hover over messages
        print("\n🖱️  Testing hover effects...")
        messages = page.locator('.message').all()
        
        for i, msg in enumerate(messages):
            msg.hover()
            page.wait_for_timeout(500)
            page.screenshot(path=f'test_screenshots/positioning_hover_msg{i+1}.png')
            print(f"  ✓ Message {i+1} hover screenshot saved")
        
        page.screenshot(path='test_screenshots/positioning_test_final.png', full_page=True)
        print("\n✓ Final screenshot saved")
        
        print("\n" + "="*80)
        print("PROBLEMS FOUND:")
        print("="*80)
        
        # Analyze problems
        problems = []
        
        for msg in analysis['messages']:
            is_sent = 'sent-by-me' in msg['class']
            
            # Check float
            if msg['float'] == 'none':
                problems.append(f"❌ Message {msg['index']+1}: float is 'none', should be 'left' or 'right'")
            
            # Check wrapper display
            if msg['wrapperDisplay'] != 'block':
                problems.append(f"❌ Message {msg['index']+1}: wrapper display is '{msg['wrapperDisplay']}', should be 'block'")
        
        # Check send button
        if analysis['sendButton']['content'] != '➤':
            problems.append(f"❌ Send button shows '{analysis['sendButton']['content']}', should be '➤'")
        
        if 'none' not in analysis['sendButton']['border'].lower():
            problems.append(f"❌ Send button has border: {analysis['sendButton']['border']}")
        
        # Check textarea
        if analysis['textarea']['tagName'] != 'TEXTAREA':
            problems.append(f"❌ Message input is {analysis['textarea']['tagName']}, should be TEXTAREA")
        
        if problems:
            for p in problems:
                print(p)
        else:
            print("✅ No problems found!")
        
        print("\n" + "="*80)
        print("Browser will stay open for 30 seconds for inspection...")
        page.wait_for_timeout(30000)
        
        browser.close()

if __name__ == '__main__':
    test_positioning()
