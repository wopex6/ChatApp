# ✅ ChatApp Manual Testing Checklist

**Complete testing guide for all ChatApp features**

---

## 🧪 Test Environment Setup

### Prerequisites:
- ✅ Server running: `python chatapp_simple.py`
- ✅ Server accessible at: http://localhost:5001
- ✅ Two browser windows (or private/incognito for second user)
- ✅ Admin credentials: Username: `Ken Tse`, Password: `KenTse2025!`

---

## 📋 TEST 1: User Signup & Login

### Signup Flow:
1. Open http://localhost:5001
2. Click **"Sign Up"** tab
3. Enter:
   - Username: `testuser_manual` (or any unique name)
   - Email: `testuser_manual@test.com`
   - Password: `TestPass123!`
4. Click **"Sign Up"** button

**✅ Expected:**
- Success message appears
- Auto-logs in
- Chat interface loads
- See "Chat with Ken Tse" header

**❌ If fails:**
- Check error message
- Try different username (may already exist)

### Login Flow:
1. After signup, click **"Logout"**
2. Click **"Login"** tab (should be default)
3. Enter credentials
4. Click **"Login"** button

**✅ Expected:**
- Chat interface loads
- Messages (if any) displayed

---

## 📋 TEST 2: Admin Login

### Admin Access:
1. Open http://localhost:5001 in second browser/window
2. Login tab (default)
3. Enter:
   - Username: `Ken Tse`
   - Password: `KenTse2025!`
4. Click **"Login"**

**✅ Expected:**
- Admin dashboard loads
- See "Admin Dashboard" header
- See "💬 Conversations" and "👥 Users" tabs
- See user list on left side
- Message input HIDDEN until user selected

**❌ If fails:**
- Verify admin account exists in database
- Check password is correct

---

## 📋 TEST 3: User → Admin Messaging

### User Sends Message:
**In User Browser:**
1. Type message: "Test message 1"
2. Click **"Send"**

**✅ Expected:**
- Message appears immediately in user's chat
- Message shows "You" as sender
- Timestamp displayed

**In Admin Browser:**
1. Wait **5 seconds** (auto-refresh)
2. Look for new user in conversation list

**✅ Expected:**
- User appears in list (or unread count increases)
- Click user to open conversation
- Message "Test message 1" visible

---

## 📋 TEST 4: Admin → User Messaging

### Admin Sends Reply:
**In Admin Browser:**
1. Select user from list
2. Message input appears
3. Type: "Admin reply test"
4. Click **"Send"**

**✅ Expected:**
- Message appears in admin's view immediately
- Shows "You" as sender

**In User Browser:**
1. Wait **5 seconds** (auto-refresh)

**✅ Expected:**
- Message "Admin reply test" appears automatically
- Shows "Ken Tse" as sender
- NO manual refresh needed

---

## 📋 TEST 5: Auto-Refresh Testing

### Test User Auto-Refresh:
1. **Admin sends** message
2. **User waits** (don't refresh)
3. **Count seconds** until message appears

**✅ Expected:**
- Message appears within **5 seconds**
- Console log shows: `[Auto-Refresh] Loaded X messages`

### Test Admin Auto-Refresh:
1. **User sends** message
2. **Admin waits** (don't refresh, stay on that user)
3. **Count seconds** until message appears

**✅ Expected:**
- Message appears within **5 seconds**
- Console log shows: `[Admin] Auto-refreshing messages for user X`

---

## 📋 TEST 6: File Upload - Image

### Upload Image:
**In User Browser:**
1. Click **📎 attachment button**
2. Select an image file (jpg, png, gif)
3. See preview appear below input
4. Type optional message: "Image test"
5. Click **"Send"**

**✅ Expected:**
- File preview shows filename and size
- After send, image appears inline in chat
- Download icon (📥) visible next to image
- Image clickable to open full size

**In Admin Browser:**
1. Wait 5 seconds

**✅ Expected:**
- Image appears in admin's view
- Image displays inline
- Download icon present

---

## 📋 TEST 7: File Upload - Video

### Upload Video:
**In Either Browser:**
1. Click 📎
2. Select video file (.mp4, .webm)
3. Send message

**✅ Expected:**
- Video player appears inline
- Has play/pause controls
- Download icon (📥) present
- Can play video in chat

---

## 📋 TEST 8: File Upload - Document

### Upload PDF/Document:
**In Either Browser:**
1. Click 📎
2. Select document (.pdf, .docx, .txt)
3. Send message

**✅ Expected:**
- Shows file icon and name
- "📥 filename • Click to download" text
- Clicking downloads file
- Original filename preserved

---

## 📋 TEST 9: File Download

### Test Downloads:
1. Find message with attachment
2. Click download icon (📥) or link
3. File should download

**✅ Expected:**
- File downloads with original name
- File opens correctly
- Works for all file types

---

## 📋 TEST 10: Change Password

### Password Change:
**In User Browser:**
1. Click **"⚙️ Settings"** button
2. Settings modal opens
3. Enter:
   - Current Password: (your password)
   - New Password: `NewPass456!`
   - Confirm New Password: `NewPass456!`
4. Click **"Change Password"**

**✅ Expected:**
- Success message appears
- Modal closes
- Logout
- Login with new password works
- Login with old password FAILS

---

## 📋 TEST 11: User Management (Admin Only)

### View All Users:
**In Admin Browser:**
1. Click **"👥 Users"** tab
2. See list of all users

**✅ Expected:**
- All registered users listed
- Shows username, email, role
- Action buttons visible (except on own account)

### Soft Delete User:
1. Find test user (NOT yourself)
2. Click **"Delete"** button
3. Confirm deletion

**✅ Expected:**
- Confirmation modal appears
- After confirm, user marked deleted
- User shown with strikethrough

### Restore User:
1. Click **"Include Deleted"** button
2. Find deleted user
3. Click **"Restore"** button

**✅ Expected:**
- User restored immediately
- Strikethrough removed
- User can login again

### Permanent Delete:
1. Soft delete a user first
2. Click **"Include Deleted"**
3. Click **"Delete Forever"** button
4. Read warning carefully
5. Confirm

**✅ Expected:**
- Strong warning shown
- After confirm, user completely removed
- Cannot be undone
- User disappears from list

---

## 📋 TEST 12: Unread Count

### Test Unread Indicators:
**In Admin Browser:**
1. Look at user list
2. Note unread counts (red badges)

**In User Browser:**
1. Send new message

**In Admin Browser:**
1. Wait 10 seconds (user list refreshes)

**✅ Expected:**
- Unread count increases
- Badge shows correct number
- Clicking user opens messages
- After viewing, count updates

---

## 📋 TEST 13: Message Width

### Test Message Bubbles:
**In Either Browser:**
1. Send short message: "Hi"
2. Send long message: "This is a very long message to test if the message bubble properly expands to fit the content but doesn't exceed the maximum width of 70% of the container."

**✅ Expected:**
- Short message has small bubble (fits content)
- Long message expands but max 70% width
- Messages don't overlap
- Proper spacing between messages
- Left/right alignment correct

---

## 📋 TEST 14: Logout

### Test Logout:
**In Both Browsers:**
1. Click **"Logout"** button

**✅ Expected:**
- Redirected to login page
- Chat interface hidden
- Login form visible
- No errors in console

---

## 📋 TEST 15: Multiple Sessions

### Concurrent Users:
1. Open 3+ browser windows
2. Login different users in each
3. Have admin in one window
4. Send messages between all

**✅ Expected:**
- All messages delivered
- Auto-refresh works for all
- No conflicts
- Performance stays good

---

## 📊 Test Results Template

Copy and fill out after testing:

```
TEST RESULTS - Date: ___________

✅ / ❌  Test 1: User Signup & Login
✅ / ❌  Test 2: Admin Login
✅ / ❌  Test 3: User → Admin Messaging
✅ / ❌  Test 4: Admin → User Messaging
✅ / ❌  Test 5: Auto-Refresh (both ways)
✅ / ❌  Test 6: File Upload - Image
✅ / ❌  Test 7: File Upload - Video
✅ / ❌  Test 8: File Upload - Document
✅ / ❌  Test 9: File Downloads
✅ / ❌  Test 10: Change Password
✅ / ❌  Test 11: User Management
✅ / ❌  Test 12: Unread Counts
✅ / ❌  Test 13: Message Width
✅ / ❌  Test 14: Logout
✅ / ❌  Test 15: Multiple Sessions

TOTAL PASSED: __ / 15

ISSUES FOUND:
-
-
-

NOTES:
-
-
```

---

## 🐛 Troubleshooting

### Login Fails:
- Check server is running
- Check console for errors
- Verify credentials
- Try different browser

### Auto-Refresh Not Working:
- Open browser console (F12)
- Look for `[Auto-Refresh]` or `[Admin]` log messages
- Should see messages every 5 seconds
- If not, refresh page and try again

### Files Not Uploading:
- Check file size (< 50MB)
- Check file type is allowed
- Check uploads/ folder exists
- Check console for errors

### Performance Issues:
- Close other applications
- Clear browser cache
- Restart server
- Check database size

---

## ✅ Quick 5-Minute Smoke Test

If time is limited, test these critical features:

1. **Login** (user + admin) - 1 min
2. **Send message** (both directions) - 1 min
3. **Auto-refresh** (wait and verify) - 2 min
4. **Upload file** (any type) - 1 min

If all 4 pass, core functionality is working!

---

## 📝 Notes

- Browser console logs are helpful for debugging
- Test in Chrome/Edge for best compatibility
- Clear cookies if having login issues
- Database is `integrated_users.db`
- Test files created in `uploads/` folder

**Happy Testing!** 🎉
