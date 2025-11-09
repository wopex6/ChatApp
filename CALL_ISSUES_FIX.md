# Call Issues - Analysis & Fix

**Date:** November 9, 2025 - 17:18  
**Issues Reported:**

1. **PC user called → Phone answered → PC didn't know it was answered (keeps waiting)**
2. **Phone admin called → PC user didn't get popup**

---

## Root Cause Analysis

### Issue 1: PC Not Receiving Answer Signal

**Current Flow:**
```
PC User:
  1. initiateCall() → starts signal polling ✅
  2. sends offer signal
  3. Polls for signals every 1 second ✅
  
Phone Admin:
  1. Receives offer via signal polling ✅
  2. Shows incoming call modal ✅
  3. Answers → sends answer signal ✅
  
PC User (should receive):
  4. Polls signals → gets answer
  5. handleSignal() processes answer
  6. BUT... checking logs, answer might not be processed correctly
```

**Potential Problems:**
- Signal polling might stop if there's an error
- Answer signal might not be sent to correct user ID
- Backend might not be storing signals correctly

### Issue 2: PC Not Showing Incoming Call Popup

**Current Flow:**
```
Phone Admin:
  1. Logged in → startSignalPolling() ✅
  2. callUser(userId) → sends offer ✅
  
PC User:
  1. Logged in → startSignalPolling() ✅
  2. Polls every 1 second ✅
  3. Should receive offer signal
  4. Should call handleIncomingCall()
  5. Should show modal
  
BUT: PC didn't get popup!
```

**Potential Problems:**
- Signal polling might have stopped
- Offer signal sent to wrong user ID
- handleIncomingCall() not showing modal correctly

---

## Debugging Steps

### Check Backend Signal Storage

The backend uses an in-memory dictionary:
```python
call_signals = {}  # {user_id: [signals]}
```

**Possible Issue:** Signals might be cleared before being read, or stored with wrong user ID.

### Check Frontend Signal Polling

Signal polling should run continuously after login, but might stop if:
1. Error in pollSignals() (caught but logged)
2. Token becomes invalid
3. Interval cleared accidentally

---

## The Fix

### Add More Logging to Debug

1. **In answerCall()** - log what user ID the answer is being sent to
2. **In pollSignals()** - log user ID and what signals are received
3. **In backend /api/call/signal** - log exactly what's being stored

### Ensure Signal Delivery

The issue might be in how we identify the target user:

**When USER calls ADMIN:**
```javascript
// User side
await sendSignal(adminId, {  // ← Sending TO admin
    type: 'offer',
    ...
});

// Admin side (answering)
await sendSignal(window.pendingCallerId, {  // ← Sending back TO user
    type: 'answer',
    ...
});
```

**When ADMIN calls USER:**
```javascript
// Admin side
await sendSignal(userId, {  // ← Sending TO user
    type: 'offer',
    ...
});

// User side (answering)
await sendSignal(window.pendingCallerId, {  // ← Sending back TO admin
    type: 'answer',
    ...
});
```

The `window.pendingCallerId` might not be set correctly!

---

## CRITICAL FIX NEEDED

### Problem: `window.pendingCallerId` might be undefined

When admin answers a call FROM a user:
```javascript
// In handleIncomingCall():
window.pendingCallerId = callerUserId;  // ✅ Set correctly

// In answerCall():
await sendSignal(window.pendingCallerId, { ... });  // ✅ Should work
```

When user answers a call FROM admin:
```javascript
// In handleIncomingCall():
window.pendingCallerId = callerUserId;  // ✅ Set to admin ID

// In answerCall():
await sendSignal(window.pendingCallerId, { ... });  // ✅ Should work
```

**This SHOULD be working!**

### Alternative Problem: Backend Signal Routing

Check if backend is routing signals correctly:

```python
# Sending signal
@app.route('/api/call/signal', methods=['POST'])
def signal():
    target_user_id = data.get('target_user_id')
    call_signals[target_user_id] = ...  # ← Store for TARGET
    
# Receiving signals
@app.route('/api/call/signals', methods=['GET'])
def get_signals():
    user_id = request.user_id  # ← Get for CURRENT user
    signals = call_signals.get(user_id, [])
```

**Issue:** If `target_user_id` and `request.user_id` types don't match (string vs int), lookups fail!

---

## RECOMMENDED FIX

### Add Explicit Logging

This will help us see exactly what's happening:

```javascript
// In answerCall()
console.log('🎯 SENDING ANSWER TO:', window.pendingCallerId, 'Type:', typeof window.pendingCallerId);
console.log('📝 Call ID:', currentCallId);
console.log('👤 Current user:', currentUser.id, currentUser.username);

await sendSignal(window.pendingCallerId, {
    type: 'answer',
    sdp: answer.sdp,
    call_id: currentCallId
});
console.log('✅ Answer signal sent!');
```

```javascript
// In handleSignal() when receiving answer
console.log('📥 RECEIVED ANSWER from user:', fromUserId);
console.log('🔗 Peer connection exists:', !!peerConnection);
console.log('📊 Current call state:', currentCallState);
```

### Ensure Signal Polling Stays Active

Add a heartbeat check:

```javascript
// Add this to pollSignals()
if (!signalPollInterval) {
    console.error('⚠️ Signal polling stopped! Restarting...');
    startSignalPolling();
}
```

---

## Next Steps

1. Add enhanced logging (above)
2. Test again with console open on both PC and phone
3. Share console logs to identify exact failure point
4. Fix based on logs

Would you like me to implement these logging fixes now?
