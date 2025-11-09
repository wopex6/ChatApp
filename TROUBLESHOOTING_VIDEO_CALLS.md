# 🔧 Troubleshooting Video Calls

**Date:** November 8, 2025  
**Purpose:** Debug and fix video call issues

---

## 🐛 **Current Issues**

### **Issue 1: PC (User) - No Camera Permission Request**
- Voice works ✅
- Video button doesn't trigger camera permission ❌
- Can't send video to iPhone ❌

### **Issue 2: PC (Admin) - No Incoming Call Modal**
- When iPhone (user) calls → no popup ❌
- When iPhone (admin) calls → no popup ❌
- Calls timeout without being answered ❌

---

## 📋 **How to Test & Get Debug Logs**

### **IMPORTANT: Open Browser Console First!**

**On PC (Chrome/Edge):**
1. Press `F12` or `Ctrl+Shift+I`
2. Click "Console" tab
3. Keep it open during testing

**On iPhone (Safari):**
1. Settings → Safari → Advanced → Enable "Web Inspector"
2. On Mac: Safari → Develop → [Your iPhone] → [Page]
3. See console logs from iPhone

---

## 🧪 **Test Scenario 1: PC User Not Getting Camera**

### **Steps:**
1. **PC:** Login as regular user (e.g., Olha)
2. **iPhone:** Login as Ken Tse (admin)
3. **PC:** Click 📞 to call admin
4. **iPhone:** Answer the call
5. **Both:** Verify audio works
6. **PC:** Click 📹 Video button

### **Expected Console Logs on PC:**
```
📹 Toggle video clicked
Current video track: undefined
🎥 Requesting camera permission...
```

### **Then you should see:**
- Browser popup asking for camera permission
- Green notification: "Click 'Allow' to enable your camera"

### **What to Check:**
- ❓ Does browser ask for camera permission?
- ❓ If you click "Allow", what happens?
- ❓ Any error messages in console?

### **Expected After Clicking "Allow":**
```
✅ Camera permission granted
✅ Video enabled
```

### **If It Fails:**
**Copy ALL console logs** and share them!

Look for errors like:
- `NotAllowedError` → Camera permission denied
- `NotFoundError` → No camera detected
- `NotReadableError` → Camera in use by another app

---

## 🧪 **Test Scenario 2: Admin Not Seeing Incoming Call Modal**

### **Steps:**
1. **PC:** Login as Ken Tse (admin)
2. **iPhone:** Login as regular user
3. **Check PC Console** - should see:
   ```
   ✅ Signal polling started for incoming calls
   ```
4. **iPhone:** Click 📞 to call admin
5. **Watch PC Console** closely!

### **Expected Console Logs on PC:**
```
📡 Received 1 signal(s)
Processing signal from user: 2
📨 Received signal: offer
📞 Incoming call from user: 2
Current user role: administrator
Offer details: {call_id: "...", sdp: "...", type: "offer"}
Modal element: <div id="incoming-call-modal">
Name element: <div id="incoming-caller-name">
✅ Incoming call modal shown
```

### **What to Check:**

#### **If NO logs appear:**
Signal polling NOT running! Check:
- Is `✅ Signal polling started` shown after login?
- Any errors in console?

#### **If you see "📡 Received signal" but NO modal:**
Modal element issue! Check:
- Does `Modal element:` show `null` or an actual element?
- Does `Name element:` show `null` or an actual element?
- Look for `❌ Modal element not found!` error

#### **If modal appears but can't click:**
CSS/z-index issue - modal hidden behind something

---

## 🧪 **Test Scenario 3: Video Reminder Notification**

### **Steps:**
1. Start any call (audio only)
2. Wait for call to connect
3. **3 seconds later**, you should see:
   ```
   💡 Tip: Click 📹 to enable video!
   ```

This reminds you that video is available!

---

## 📊 **Key Logs to Look For**

### **On Login:**
```
✅ Signal polling started for incoming calls
```
**If missing:** Signal polling NOT started → won't receive calls!

### **When Receiving Call:**
```
📡 Received 1 signal(s)
Processing signal from user: X
📨 Received signal: offer
📞 Incoming call from user: X
✅ Incoming call modal shown
```
**If missing:** Not receiving signals from server

### **When Clicking Video Button:**
```
📹 Toggle video clicked
Current video track: undefined
🎥 Requesting camera permission...
✅ Camera permission granted
```
**If stuck at "Requesting":** Browser blocked camera or user denied

### **When Call Connects:**
```
Connection state: connected
✅ Call connected
⏰ Call timeout cleared - connected
```
**If "timeout cleared" missing:** May get false timeout

---

## 🔍 **What Information to Provide**

If issues persist, please provide:

### **1. Which scenario failed?**
- [ ] PC user can't enable video
- [ ] PC admin doesn't see incoming call modal
- [ ] Both issues

### **2. Console logs:**
Copy and paste **ALL** console output from:
- Login time
- Through the failed call attempt
- Any errors (red text)

### **3. Screenshots:**
- PC screen during issue
- iPhone screen during issue
- Browser console with errors

### **4. Browser details:**
- PC browser: Chrome / Edge / Firefox / Safari
- PC browser version
- iPhone iOS version
- iPhone Safari version

### **5. Specific observations:**
- Does browser ask for camera permission? (Yes/No)
- Does modal element exist in logs? (null / actual element)
- Does signal polling start message appear? (Yes/No)

---

## ✅ **Quick Checklist**

Before testing:

- [ ] Refresh both pages (Ctrl+F5 on PC)
- [ ] Open browser console (F12)
- [ ] Logout and login again
- [ ] Check for "Signal polling started" message
- [ ] Try from clean browser tab / incognito mode

---

## 🎯 **Expected Working Behavior**

### **Camera Permission (PC User):**
1. Call connects with audio
2. Click 📹 button
3. Browser asks: "Allow camera access?"
4. Click "Allow"
5. Your video appears in small corner
6. Other person sees your video

### **Incoming Call Modal (PC Admin):**
1. Login as admin
2. See "Signal polling started" in console
3. Someone calls you
4. Modal pops up: "User X is calling..."
5. Answer / Reject buttons work
6. Click Answer → call connects

---

## 🔧 **Common Fixes**

### **If camera permission not asked:**
1. Check browser settings: `chrome://settings/content/camera`
2. Make sure site isn't blocked
3. Try different browser
4. Check camera not in use by another app

### **If modal doesn't appear:**
1. Check console for "Signal polling started"
2. If missing → logout/login again
3. Check for JavaScript errors
4. Try incognito mode
5. Clear browser cache

### **If calls timeout immediately:**
1. Check both users' console logs
2. Look for "offer" signal received
3. Verify WebRTC connection state logs
4. Check network/firewall settings

---

## 📝 **Next Steps**

1. **Wait 2-3 minutes** for Railway to deploy latest changes
2. **Clear browser cache** (Ctrl+Shift+Delete)
3. **Open console** on both PC and iPhone
4. **Test** all scenarios above
5. **Copy console logs** from failed scenarios
6. **Report** findings with logs, screenshots, and details

---

**The extensive logging will help us pinpoint exactly where the issue occurs!** 🎯
