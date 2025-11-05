# 📞 Admin (Ken Tse) - Voice Call Guide

## ✅ **Complete Features for Ken Tse**

---

## 🎯 **3 Main Features:**

### **1. 📞 Make Calls to Users**

**Location:** Left sidebar in User Conversations

```
┌─────────────────────────────┐
│ 💬 Conversations            │
├─────────────────────────────┤
│ john_doe                📞  │ ← Click phone icon
│ jane_smith              📞  │
│ bob_jones               📞  │
└─────────────────────────────┘
```

**How it works:**
- Each user in the list has a **📞 button** next to their name
- Click the button to call that user
- If user is **offline**, you'll see: "User is offline"
- If user is **online**, call will connect automatically

---

### **2. 📥 Pick Up Incoming Calls**

**When a user calls you:**

```
┌──────────────────────────────┐
│         📞                   │  ← Pulsing animation
│     john_doe is calling...   │
│     Ringing...               │
│                              │
│   [📞 Answer]  [✖ Reject]   │  ← Choose action
└──────────────────────────────┘
```

**Automatic popup appears:**
- Shows who is calling
- **Answer button** (📞) - Accept the call
- **Reject button** (✖) - Decline the call
- If you're already in a call, incoming call is **automatically rejected** and logged as missed

---

### **3. 🔔 See Call Records (Missed Calls)**

**Location:** Top right corner

```
┌────────────────────────────────────────────┐
│ Admin Dashboard                            │
│         [🔔 Missed Calls (3)]  [⚙️] [Logout] │ ← Click here
└────────────────────────────────────────────┘
```

**Click "🔔 Missed Calls" to see:**

```
┌─────────────────────────────────────┐
│         Missed Calls                │
├─────────────────────────────────────┤
│ john_doe                        ✓   │
│ 2:45 PM                             │
│                                     │
│ jane_smith                      ✓   │
│ 1:30 PM                             │
│                                     │
│ bob_jones                       ✓   │
│ 10:15 AM                            │
└─────────────────────────────────────┘
```

**Features:**
- See who called
- See what time they called
- **Badge shows count:** 🔔 Missed Calls **(3)**
- Click **✓** to mark individual call as seen
- Click **"Mark All Seen"** to clear all
- Orange background = new/unseen call
- Gray background = already seen

---

## 🎮 **Call Controls During Active Call**

```
┌────────────────────────┐
│       📞               │
│    john_doe            │
│    Connected           │
│    02:34               │ ← Timer shows duration
│                        │
│   [🔇]      [📞]       │ ← Mute / Hang up
└────────────────────────┘
```

**Controls:**
- **🔇 Mute** - Toggle your microphone on/off
- **📞 Hang Up** - End the call
- **Timer** - Shows call duration in real-time

---

## 📊 **Call Scenarios**

### **Scenario A: You Call User (Success)**
1. Click 📞 button next to user name
2. Browser asks for microphone permission ✅ Allow
3. Modal shows "Calling..."
4. User answers
5. "Connected" - you can talk!
6. Timer starts counting

### **Scenario B: You Call User (Offline)**
1. Click 📞 button next to user name
2. Message appears: "User is offline"
3. No call is logged (user wasn't available)

### **Scenario C: User Calls You (You Answer)**
1. Popup appears: "john_doe is calling..."
2. Click 📞 Answer
3. Browser asks for microphone ✅ Allow
4. Connected! Talk to user
5. Timer starts

### **Scenario D: User Calls You (You're Busy)**
1. You're already in a call with someone else
2. Another user tries to call you
3. **Automatic:** Their call is logged as "missed"
4. You see badge: 🔔 Missed Calls (1)
5. Later, you can see who called and when

### **Scenario E: User Calls You (You Reject)**
1. Popup appears: "john_doe is calling..."
2. Click ✖ Reject
3. Call is logged as "rejected"
4. User sees: "Call ended"

---

## 🔧 **Technical Details**

### **Call State Indicators:**
- **● Online** - User is logged in and available
- **🔴 Offline** - User is not logged in
- **📞 In Call** - User is currently on another call

### **Auto-Features:**
- ✅ Heartbeat keeps you marked as "online"
- ✅ Missed calls update every 30 seconds
- ✅ Incoming call signals check every 2 seconds
- ✅ Call timeout: 30 seconds (auto-hangs up if no answer)

### **Call History Database:**
- Every call is logged in `call_history` table
- Tracks: who called, who was called, time, status, duration
- Status types: missed, answered, rejected, ended
- Duration recorded in seconds

---

## 🎯 **Quick Reference**

| Action | Location | Button |
|--------|----------|--------|
| **Call a user** | Left sidebar (user list) | 📞 next to name |
| **Answer call** | Popup modal | 📞 Answer |
| **Reject call** | Popup modal | ✖ Reject |
| **View missed calls** | Top right | 🔔 Missed Calls |
| **Mark call seen** | Missed calls modal | ✓ |
| **Mute yourself** | During call | 🔇 |
| **Hang up** | During call | 📞 |

---

## 📱 **Browser Requirements**

**Supported browsers:**
- ✅ Chrome (recommended)
- ✅ Edge
- ✅ Firefox
- ✅ Safari (iOS/Mac)
- ✅ Opera

**Required:**
- Microphone permission
- WebRTC support (all modern browsers)
- Internet connection

---

## 🐛 **Troubleshooting**

### **"Microphone permission denied"**
→ Click lock icon in browser address bar → Allow microphone

### **"No audio during call"**
→ Check system volume
→ Check browser permissions
→ Try refreshing page

### **"User is offline" but they're online**
→ Wait 10 seconds for heartbeat to update
→ Refresh the page

### **Can't see missed calls**
→ Refresh the page
→ Check you're logged in as admin (Ken Tse)

---

## ✅ **Everything You Need!**

Ken Tse can now:
- ✅ Call any user from the conversation list
- ✅ Receive calls from users with popup notification
- ✅ See complete call history and missed calls
- ✅ Control calls (mute, hang up, reject)
- ✅ Know if users are online/offline before calling

**All features are fully implemented and working!** 🎉
