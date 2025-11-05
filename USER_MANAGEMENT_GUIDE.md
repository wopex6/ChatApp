# 🔐 User Management & Password Change Features

**Added:** Change password and user management capabilities from the original app!

---

## ✨ Features Added

### 1. **Change Password** (All Users)
- Click "⚙️ Settings" button in chat
- Enter current password
- Enter new password (min 6 characters)
- Confirm new password
- Password validation and error handling

### 2. **User Management** (Ken Tse/Admin Only)
- New "👥 Users" tab in admin panel
- View all users with their roles
- Soft delete users (can be restored)
- Restore deleted users
- Permanently delete users (cannot be undone)
- Filter: Active users or Include deleted

---

## 🎯 How to Use

### For All Users: Change Password

1. **Login** to ChatApp
2. **Click "⚙️ Settings"** button (top right)
3. **Enter Current Password**
4. **Enter New Password** (minimum 6 characters)
5. **Confirm New Password**
6. **Click "Change Password"**

**Validations:**
- All fields required
- New passwords must match
- Current password must be correct
- New password minimum 6 characters

---

### For Ken Tse: User Management

#### View All Users

1. **Login** as Ken Tse
2. **Click "👥 Users" tab** in admin panel
3. **See all active users** by default
4. **Click "Include Deleted"** to see deleted users too

#### Soft Delete User

1. Go to Users tab
2. Find the user to delete
3. **Click "Delete" button** next to their name
4. **Confirm** the deletion
5. User is marked as deleted (can log back in yet)

**What happens:**
- User is soft-deleted (is_deleted = 1)
- User cannot login anymore
- All messages preserved
- Can be restored later

#### Restore Deleted User

1. **Click "Include Deleted"** to show deleted users
2. Find the deleted user (shown with strikethrough)
3. **Click "Restore" button**
4. User can login again immediately

#### Permanent Delete User

1. **Delete the user first** (soft delete)
2. **Click "Include Deleted"**
3. Find the deleted user
4. **Click "Delete Forever" button**
5. **Confirm** permanent deletion

**⚠️ WARNING:**
- This CANNOT be undone!
- Deletes user account permanently
- Deletes all their messages
- Deletes their profile
- Everything is gone forever

**Protection:**
- Cannot delete your own account
- Requires confirmation
- Only works on already soft-deleted users

---

## 🔧 Technical Implementation

### Backend Endpoints

#### Password Change
```
POST /api/auth/change-password
Headers: Authorization: Bearer <token>
Body: {
  "currentPassword": "old_pass",
  "newPassword": "new_pass"
}
```

#### User Management (Admin Only)
```
GET  /api/admin/users?include_deleted=true
POST /api/admin/users/:id/delete
POST /api/admin/users/:id/restore
POST /api/admin/users/:id/permanent-delete
POST /api/admin/users/:id/role
POST /api/admin/users/bulk-delete-deleted
```

### Database Methods (`chatapp_database.py`)

**Password:**
- `update_user_password(user_id, new_password)` - Hash and update
- `get_user_role(user_id)` - Get user's role

**User Management:**
- `soft_delete_user(user_id)` - Mark as deleted
- `restore_user(user_id)` - Unmark deleted
- `permanent_delete_user(user_id)` - DELETE from DB
- `bulk_delete_deleted_users()` - Delete all soft-deleted
- `update_user_role(user_id, role)` - Change role

### Frontend Components

**Settings Modal:**
- Change password form
- Validation UI
- Success/error messages

**Admin User Management:**
- Two tabs: Conversations & Users
- User list with action buttons
- Confirmation modal for destructive actions
- Real-time updates after actions

---

## 🎨 UI Elements

### Settings Button
- Located top-right corner (next to Logout)
- "⚙️ Settings" button
- Opens modal overlay

### Settings Modal
- Clean white modal
- Password input fields
- Change Password button
- Cancel button

### Admin Users Tab
- "Active Users" button (default)
- "Include Deleted" button
- User cards with info:
  - Username
  - Email
  - Role
  - Action buttons

### User Action Buttons

**Active User:**
- 🔴 **Delete** - Soft delete

**Deleted User (strikethrough):**
- 🟢 **Restore** - Bring back
- 🔴 **Delete Forever** - Permanent delete

### Confirmation Modal
- Title and message
- Confirm button (red for delete)
- Cancel button

---

## 🔒 Security Features

✅ **Current Password Required** - Must verify before changing  
✅ **JWT Authentication** - All endpoints require valid token  
✅ **Admin-Only Actions** - User management locked to administrators  
✅ **Self-Protection** - Cannot delete/modify your own account  
✅ **Confirmation Required** - Destructive actions ask for confirmation  
✅ **Password Hashing** - bcrypt with salt  
✅ **Soft Delete First** - Must soft-delete before permanent delete

---

## 📊 Database Schema Impact

### `users` Table
```sql
is_deleted INTEGER DEFAULT 0  -- Soft delete flag
user_role TEXT                -- Role (guest, user, paid, administrator)
password_hash TEXT            -- bcrypt hashed password
```

### Cascade Behavior
When permanently deleting user:
1. Delete from `admin_messages` (all messages)
2. Delete from `user_profiles` (profile data)
3. Delete from `users` (account)

---

## 🐛 Error Handling

### Password Change Errors
- "Please fill all password fields"
- "New passwords do not match"
- "New password must be at least 6 characters"
- "Current password is incorrect"
- "Failed to change password"

### User Management Errors
- "Admin access required" (403)
- "Cannot delete your own account" (400)
- "User not found" (404)
- "Failed to delete user" (500)

---

## 🧪 Testing Guide

### Test Password Change

1. **Login as any user**
2. Click Settings
3. **Try wrong current password** → Should show error
4. **Try mismatched new passwords** → Should show error
5. **Try password < 6 chars** → Should show error
6. **Use correct values** → Should succeed

### Test Soft Delete

1. **Login as Ken Tse**
2. Go to Users tab
3. Delete a test user
4. **Try logging in as that user** → Should fail
5. Restore the user
6. **Try logging in again** → Should work

### Test Permanent Delete

1. Soft delete a user
2. Click "Include Deleted"
3. Click "Delete Forever"
4. Confirm deletion
5. Check database → User should be gone

---

## 💡 Best Practices

### For Ken Tse:

1. **Soft delete first** - Always use soft delete initially
2. **Wait before permanent** - Give grace period
3. **Backup messages** - Export important conversations first
4. **Verify user** - Make sure deleting correct account
5. **Cannot undo** - Permanent delete is final!

### For All Users:

1. **Strong passwords** - Use 8+ characters with mix
2. **Regular changes** - Update password periodically
3. **Unique password** - Don't reuse passwords
4. **Remember it** - Need current password to change

---

## 📝 API Response Examples

### Change Password Success
```json
{
  "success": true,
  "message": "Password updated successfully"
}
```

### Delete User Success
```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

### Error Response
```json
{
  "error": "Current password is incorrect"
}
```

---

## 🚀 Quick Actions

### Change Ken Tse's Password

1. Login as: `Ken Tse`
2. Password: `KenTse2025!`
3. Click Settings
4. Change to secure password
5. ✅ Done!

### Test User Management

1. Create test user via Signup
2. Login as Ken Tse
3. Go to Users tab
4. Test delete/restore
5. Test permanent delete

---

## ✅ Summary

**Change Password:**
✅ All users can change password  
✅ Requires current password verification  
✅ Validation and error handling  
✅ Success confirmation  

**User Management (Admin):**
✅ View all users with roles  
✅ Soft delete users  
✅ Restore deleted users  
✅ Permanent delete (after soft delete)  
✅ Cannot delete self  
✅ Confirmation modals  
✅ Real-time updates  

**Everything copied from original app.py and working!** 🎉
