"""
Dump the actual HTML being served to see what's really happening
"""
import requests

print("=" * 80)
print("FETCHING HTML FROM http://localhost:5001/")
print("=" * 80)

try:
    response = requests.get('http://localhost:5001/')
    html = response.text
    
    # Find the login form section
    form_start = html.find('<form id="login-form"')
    if form_start == -1:
        print("❌ Login form not found!")
    else:
        # Get 1500 characters starting from the form
        form_section = html[form_start:form_start + 1500]
        
        print("\nHTML AROUND LOGIN FORM:")
        print("=" * 80)
        
        lines = form_section.split('\n')
        for i, line in enumerate(lines[:40], 1):
            # Highlight the key lines
            if 'error-message' in line.lower():
                print(f"{i:3} >>> {line}")
            elif 'button' in line.lower() and 'submit' in line.lower():
                print(f"{i:3} ### {line}")
            else:
                print(f"{i:3}     {line}")
        
        print("=" * 80)
        
        # Check for error-message divs BEFORE the form
        before_form = html[:form_start]
        if 'id="error-message"' in before_form:
            print("\n⚠️  FOUND error-message DIV BEFORE THE FORM!")
            # Find it
            error_pos = before_form.rfind('id="error-message"')
            context_start = max(0, error_pos - 200)
            context = before_form[context_start:error_pos + 200]
            print("\nContext:")
            print(context)
        else:
            print("\n✅ No error-message div before the form")
        
        # Count total error-message divs
        error_count = html.count('id="error-message"')
        print(f"\nTotal divs with id='error-message': {error_count}")
        
        if error_count > 1:
            print("❌ PROBLEM: Multiple divs with same ID!")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nMake sure the server is running: python chatapp_simple.py")
