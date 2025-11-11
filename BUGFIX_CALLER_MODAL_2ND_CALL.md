# 🔧 Critical Fix: Caller Modal Not Showing on 2nd+ Calls

**Date:** November 11, 2025 - 14:59  
**Issue:** PC user's "Calling..." modal doesn't appear on 2nd+ calls (but call connects)

---

## 🐛 The REAL Problem (Correctly Identified)

I was fixing the **wrong modal**! 🤦

- ✅ **Phone admin (receiver) incoming modal** - Works fine
- ❌ **PC user (caller) active call modal** - Doesn't show on 2nd+ calls

---

## 🔍 Root Cause

### **Same Issue, Different Modal**

When a call ends, `hangupCall()` sets:
```javascript
activeModal.style.cssText = 'display: none !important;';
```

On the 2nd call, `callUser()` or `showCallingUI()` does:
```javascript
document.getElementById('active-call-modal').classList.add('show');
```

**Problem:** The `display: none !important` inline style from the previous call **overrides** the `.show` class CSS!

**Result:** Modal is in DOM, has `.show` class, but inline style prevents it from displaying.

---

## 💡 Solution

### **Remove Inline Styles Before Showing Modal**

Added `removeAttribute('style')` before adding `.show` class in TWO locations:

### **1. Admin Calling User (`callUser` function):**

```javascript
// Show calling UI
const activeModal = document.getElementById('active-call-modal');
activeModal.removeAttribute('style'); // Remove display: none !important
activeModal.classList.add('show');
```

### **2. User Calling Admin (`showCallingUI` function):**

```javascript
function showCallingUI() {
    // ...set caller name and status...
    
    // CRITICAL: Remove inline styles from previous call before showing
    const activeModal = document.getElementById('active-call-modal');
    activeModal.removeAttribute('style'); // Remove display: none !important
    activeModal.classList.add('show');
}
```

---

## 🧪 Testing

### **Test: PC User Calls Admin (2nd+ Time)**

**Steps:**
1. PC user clicks "📞 Call" button
2. Admin answers → Talk → Hangup
3. **PC user clicks "📞 Call" button AGAIN**
4. **Expected:** PC user sees "Calling..." modal ✅

**Before Fix:**
- 1st call: Modal appears ✅
- 2nd call: Modal doesn't appear ❌ (but call still connects)

**After Fix:**
- 1st call: Modal appears ✅
- 2nd call: Modal appears ✅
- 3rd+ calls: Modal appears ✅

---

## 📊 Technical Details

### **Files Modified:**
- `chatapp_login_only.html`

### **Functions Modified:**

1. **`callUser()`** (Admin calling user) - Line ~3257
   - Added `activeModal.removeAttribute('style')` before showing

2. **`showCallingUI()`** (User calling admin) - Line ~4572
   - Added `activeModal.removeAttribute('style')` before showing

### **Lines Changed:**
- ~6 lines added across 2 functions

---

## ✅ Expected Behavior

### **Caller Modal Appearance:**

| Call # | Modal Shows? | Before | After |
|--------|-------------|--------|-------|
| 1st | Yes | ✅ | ✅ |
| 2nd | Yes | ❌ **BROKEN** | ✅ **FIXED** |
| 3rd+ | Yes | ❌ | ✅ **FIXED** |

---

## 🎯 Why This Fix Works

**Before:**
```javascript
// After 1st call hangup:
modal.style = "display: none !important"  // Set by hangupCall()

// On 2nd call:
modal.classList.add('show')  // Tries to show
// But inline style wins! Modal stays hidden ❌
```

**After:**
```javascript
// After 1st call hangup:
modal.style = "display: none !important"  // Set by hangupCall()

// On 2nd call:
modal.removeAttribute('style')  // ← Remove inline styles first!
modal.classList.add('show')     // Now .show CSS works ✅
```

---

## 💡 Lesson Learned

**Inline styles (`style=""`) always override CSS classes!**

When hiding modals with `style.cssText = 'display: none !important'`, you MUST remove these inline styles before trying to show the modal again with just a CSS class.

**Better approach for future:**
- Hide: `modal.classList.remove('show')`
- Show: `modal.classList.add('show')`
- Don't use `style.cssText` unless absolutely necessary

---

## 📝 Commit Message
```
Fix caller modal not showing on 2nd+ calls

- Remove inline styles from active-call-modal before showing
- Fix callUser() to clear previous display: none !important
- Fix showCallingUI() to clear previous display: none !important  
- Ensure modal appears on all subsequent calls (2nd, 3rd, etc.)
```

---

**Fixed:** November 11, 2025 at 14:59  
**Root Cause:** `display: none !important` inline style from previous call  
**Solution:** Remove inline styles with `removeAttribute('style')` before showing  
**Applies To:** Both admin→user and user→admin call scenarios
