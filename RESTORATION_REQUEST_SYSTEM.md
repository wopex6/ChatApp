# 🔐 Restoration Request System - IMPLEMENTED

**Date:** November 7, 2025  
**Status:** Backend ✅ Complete | Frontend ⏳ Pending

---

## 🎯 **Problem Solved**

Deleted users could automatically restore their accounts by re-signing up with the same username. This gave them unauthorized access without admin approval.

---

## ✅ **What Was Implemented (Backend)**

### **1. Removed Auto-Restore**
```python
# OLD (removed):
if is_deleted:
    # Auto-restore deleted user
    UPDATE users SET is_deleted = 0
    
# NEW:
if existing_user:
    # Username taken (even if deleted)
    return None
```

### **2. New Database Table: `restoration_requests`**
```sql
CREATE TABLE restoration_requests (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    message TEXT,  -- User's reason for requesting restoration
    status TEXT DEFAULT 'pending',  -- pending, approved, denied
    created_at DATETIME,
    reviewed_at DATETIME,
    reviewed_by INTEGER  -- Admin who reviewed
)
```

### **3. Backend Methods Added**
- `check_deleted_user(username)` - Check if username is deleted
- `submit_restoration_request(username, email, message)` - Submit request
- `get_restoration_requests(status=None)` - Get all requests (admin)
- `approve_restoration_request(request_id, admin_id)` - Approve & restore user
- `deny_restoration_request(request_id, admin_id)` - Deny request

### **4. API Endpoints Added**
| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/auth/request-restoration` | POST | None | Submit restoration request |
| `/api/admin/restoration-requests` | GET | Admin | View all requests |
| `/api/admin/restoration-requests/<id>/approve` | POST | Admin | Approve request |
| `/api/admin/restoration-requests/<id>/deny` | POST | Admin | Deny request |

### **5. Updated Signup Endpoint**
```javascript
// When deleted user tries to signup:
{
    "error": "account_deleted",
    "message": "This account has been deleted. Please submit a restoration request.",
    "username": "Olha"
}
// HTTP 403 Forbidden
```

---

## ⏳ **What Needs to Be Done (Frontend)**

### **1. Update Signup Error Handling**

**File:** `chatapp_frontend.html` - `signup()` function

```javascript
async function signup() {
    const response = await fetch(`${API_URL}/auth/signup`, ...);
    const data = await response.json();
    
    if (response.status === 403 && data.error === 'account_deleted') {
        // Show restoration request modal
        showRestorationRequestModal(data.username);
    } else if (!response.ok) {
        showError(data.error || 'Signup failed');
    }
}
```

### **2. Create Restoration Request Modal**

**Add HTML:**
```html
<!-- Restoration Request Modal -->
<div id="restoration-modal" class="modal">
    <div class="modal-content">
        <h2>Account Restoration Request</h2>
        <p>Your account has been deleted. Submit a request to restore it.</p>
        
        <form id="restoration-form" onsubmit="submitRestorationRequest(event)">
            <input type="text" id="restoration-username" readonly>
            <input type="email" id="restoration-email" placeholder="Email" required>
            <textarea id="restoration-message" 
                      placeholder="Why would you like to restore your account?" 
                      rows="4" required></textarea>
            <button type="submit">Submit Request</button>
            <button type="button" onclick="closeRestorationModal()">Cancel</button>
        </form>
        
        <div id="restoration-success" style="display: none;">
            <p>✅ Request submitted! An administrator will review it.</p>
        </div>
    </div>
</div>
```

**Add JavaScript:**
```javascript
function showRestorationRequestModal(username) {
    document.getElementById('restoration-username').value = username;
    document.getElementById('restoration-modal').classList.add('show');
}

function closeRestorationModal() {
    document.getElementById('restoration-modal').classList.remove('show');
    document.getElementById('restoration-form').reset();
}

async function submitRestorationRequest(event) {
    event.preventDefault();
    
    const username = document.getElementById('restoration-username').value;
    const email = document.getElementById('restoration-email').value;
    const message = document.getElementById('restoration-message').value;
    
    const response = await fetch(`${API_URL}/auth/request-restoration`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, message })
    });
    
    if (response.ok) {
        document.getElementById('restoration-form').style.display = 'none';
        document.getElementById('restoration-success').style.display = 'block';
        setTimeout(() => closeRestorationModal(), 3000);
    } else {
        const data = await response.json();
        showError(data.error);
    }
}
```

### **3. Add Admin UI for Restoration Requests**

**Add Tab in Admin Panel:**
```html
<div class="admin-tabs">
    <button class="admin-tab" onclick="showAdminTab('conversations')">💬 Conversations</button>
    <button class="admin-tab" onclick="showAdminTab('users')">👥 Users</button>
    <button class="admin-tab" onclick="showAdminTab('restoration-requests')">🔄 Restoration Requests</button>
</div>

<div id="admin-restoration-tab" style="display: none;">
    <h3>Account Restoration Requests</h3>
    
    <div style="margin-bottom: 15px;">
        <label>
            <input type="radio" name="request-filter" value="pending" checked onchange="loadRestorationRequests()">
            Pending
        </label>
        <label>
            <input type="radio" name="request-filter" value="all" onchange="loadRestorationRequests()">
            All
        </label>
    </div>
    
    <div id="restoration-requests-list"></div>
</div>
```

**Add JavaScript:**
```javascript
async function loadRestorationRequests() {
    const filter = document.querySelector('input[name="request-filter"]:checked').value;
    const status = filter === 'pending' ? 'pending' : null;
    
    const response = await fetch(
        `${API_URL}/admin/restoration-requests${status ? `?status=${status}` : ''}`,
        { headers: { 'Authorization': `Bearer ${token}` } }
    );
    
    const requests = await response.json();
    const container = document.getElementById('restoration-requests-list');
    
    if (requests.length === 0) {
        container.innerHTML = '<p>No restoration requests found.</p>';
        return;
    }
    
    container.innerHTML = requests.map(req => `
        <div class="request-item ${req.status}">
            <div class="request-info">
                <strong>${req.username}</strong>
                <span class="status-badge ${req.status}">${req.status.toUpperCase()}</span>
                <div style="margin-top: 5px;">
                    📧 ${req.email}<br>
                    📅 ${formatTimestamp(req.created_at)}<br>
                    💬 "${req.message}"
                </div>
                ${req.reviewed_by ? `
                    <div style="margin-top: 5px; font-size: 0.9em; color: #666;">
                        Reviewed by ${req.reviewed_by_name} on ${formatTimestamp(req.reviewed_at)}
                    </div>
                ` : ''}
            </div>
            ${req.status === 'pending' ? `
                <div class="request-actions">
                    <button class="btn-approve" onclick="approveRestoration(${req.id})">
                        ✅ Approve
                    </button>
                    <button class="btn-deny" onclick="denyRestoration(${req.id})">
                        ❌ Deny
                    </button>
                </div>
            ` : ''}
        </div>
    `).join('');
}

async function approveRestoration(requestId) {
    if (!confirm('Approve this restoration request and restore the user account?')) return;
    
    const response = await fetch(
        `${API_URL}/admin/restoration-requests/${requestId}/approve`,
        {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        }
    );
    
    if (response.ok) {
        showSuccess('Account restored successfully!');
        loadRestorationRequests();
        loadAllUsers();  // Refresh user list
    } else {
        const data = await response.json();
        showError(data.error);
    }
}

async function denyRestoration(requestId) {
    if (!confirm('Deny this restoration request?')) return;
    
    const response = await fetch(
        `${API_URL}/admin/restoration-requests/${requestId}/deny`,
        {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        }
    );
    
    if (response.ok) {
        showSuccess('Request denied');
        loadRestorationRequests();
    } else {
        const data = await response.json();
        showError(data.error);
    }
}
```

**Add CSS:**
```css
.request-item {
    padding: 15px;
    border: 1px solid #ddd;
    border-radius: 8px;
    margin-bottom: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.request-item.pending {
    background: #fffef0;
    border-color: #ffc107;
}

.request-item.approved {
    background: #f0fff4;
    border-color: #4caf50;
}

.request-item.denied {
    background: #fff0f0;
    border-color: #f44336;
}

.status-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 0.85em;
    font-weight: 600;
    margin-left: 10px;
}

.status-badge.pending {
    background: #ffc107;
    color: #000;
}

.status-badge.approved {
    background: #4caf50;
    color: #fff;
}

.status-badge.denied {
    background: #f44336;
    color: #fff;
}

.request-actions {
    display: flex;
    gap: 8px;
}

.btn-approve {
    background: #4caf50;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
}

.btn-deny {
    background: #f44336;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
}
```

---

## 🔄 **User Flow**

### **Deleted User Tries to Signup:**
```
1. User enters "Olha" + password
   ↓
2. Signup fails with 403 error
   ↓
3. Modal appears: "Account deleted - request restoration"
   ↓
4. User enters email + reason
   ↓
5. Request submitted to database
   ↓
6. Confirmation: "Admin will review your request"
```

### **Admin Reviews Request:**
```
1. Admin logs in
   ↓
2. Goes to "🔄 Restoration Requests" tab
   ↓
3. Sees list of pending requests
   ↓
4. Reviews Olha's request + reason
   ↓
5. Clicks "✅ Approve" or "❌ Deny"
   ↓
6. If approved: User account restored (is_deleted = 0)
   ↓
7. Olha can now login with old password
```

---

## 📊 **Database State Examples**

### **Before Request:**
```sql
-- users table
| id | username | is_deleted |
|----|----------|------------|
| 2  | Olha     | 1          |

-- restoration_requests table
(empty)
```

### **After Request Submitted:**
```sql
-- restoration_requests table
| id | username | email          | message            | status  |
|----|----------|----------------|-----------------------|---------|
| 1  | Olha     | olha@me.com    | "Please restore..."   | pending |
```

### **After Admin Approves:**
```sql
-- users table
| id | username | is_deleted |
|----|----------|------------|
| 2  | Olha     | 0          |  ← Restored!

-- restoration_requests table
| id | username | status   | reviewed_by | reviewed_at         |
|----|----------|----------|-------------|---------------------|
| 1  | Olha     | approved | 1           | 2025-11-07 10:51:00 |
```

---

## ✅ **Benefits**

1. **Admin Control** - Only admin can restore accounts
2. **Audit Trail** - All requests logged with reason
3. **Transparency** - User knows request is being reviewed
4. **Security** - Prevents unauthorized re-signup
5. **Communication** - User can explain why they want restoration

---

## 🚀 **What's Live Now**

✅ Backend fully deployed to Railway  
✅ API endpoints ready and working  
✅ Database table created  
✅ Signup blocks deleted users  

⏳ **Next:** Update frontend HTML/JS/CSS to add UI

---

## 📝 **Summary**

**Backend is complete and deployed!** The system is working but users don't have the UI to submit requests yet. Admin can restore users manually via the existing "Restore" button in the user list, OR we can add the frontend UI to let users submit formal requests with reasons.

The restoration request system gives you:
- **Control:** Admin approval required
- **Transparency:** Users can request restoration
- **Logging:** All requests tracked with messages
- **Flexibility:** Admin can approve/deny with context
