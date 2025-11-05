from playwright.sync_api import sync_playwright

def test_three_fixes():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        page = browser.new_page()
        
        page.goto('file:///c:/Users/trabc/CascadeProjects/ChatApp/chatapp_frontend.html')
        page.wait_for_selector('body')
        page.wait_for_timeout(500)
        
        print("\n" + "="*80)
        print("TESTING: 1) TICK REMOVAL, 2) SCROLLABLE LISTS, 3) BUTTON GAP")
        print("="*80)
        
        # Inject messages to test tick removal
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
                            Unread message
                            <span class="message-time">2:30pm</span>
                        </div>
                    </div>
                </div>
                
                <div class="message-wrapper sent-by-me">
                    <div class="message sent-by-me">
                        <div>
                            Read message
                            <span class="message-time">2:31pm</span>
                        </div>
                    </div>
                </div>
            `;
        }''')
        
        page.wait_for_timeout(1000)
        
        # Test 1: Check for tick marks
        print("\n✓ TEST 1: TICK REMOVAL")
        tick_check = page.evaluate('''() => {
            const ticks = document.querySelectorAll('.message-tick');
            const messageTimeSpans = document.querySelectorAll('.message-time');
            
            return {
                tickCount: ticks.length,
                messageTimeCount: messageTimeSpans.length,
                timeContents: Array.from(messageTimeSpans).map(span => span.textContent.trim())
            };
        }''')
        
        print(f"  Found {tick_check['tickCount']} tick elements (.message-tick)")
        print(f"  Found {tick_check['messageTimeCount']} message times")
        for i, content in enumerate(tick_check['timeContents']):
            print(f"    Time {i+1}: '{content}'")
            if '✓' in content:
                print(f"      ❌ Still has tick mark!")
            else:
                print(f"      ✅ No tick mark")
        
        if tick_check['tickCount'] == 0:
            print(f"  ✅ SUCCESS: No .message-tick elements found")
        else:
            print(f"  ❌ ISSUE: Still has {tick_check['tickCount']} tick elements")
        
        # Test 2: Check button gap
        print("\n🔘 TEST 2: BUTTON GAP")
        button_gap = page.evaluate('''() => {
            const container = document.querySelector('.input-actions');
            if (!container) return { exists: false };
            
            const style = window.getComputedStyle(container);
            const buttons = container.querySelectorAll('button');
            
            const gaps = [];
            for (let i = 0; i < buttons.length - 1; i++) {
                const rect1 = buttons[i].getBoundingClientRect();
                const rect2 = buttons[i + 1].getBoundingClientRect();
                gaps.push(Math.round(rect2.left - rect1.right));
            }
            
            return {
                exists: true,
                cssGap: style.gap,
                columnGap: style.columnGap,
                actualGaps: gaps,
                buttonCount: buttons.length
            };
        }''')
        
        if button_gap['exists']:
            print(f"  CSS gap property: {button_gap['cssGap']}")
            print(f"  CSS column-gap property: {button_gap['columnGap']}")
            print(f"  Button count: {button_gap['buttonCount']}")
            print(f"  Actual measured gaps:")
            for i, gap in enumerate(button_gap['actualGaps']):
                print(f"    Gap {i+1}: {gap}px")
            
            # Check if gap is 2.5px or close to it
            avg_gap = sum(button_gap['actualGaps']) / len(button_gap['actualGaps']) if button_gap['actualGaps'] else 0
            print(f"  Average gap: {avg_gap:.1f}px")
            
            if avg_gap <= 3:
                print(f"  ✅ Gap is small (≤3px)")
            else:
                print(f"  ❌ Gap is still large (>{avg_gap}px)")
                print(f"  ⚠️  Expected ~2.5px, browser may have cached old CSS")
        else:
            print(f"  ❌ .input-actions not found")
        
        # Test 3: Check scrollable lists
        print("\n📜 TEST 3: SCROLLABLE LISTS")
        
        # Check admin tabs
        scroll_check = page.evaluate('''() => {
            const checks = [];
            
            // Check user-list (conversations)
            const userList = document.getElementById('user-list');
            if (userList) {
                const style = window.getComputedStyle(userList);
                const parent = userList.parentElement;
                const parentStyle = parent ? window.getComputedStyle(parent) : null;
                
                checks.push({
                    name: 'user-list (conversations)',
                    overflowY: style.overflowY,
                    flex: style.flex,
                    height: style.height,
                    scrollHeight: userList.scrollHeight,
                    clientHeight: userList.clientHeight,
                    parentOverflow: parentStyle ? parentStyle.overflowY : 'N/A',
                    parentId: parent ? parent.id : 'N/A'
                });
            }
            
            // Check all-users-list
            const allUsersList = document.getElementById('all-users-list');
            if (allUsersList) {
                const style = window.getComputedStyle(allUsersList);
                const parent = allUsersList.parentElement;
                const parentStyle = parent ? window.getComputedStyle(parent) : null;
                
                checks.push({
                    name: 'all-users-list (user management)',
                    overflowY: style.overflowY,
                    flex: style.flex,
                    height: style.height,
                    scrollHeight: allUsersList.scrollHeight,
                    clientHeight: allUsersList.clientHeight,
                    parentOverflow: parentStyle ? parentStyle.overflowY : 'N/A',
                    parentId: parent ? parent.id : 'N/A'
                });
            }
            
            // Check admin-conversations-tab
            const convTab = document.getElementById('admin-conversations-tab');
            if (convTab) {
                const style = window.getComputedStyle(convTab);
                checks.push({
                    name: 'admin-conversations-tab (parent)',
                    overflowY: style.overflowY,
                    flex: style.flex,
                    height: style.height,
                    display: style.display,
                    flexDirection: style.flexDirection
                });
            }
            
            // Check admin-users-tab
            const usersTab = document.getElementById('admin-users-tab');
            if (usersTab) {
                const style = window.getComputedStyle(usersTab);
                checks.push({
                    name: 'admin-users-tab (parent)',
                    overflowY: style.overflowY,
                    flex: style.flex,
                    height: style.height,
                    display: style.display,
                    flexDirection: style.flexDirection
                });
            }
            
            return checks;
        }''')
        
        for check in scroll_check:
            print(f"\n  {check['name']}:")
            print(f"    overflow-y: {check['overflowY']}")
            print(f"    flex: {check.get('flex', 'N/A')}")
            print(f"    height: {check.get('height', 'N/A')}")
            
            if 'display' in check:
                print(f"    display: {check['display']}")
                print(f"    flex-direction: {check.get('flexDirection', 'N/A')}")
            
            if 'scrollHeight' in check:
                print(f"    scroll height: {check['scrollHeight']}px")
                print(f"    client height: {check['clientHeight']}px")
                print(f"    parent overflow-y: {check.get('parentOverflow', 'N/A')}")
                print(f"    parent id: {check.get('parentId', 'N/A')}")
                
                if check['overflowY'] == 'auto':
                    print(f"    ✅ Has overflow-y: auto")
                else:
                    print(f"    ❌ No overflow-y: auto (found: {check['overflowY']})")
        
        # Take screenshots
        page.screenshot(path='test_screenshots/three_fixes.png', full_page=True)
        print("\n✓ Screenshot saved: three_fixes.png")
        
        print("\n" + "="*80)
        print("SUMMARY:")
        print("="*80)
        
        print("\n1. TICK REMOVAL:")
        if tick_check['tickCount'] == 0:
            print("   ✅ All ticks removed from messages")
        else:
            print(f"   ❌ Still has {tick_check['tickCount']} tick elements")
        
        print("\n2. BUTTON GAP:")
        if button_gap['exists']:
            avg_gap = sum(button_gap['actualGaps']) / len(button_gap['actualGaps']) if button_gap['actualGaps'] else 0
            print(f"   CSS gap: {button_gap['cssGap']}")
            print(f"   Actual gap: {avg_gap:.1f}px")
            if avg_gap <= 3:
                print("   ✅ Buttons closer together")
            else:
                print("   ❌ Gap still large - likely browser cache issue")
                print("   💡 SOLUTION: Press Ctrl+Shift+Del and clear cache")
        
        print("\n3. SCROLLABLE LISTS:")
        has_auto = any(c['overflowY'] == 'auto' for c in scroll_check if 'overflowY' in c)
        if has_auto:
            print("   ✅ Lists have overflow-y: auto")
        else:
            print("   ❌ Lists don't have overflow-y: auto")
        
        print("\n⚠️ CRITICAL: CLEAR BROWSER CACHE!")
        print("   The CSS changes won't apply with cached files.")
        print("   Press Ctrl+Shift+Del → Clear cached files")
        print("\nBrowser will stay open for 30 seconds...")
        page.wait_for_timeout(30000)
        
        browser.close()

if __name__ == '__main__':
    test_three_fixes()
