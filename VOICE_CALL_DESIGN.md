# 📞 Voice Call System Design

## 🎯 Requirements

### **Core Features:**
1. ✅ Voice call between user and admin (WebRTC)
2. ✅ Show caller "admin is offline" if admin is busy
3. ✅ Record missed calls with timestamp
4. ✅ Show admin who called when they were busy
5. ✅ Check if user is offline before admin calls
6. ✅ Handle all edge cases

---

## 🏗️ System Architecture

### **Components:**

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   User      │◄──────► │   Server    │◄──────► │   Admin     │
│  Browser    │ WebRTC  │  Signaling  │ WebRTC  │  Browser    │
└─────────────┘         └─────────────┘         └─────────────┘
      │                        │                       │
      ├── Microphone           ├── Call State         ├── Speaker
      ├── Speaker              ├── User Status        ├── Microphone
      └── UI Controls          └── Missed Calls       └── UI Controls
```

---

## 📊 Database Schema

### **New Tables:**

#### **1. user_status**
```sql
CREATE TABLE user_status (
    user_id INTEGER PRIMARY KEY,
    status TEXT DEFAULT 'offline',  -- 'online', 'offline', 'in_call', 'busy'
    last_seen TIMESTAMP,
    current_call_with INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (current_call_with) REFERENCES users(id)
);
```

#### **2. call_history**
```sql
CREATE TABLE call_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    caller_id INTEGER NOT NULL,
    callee_id INTEGER NOT NULL,
    call_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    call_status TEXT,  -- 'missed', 'answered', 'rejected', 'dropped'
    call_duration INTEGER,  -- seconds
    answered_at TIMESTAMP,
    ended_at TIMESTAMP,
    FOREIGN KEY (caller_id) REFERENCES users(id),
    FOREIGN KEY (callee_id) REFERENCES users(id)
);
```

---

## 🔄 Call States

### **User States:**
- `offline` - Not logged in
- `online` - Logged in, available
- `calling` - Initiating a call
- `ringing` - Being called
- `in_call` - Currently in a call
- `busy` - In call with someone else

### **Call States:**
- `initiating` - User clicked call button
- `ringing` - Admin's phone is ringing
- `connecting` - WebRTC negotiation
- `connected` - Active call
- `ended` - Call finished
- `missed` - Admin didn't answer
- `rejected` - Admin declined
- `failed` - Technical error

---

## 🎨 UI Components

### **User View:**
```
┌──────────────────────────────────────┐
│ Chat with Ken                        │
│                                      │
│ [Messages...]                        │
│                                      │
│ [📞 Call Ken] ← Button               │
│                                      │
│ Status: ● Online / 🔴 Busy          │
└──────────────────────────────────────┘

When Calling:
┌──────────────────────────────────────┐
│ 📞 Calling Ken...                    │
│ ⏱️ 00:05                             │
│ [🔇 Mute] [📞 Hang Up]               │
└──────────────────────────────────────┘

When Admin Busy:
┌──────────────────────────────────────┐
│ ⚠️ Admin is currently unavailable    │
│ Your call has been recorded          │
│ Ken will see you tried to reach them │
└──────────────────────────────────────┘
```

### **Admin View:**
```
┌──────────────────────────────────────┐
│ Admin Dashboard                      │
│                                      │
│ john_doe (● Online)                  │
│ [📞 Call] [💬 Chat]                  │
│                                      │
│ jane_smith (🔴 Offline)              │
│ [📞 Call] [💬 Chat]                  │
│ └─ ⚠️ Cannot call (offline)          │
│                                      │
│ 🔔 Missed Calls:                     │
│ • bob_jones called at 2:45 PM        │
│ • alice_w called at 1:30 PM          │
└──────────────────────────────────────┘

When In Call:
┌──────────────────────────────────────┐
│ 📞 In Call with john_doe             │
│ ⏱️ 02:34                             │
│ [🔇 Mute] [📞 Hang Up]               │
│                                      │
│ 🔔 alice_w is calling... (waiting)   │
└──────────────────────────────────────┘
```

---

## 🔌 API Endpoints

### **Call Management:**
```
POST   /api/call/initiate        - Start call
POST   /api/call/answer          - Answer incoming call
POST   /api/call/reject          - Reject incoming call
POST   /api/call/hangup          - End call
GET    /api/call/status          - Get current call state
POST   /api/call/signal          - WebRTC signaling (offer/answer/ICE)
```

### **Status Management:**
```
GET    /api/status/user/:id      - Get user online status
POST   /api/status/heartbeat     - Update "last seen"
GET    /api/status/missed-calls  - Get missed call list
POST   /api/status/mark-seen     - Mark missed call as seen
```

---

## 🎯 Call Flow Diagrams

### **Scenario 1: Successful Call**
```
User                    Server                  Admin
 │                        │                       │
 ├─ Click [Call]         │                       │
 ├─────initiate()────────>│                       │
 │                        ├─ Check admin status  │
 │                        ├─ Status: online      │
 │                        ├────ring()────────────>│
 │                        │                       ├─ Show incoming
 │                        │                       ├─ Ring sound
 │                        │<────answer()──────────┤
 │<────connected()────────┤                       │
 ├─ WebRTC handshake ────────────────────────────>│
 │<══════ Voice Stream ══════════════════════════>│
 │                        │                       │
 ├────hangup()───────────>│                       │
 │                        ├────ended()───────────>│
 │<────ack()──────────────┤<────ack()─────────────┤
```

### **Scenario 2: Admin Busy**
```
User                    Server                  Admin (In Call)
 │                        │                       │
 ├─ Click [Call]         │                       │
 ├─────initiate()────────>│                       │
 │                        ├─ Check admin status  │
 │                        ├─ Status: in_call     │
 │<────busy()─────────────┤                       │
 ├─ Show "Offline"       │                       │
 │                        ├─ Log missed call     │
 │                        ├─ Notify admin later ─>│
 │                        │                       ├─ Show badge
```

### **Scenario 3: User Offline (Admin Calling)**
```
Admin                   Server                  User (Offline)
 │                        │                       │
 ├─ Click [Call user]    │                       │
 ├─────initiate()────────>│                       │
 │                        ├─ Check user status   │
 │                        ├─ Status: offline     │
 │<────offline()──────────┤                       │
 ├─ Show "User offline"  │                       │
```

---

## 🛡️ Edge Cases & Handling

### **1. Connection Drops During Call**
- **Detection:** WebRTC connection state changes to "disconnected"
- **Action:** Show reconnecting UI for 5 seconds
- **Fallback:** If not reconnected, end call and log as "dropped"

### **2. Microphone Permission Denied**
- **Detection:** `getUserMedia()` rejects with permission error
- **Action:** Show error message with instructions to enable mic
- **UI:** Button disabled until permission granted

### **3. Multiple Users Calling Simultaneously**
- **Detection:** Admin already in `in_call` state
- **Action:** Queue call as "missed", notify later
- **UI:** Show caller "Admin is busy" message

### **4. User Navigates Away During Call**
- **Detection:** `beforeunload` or WebSocket disconnect
- **Action:** Automatically hang up, notify other party

### **5. Network Quality Issues**
- **Detection:** ICE connection state, stats API
- **Action:** Show network quality indicator
- **Fallback:** Suggest reconnecting if quality too poor

### **6. Browser Not Supported**
- **Detection:** Check for WebRTC API availability
- **Action:** Hide call button, show message about browser support

### **7. Call Timeout (No Answer)**
- **Detection:** 30 seconds with no answer
- **Action:** Auto-hangup, log as "missed call"

### **8. Spam Protection**
- **Detection:** More than 5 calls in 5 minutes
- **Action:** Rate limit, show cooldown message

### **9. Admin Logs Out During Call**
- **Detection:** Session invalidated
- **Action:** Disconnect call gracefully, notify user

### **10. Simultaneous Admin/User Call**
- **Detection:** Both parties initiate call at same time
- **Action:** Use timestamp tiebreaker (earlier wins)

---

## 🔊 WebRTC Implementation

### **Simple Peer-to-Peer:**
```javascript
// User initiates
const peerConnection = new RTCPeerConnection(config);
const localStream = await navigator.mediaDevices.getUserMedia({ audio: true });

localStream.getTracks().forEach(track => {
    peerConnection.addTrack(track, localStream);
});

// Create offer
const offer = await peerConnection.createOffer();
await peerConnection.setLocalDescription(offer);

// Send offer to server → admin
sendSignal({ type: 'offer', sdp: offer });

// Receive answer from admin
peerConnection.setRemoteDescription(answer);

// Handle ICE candidates
peerConnection.onicecandidate = (event) => {
    if (event.candidate) {
        sendSignal({ type: 'ice', candidate: event.candidate });
    }
};

// Receive remote stream
peerConnection.ontrack = (event) => {
    remoteAudio.srcObject = event.streams[0];
};
```

---

## 📋 Implementation Checklist

### **Phase 1: Status Tracking**
- [ ] Add user_status table
- [ ] Implement heartbeat system (ping every 10s)
- [ ] Show online/offline indicators
- [ ] Detect when user navigates away

### **Phase 2: Call History**
- [ ] Add call_history table
- [ ] Log all call attempts
- [ ] Display missed calls to admin
- [ ] Mark calls as seen/unseen

### **Phase 3: Call UI**
- [ ] Add call button to user view
- [ ] Add call button to admin user list
- [ ] Create incoming call modal
- [ ] Create active call controls
- [ ] Add call status indicators

### **Phase 4: WebRTC**
- [ ] Implement signaling server
- [ ] Add WebRTC offer/answer flow
- [ ] Handle ICE candidates
- [ ] Connect audio streams
- [ ] Add mute functionality

### **Phase 5: Call States**
- [ ] Implement state machine
- [ ] Handle busy detection
- [ ] Queue missed calls
- [ ] Timeout handling
- [ ] Graceful disconnection

### **Phase 6: Edge Cases**
- [ ] Connection drop recovery
- [ ] Permission handling
- [ ] Browser compatibility check
- [ ] Network quality monitoring
- [ ] Rate limiting

### **Phase 7: Testing**
- [ ] Test successful call flow
- [ ] Test busy scenario
- [ ] Test offline scenario
- [ ] Test disconnection handling
- [ ] Test multiple users

---

## 🎛️ Configuration

### **Call Settings:**
```javascript
const CALL_CONFIG = {
    RING_TIMEOUT: 30000,        // 30 seconds
    HEARTBEAT_INTERVAL: 10000,  // 10 seconds
    RECONNECT_TIMEOUT: 5000,    // 5 seconds
    MAX_CALLS_PER_PERIOD: 5,    // Rate limit
    RATE_LIMIT_PERIOD: 300000,  // 5 minutes
    ICE_SERVERS: [
        { urls: 'stun:stun.l.google.com:19302' }
    ]
};
```

---

## 🔐 Security Considerations

1. **Authentication:** Only authenticated users can initiate calls
2. **Authorization:** Users can only call admin, not other users
3. **Rate Limiting:** Prevent spam calling
4. **Encryption:** WebRTC uses DTLS-SRTP (encrypted by default)
5. **Session Validation:** Check token on every signaling message

---

## 📱 Mobile Considerations

1. **Battery:** Minimize background polling
2. **Permissions:** Handle mobile mic permissions
3. **Network:** Handle 3G/4G/WiFi transitions
4. **Background:** Detect when app goes to background
5. **Notifications:** Browser notifications for incoming calls

---

## 🚀 Next Steps

1. ✅ Create database schema
2. ✅ Implement status tracking backend
3. ✅ Add UI components
4. ✅ Implement WebRTC signaling
5. ✅ Test call scenarios
6. ✅ Handle edge cases
7. ✅ Deploy and monitor

---

**This is a comprehensive system. Let's build it step by step!**
