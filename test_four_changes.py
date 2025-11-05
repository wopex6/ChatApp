from playwright.sync_api import sync_playwright

def test_four_changes():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        page = browser.new_page()
        
        page.goto('file:///c:/Users/trabc/CascadeProjects/ChatApp/chatapp_frontend.html')
        page.wait_for_selector('body')
        page.wait_for_timeout(500)
        
        print("\n" + "="*80)
        print("TESTING: 1) REMOVE MESSAGES, 2) REMOVE ONLINE, 3) YELLOW, 4) HIDE CHATAPP")
        print("="*80)
        
        # Test 1: Check if header with ChatApp is hidden
        print("\n📋 TEST 1: CHATAPP HEADER SECTION")
        header_check = page.evaluate('''() => {
            const header = document.querySelector('.header');
            if (!header) return { exists: false };
            
            const style = window.getComputedStyle(header);
            const h1 = header.querySelector('h1');
            
            return {
                exists: true,
                display: style.display,
                h1Text: h1 ? h1.textContent : 'N/A'
            };
        }''')
        
        if header_check['exists']:
            print(f"  Element exists: Yes")
            print(f"  Display: {header_check['display']}")
            print(f"  Text: '{header_check['h1Text']}'")
            
            if header_check['display'] == 'none':
                print(f"  ✅ ChatApp header hidden (display: none)")
            else:
                print(f"  ❌ ChatApp header still visible")
        else:
            print(f"  Element not found")
        
        # Test 2: Check if "Messages" title is empty
        print("\n📋 TEST 2: MESSAGES TITLE")
        title_check = page.evaluate('''() => {
            const title = document.getElementById('chat-title');
            if (!title) return { exists: false };
            
            return {
                exists: true,
                text: title.textContent,
                isEmpty: title.textContent.trim() === ''
            };
        }''')
        
        if title_check['exists']:
            print(f"  Element exists: Yes")
            print(f"  Text: '{title_check['text']}'")
            
            if title_check['isEmpty']:
                print(f"  ✅ 'Messages' removed (title is empty)")
            else:
                print(f"  ❌ Title still has text: '{title_check['text']}'")
        else:
            print(f"  Element not found")
        
        # Test 3: Check background color - yellow instead of light yellow
        print("\n🎨 TEST 3: BACKGROUND COLOR (Light Yellow → Yellow)")
        color_check = page.evaluate('''() => {
            // Get CSS rule for .message.sent-by-me.unread
            const sheets = Array.from(document.styleSheets);
            let foundRule = null;
            
            for (const sheet of sheets) {
                try {
                    const rules = Array.from(sheet.cssRules || sheet.rules || []);
                    for (const rule of rules) {
                        if (rule.selectorText && rule.selectorText.includes('.message.sent-by-me.unread')) {
                            foundRule = {
                                selector: rule.selectorText,
                                background: rule.style.background || rule.style.backgroundColor
                            };
                            break;
                        }
                    }
                } catch (e) {
                    // Skip cross-origin stylesheets
                }
                if (foundRule) break;
            }
            
            return foundRule;
        }''')
        
        if color_check:
            print(f"  CSS Rule: {color_check['selector']}")
            print(f"  Background: {color_check['background']}")
            
            # Check if it's yellow (#FFFF00) not light yellow (#FFFACD)
            if '#FFFF00' in color_check['background'].upper() or 'rgb(255, 255, 0)' in color_check['background']:
                print(f"  ✅ Changed to yellow (#FFFF00)")
            elif '#FFFACD' in color_check['background'].upper():
                print(f"  ❌ Still light yellow (#FFFACD)")
            else:
                print(f"  ⚠️  Color: {color_check['background']}")
        else:
            print(f"  CSS rule not found (may need cache clear)")
        
        # Test 4: Test welcome message without "Online"
        print("\n👋 TEST 4: WELCOME MESSAGE (Remove 'Online')")
        
        # Simulate user login
        page.evaluate('''() => {
            window.currentUser = {
                id: 123,
                username: 'JohnDoe',
                role: 'user'
            };
            window.adminId = 1;
            localStorage.setItem('admin_name_for_user_123', 'Ken');
        }''')
        
        page.wait_for_timeout(500)
        
        # Test with online status
        print("\n  Testing ONLINE status:")
        msg_online = page.evaluate('''async () => {
            window.getUserStatus = async function() {
                return { status: 'online' };
            };
            
            await updateUserWelcomeMessage();
            
            const userInfo = document.getElementById('user-info');
            return userInfo ? userInfo.textContent : 'Element not found';
        }''')
        
        print(f"    Text: '{msg_online}'")
        
        if 'Online' not in msg_online and 'Welcome' in msg_online:
            print(f"    ✅ 'Online' removed (shows: '{msg_online}')")
        elif 'Online' in msg_online:
            print(f"    ❌ Still shows 'Online'")
        else:
            print(f"    ⚠️  Unexpected format")
        
        # Test with offline status
        print("\n  Testing OFFLINE status:")
        msg_offline = page.evaluate('''async () => {
            window.getUserStatus = async function() {
                return { status: 'offline' };
            };
            
            await updateUserWelcomeMessage();
            
            const userInfo = document.getElementById('user-info');
            return userInfo ? userInfo.textContent : 'Element not found';
        }''')
        
        print(f"    Text: '{msg_offline}'")
        
        if 'Offline' in msg_offline:
            print(f"    ✅ Still shows 'Offline' (correct)")
        else:
            print(f"    ❌ Should show 'Offline'")
        
        # Test with not available status
        print("\n  Testing NOT AVAILABLE status:")
        msg_busy = page.evaluate('''async () => {
            window.getUserStatus = async function() {
                return { status: 'in_call' };
            };
            
            await updateUserWelcomeMessage();
            
            const userInfo = document.getElementById('user-info');
            return userInfo ? userInfo.textContent : 'Element not found';
        }''')
        
        print(f"    Text: '{msg_busy}'")
        
        if 'Not Available' in msg_busy:
            print(f"    ✅ Still shows 'Not Available' (correct)")
        else:
            print(f"    ❌ Should show 'Not Available'")
        
        # Take screenshot
        page.screenshot(path='test_screenshots/four_changes.png', full_page=True)
        print("\n✓ Screenshot saved: four_changes.png")
        
        print("\n" + "="*80)
        print("SUMMARY:")
        print("="*80)
        
        print("\n1. CHATAPP HEADER:")
        if header_check['exists'] and header_check['display'] == 'none':
            print("   ✅ Removed (display: none)")
        else:
            print("   ❌ Still visible")
        
        print("\n2. MESSAGES TITLE:")
        if title_check['exists'] and title_check['isEmpty']:
            print("   ✅ Removed (empty string)")
        else:
            print("   ❌ Still has text")
        
        print("\n3. YELLOW COLOR:")
        if color_check and '#FFFF00' in color_check['background'].upper():
            print("   ✅ Changed from #FFFACD to #FFFF00")
        else:
            print("   ⚠️  Need to verify or clear cache")
        
        print("\n4. ONLINE WORD:")
        if msg_online and 'Online' not in msg_online:
            print("   ✅ Removed from welcome message")
            print(f"   Shows: '{msg_online}'")
        else:
            print("   ❌ Still shows 'Online'")
        
        print("\n📋 MESSAGE FORMATS:")
        print(f"   Online:        '{msg_online}'")
        print(f"   Offline:       '{msg_offline}'")
        print(f"   Not Available: '{msg_busy}'")
        
        print("\n⚠️ CRITICAL: CLEAR BROWSER CACHE (Ctrl+F5)!")
        print("\nBrowser will stay open for 30 seconds...")
        page.wait_for_timeout(30000)
        
        browser.close()

if __name__ == '__main__':
    test_four_changes()
