"""
Use Playwright to verify where the error message appears
"""
import asyncio
from playwright.async_api import async_playwright

async def test_error_message_position():
    async with async_playwright() as p:
        print("=" * 80)
        print("TESTING ERROR MESSAGE POSITION WITH PLAYWRIGHT")
        print("=" * 80)
        
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Navigate to the login page
        print("\n1. Navigating to http://localhost:5001/")
        try:
            await page.goto('http://localhost:5001/', timeout=10000)
            await page.wait_for_load_state('networkidle')
            print("   ✅ Page loaded")
        except Exception as e:
            print(f"   ❌ Failed to load: {e}")
            await browser.close()
            return
        
        # Get page title
        title = await page.title()
        print(f"\n2. Page Title: {title}")
        
        # Check which HTML file is being served by looking for unique elements
        print("\n3. Checking HTML structure...")
        
        # Check if error-message div exists
        error_div = await page.query_selector('#error-message')
        if error_div:
            print("   ✅ Found #error-message div")
            
            # Get the parent element
            parent = await error_div.evaluate('el => el.parentElement.tagName')
            parent_id = await error_div.evaluate('el => el.parentElement.id || "no-id"')
            
            print(f"   Parent element: <{parent}> (id: {parent_id})")
            
            # Get position relative to form and button
            login_form = await page.query_selector('#login-form')
            login_button = await page.query_selector('#login-form button[type="submit"]')
            
            if login_form and login_button and error_div:
                # Get bounding boxes
                error_box = await error_div.bounding_box()
                button_box = await login_button.bounding_box()
                form_box = await login_form.bounding_box()
                
                if error_box and button_box and form_box:
                    print(f"\n4. Element Positions (Y-axis):")
                    print(f"   Form top: {form_box['y']:.1f}px")
                    print(f"   Button top: {button_box['y']:.1f}px")
                    print(f"   Button bottom: {button_box['y'] + button_box['height']:.1f}px")
                    print(f"   Error div top: {error_box['y']:.1f}px")
                    
                    if error_box['y'] < button_box['y']:
                        print("\n   ❌ ERROR MESSAGE IS ABOVE THE BUTTON!")
                        print(f"   Distance: {button_box['y'] - error_box['y']:.1f}px above")
                    elif error_box['y'] > button_box['y'] + button_box['height']:
                        print("\n   ✅ ERROR MESSAGE IS BELOW THE BUTTON!")
                        print(f"   Distance: {error_box['y'] - (button_box['y'] + button_box['height']):.1f}px below")
                    else:
                        print("\n   ⚠️  ERROR MESSAGE OVERLAPS WITH BUTTON!")
        else:
            print("   ❌ #error-message div NOT FOUND")
        
        # Check the HTML structure by getting the form's innerHTML
        print("\n5. Getting actual HTML structure around login button...")
        form_html = await page.query_selector('#login-form')
        if form_html:
            inner_html = await form_html.inner_html()
            
            # Find the button and see what comes after
            button_index = inner_html.find('<button class="btn" type="submit">')
            if button_index > -1:
                # Get 500 characters after the button
                after_button = inner_html[button_index:button_index + 500]
                
                print("\n   HTML after login button:")
                print("   " + "-" * 60)
                # Show just the relevant part
                lines = after_button.split('\n')
                for line in lines[:15]:  # First 15 lines
                    print(f"   {line[:70]}")
                print("   " + "-" * 60)
        
        # Try to trigger an error and see where it appears
        print("\n6. Testing error display by submitting invalid login...")
        
        # Fill in invalid credentials
        await page.fill('#login-username', 'testuser')
        await page.fill('#login-password', 'wrongpassword')
        
        # Click login button
        await page.click('button[type="submit"]')
        
        # Wait a bit for error to appear
        await asyncio.sleep(2)
        
        # Check if error message is visible and where
        error_div = await page.query_selector('#error-message')
        if error_div:
            is_visible = await error_div.is_visible()
            if is_visible:
                error_text = await error_div.inner_text()
                error_box = await error_div.bounding_box()
                button_box = await page.query_selector('button[type="submit"]')
                button_box = await button_box.bounding_box() if button_box else None
                
                print(f"   ✅ Error message visible: '{error_text}'")
                if error_box and button_box:
                    if error_box['y'] < button_box['y']:
                        print(f"   ❌ ERROR APPEARS ABOVE BUTTON (at Y={error_box['y']:.1f})")
                    else:
                        print(f"   ✅ ERROR APPEARS BELOW BUTTON (at Y={error_box['y']:.1f})")
            else:
                print("   ⚠️  Error div exists but not visible")
        
        # Take a screenshot for visual confirmation
        await page.screenshot(path='login_page_error.png')
        print("\n7. Screenshot saved to: login_page_error.png")
        
        await browser.close()
        
        print("\n" + "=" * 80)
        print("TEST COMPLETE")
        print("=" * 80)

# Run the test
asyncio.run(test_error_message_position())
