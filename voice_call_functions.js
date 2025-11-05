/**
 * Voice Call System - Complete Implementation
 * Includes: Heartbeat, Status Tracking, WebRTC, Call Management
 */

// ============= Heartbeat & Status Management =============

function startHeartbeat() {
    console.log('📡 Starting heartbeat...');
    
    // Send initial heartbeat
    sendHeartbeat();
    
    // Set up interval to send heartbeat every 10 seconds
    heartbeatInterval = setInterval(sendHeartbeat, 10000);
    
    // Update status to online
    updateMyStatus('online');
}

async function sendHeartbeat() {
    try {
        await fetch(`${API_URL}/status/heartbeat`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });
    } catch (error) {
        console.error('Heartbeat failed:', error);
    }
}

async function updateMyStatus(status, currentCallWith = null) {
    try {
        await fetch(`${API_URL}/status/update`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                status: status,
                current_call_with: currentCallWith
            })
        });
        console.log(`📊 Status updated to: ${status}`);
    } catch (error) {
        console.error('Status update failed:', error);
    }
}

async function getUserStatus(userId) {
    try {
        const response = await fetch(`${API_URL}/status/user/${userId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        return await response.json();
    } catch (error) {
        console.error('Failed to get user status:', error);
        return { status: 'offline' };
    }
}

function stopHeartbeat() {
    if (heartbeatInterval) {
        clearInterval(heartbeatInterval);
        heartbeatInterval = null;
    }
    updateMyStatus('offline');
}

// Update status indicator UI
async function updateStatusIndicator(userId) {
    const status = await getUserStatus(userId);
    const indicator = document.getElementById('admin-status-indicator');
    
    if (!indicator) return;
    
    let statusClass, statusText, dotClass;
    
    switch (status.status) {
        case 'online':
            statusClass = 'status-online';
            statusText = 'Online';
            dotClass = 'dot-online';
            break;
        case 'in_call':
            statusClass = 'status-in-call';
            statusText = 'In Call';
            dotClass = 'dot-in-call';
            break;
        default:
            statusClass = 'status-offline';
            statusText = 'Offline';
            dotClass = 'dot-offline';
    }
    
    indicator.innerHTML = `
        <span class="status-indicator ${statusClass}">
            <span class="status-dot ${dotClass}"></span>
            ${statusText}
        </span>
    `;
    indicator.style.display = 'block';
}

// ============= Call Initiation =============

async function initiateCall() {
    console.log('📞 Initiating call to admin...');
    
    const callBtn = document.getElementById('call-admin-btn');
    if (callBtn) callBtn.disabled = true;
    
    try {
        // Check if WebRTC is supported
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            showError('Voice calls are not supported in this browser');
            return;
        }
        
        // Get admin ID (administrator role user)
        if (!adminId) {
            showError('Admin ID not found');
            return;
        }
        
        // Request microphone permission and get local stream
        try {
            localStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            console.log('🎤 Microphone access granted');
        } catch (error) {
            showError('Microphone permission denied. Please enable microphone access.');
            console.error('Microphone error:', error);
            if (callBtn) callBtn.disabled = false;
            return;
        }
        
        // Initiate call via API
        const response = await fetch(`${API_URL}/call/initiate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ callee_id: adminId })
        });
        
        const data = await response.json();
        
        if (!data.success) {
            // Admin is busy or offline
            if (localStream) {
                localStream.getTracks().forEach(track => track.stop());
                localStream = null;
            }
            
            if (data.reason === 'busy') {
                showError('Admin is currently unavailable. Your call has been recorded.');
            } else if (data.reason === 'offline') {
                showError('Admin is offline. Your call has been recorded.');
            }
            
            if (callBtn) callBtn.disabled = false;
            return;
        }
        
        // Call initiated successfully
        currentCallId = data.call_id;
        currentCallState = 'calling';
        
        // Show calling UI
        showCallingUI();
        
        // Set up WebRTC
        await setupPeerConnection();
        
        // Create and send offer
        const offer = await peerConnection.createOffer();
        await peerConnection.setLocalDescription(offer);
        
        // Send offer to admin via signaling
        await sendSignal(adminId, {
            type: 'offer',
            sdp: offer.sdp,
            call_id: currentCallId
        });
        
        // Start polling for signals (answer, ICE candidates)
        startSignalPolling();
        
        // Set timeout (30 seconds)
        setTimeout(() => {
            if (currentCallState === 'calling') {
                hangupCall('No answer');
            }
        }, 30000);
        
    } catch (error) {
        console.error('Call initiation failed:', error);
        showError('Failed to initiate call');
        if (callBtn) callBtn.disabled = false;
        
        if (localStream) {
            localStream.getTracks().forEach(track => track.stop());
            localStream = null;
        }
    }
}

// ============= WebRTC Setup =============

async function setupPeerConnection() {
    const configuration = {
        iceServers: [
            { urls: 'stun:stun.l.google.com:19302' },
            { urls: 'stun:stun1.l.google.com:19302' }
        ]
    };
    
    peerConnection = new RTCPeerConnection(configuration);
    
    // Add local stream tracks
    localStream.getTracks().forEach(track => {
        peerConnection.addTrack(track, localStream);
    });
    
    // Handle remote stream
    peerConnection.ontrack = (event) => {
        console.log('📥 Received remote track');
        remoteStream = event.streams[0];
        const remoteAudio = document.getElementById('remote-audio');
        if (remoteAudio) {
            remoteAudio.srcObject = remoteStream;
        }
    };
    
    // Handle ICE candidates
    peerConnection.onicecandidate = async (event) => {
        if (event.candidate) {
            console.log('🧊 New ICE candidate');
            await sendSignal(adminId, {
                type: 'ice',
                candidate: event.candidate,
                call_id: currentCallId
            });
        }
    };
    
    // Handle connection state changes
    peerConnection.onconnectionstatechange = () => {
        console.log('Connection state:', peerConnection.connectionState);
        
        if (peerConnection.connectionState === 'connected') {
            console.log('✅ Call connected');
            currentCallState = 'connected';
            startCallTimer();
        } else if (peerConnection.connectionState === 'disconnected' || 
                   peerConnection.connectionState === 'failed') {
            console.log('❌ Call disconnected');
            hangupCall('Connection lost');
        }
    };
}

// ============= WebRTC Signaling =============

async function sendSignal(targetUserId, signal) {
    try {
        await fetch(`${API_URL}/call/signal`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                target_user_id: targetUserId,
                signal: signal
            })
        });
    } catch (error) {
        console.error('Failed to send signal:', error);
    }
}

async function pollSignals() {
    try {
        const response = await fetch(`${API_URL}/call/signals`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        const signals = await response.json();
        
        for (const signalData of signals) {
            await handleSignal(signalData.signal, signalData.from);
        }
    } catch (error) {
        console.error('Failed to poll signals:', error);
    }
}

async function handleSignal(signal, fromUserId) {
    if (!peerConnection) return;
    
    console.log('📨 Received signal:', signal.type);
    
    if (signal.type === 'answer') {
        await peerConnection.setRemoteDescription(new RTCSessionDescription({
            type: 'answer',
            sdp: signal.sdp
        }));
        console.log('✅ Answer received, call connecting...');
        currentCallState = 'connecting';
        document.getElementById('active-call-status').textContent = 'Connecting...';
        
    } else if (signal.type === 'ice') {
        await peerConnection.addIceCandidate(new RTCIceCandidate(signal.candidate));
        
    } else if (signal.type === 'offer') {
        // Incoming call from admin
        await handleIncomingCall(signal, fromUserId);
    }
}

function startSignalPolling() {
    signalPollInterval = setInterval(pollSignals, 1000); // Poll every second
}

function stopSignalPolling() {
    if (signalPollInterval) {
        clearInterval(signalPollInterval);
        signalPollInterval = null;
    }
}

// ============= Incoming Call Handling =============

async function handleIncomingCall(offer, callerUserId) {
    console.log('📞 Incoming call from user:', callerUserId);
    
    currentCallId = offer.call_id;
    currentCallState = 'ringing';
    
    // Get caller info
    let callerName = 'User';
    if (currentUser.role === 'administrator') {
        // Admin receiving call from user
        const users = await loadAllUsersForCall();
        const caller = users.find(u => u.id === callerUserId);
        if (caller) callerName = caller.username;
    }
    
    // Show incoming call modal
    document.getElementById('incoming-caller-name').textContent = `${callerName} is calling...`;
    document.getElementById('incoming-call-modal').classList.add('show');
    
    // Play ring sound (optional)
    playRingSound();
    
    // Store offer for when user answers
    window.pendingOffer = offer;
    window.pendingCallerId = callerUserId;
}

async function answerCall() {
    console.log('✅ Answering call...');
    
    // Hide incoming call modal
    document.getElementById('incoming-call-modal').classList.remove('show');
    
    try {
        // Get microphone permission
        localStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        // Set up peer connection
        await setupPeerConnection();
        
        // Set remote description (offer)
        await peerConnection.setRemoteDescription(new RTCSessionDescription({
            type: 'offer',
            sdp: window.pendingOffer.sdp
        }));
        
        // Create answer
        const answer = await peerConnection.createAnswer();
        await peerConnection.setLocalDescription(answer);
        
        // Send answer back
        await sendSignal(window.pendingCallerId, {
            type: 'answer',
            sdp: answer.sdp,
            call_id: currentCallId
        });
        
        // Update call status in backend
        await fetch(`${API_URL}/call/answer`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                call_id: currentCallId,
                caller_id: window.pendingCallerId
            })
        });
        
        // Show active call UI
        currentCallState = 'connected';
        let callerName = 'User';
        if (currentUser.role === 'administrator') {
            const users = await loadAllUsersForCall();
            const caller = users.find(u => u.id === window.pendingCallerId);
            if (caller) callerName = caller.username;
        }
        
        document.getElementById('active-call-name').textContent = callerName;
        document.getElementById('active-call-status').textContent = 'Connected';
        document.getElementById('active-call-modal').classList.add('show');
        
        startCallTimer();
        startSignalPolling();
        
    } catch (error) {
        console.error('Failed to answer call:', error);
        showError('Failed to answer call');
        rejectCall();
    }
}

async function rejectCall() {
    console.log('❌ Rejecting call');
    
    // Hide modal
    document.getElementById('incoming-call-modal').classList.remove('show');
    
    // Update backend
    if (currentCallId) {
        await fetch(`${API_URL}/call/reject`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ call_id: currentCallId })
        });
    }
    
    cleanupCall();
}

// ============= Call Controls =============

async function hangupCall(reason = 'Call ended') {
    console.log('📴 Hanging up call:', reason);
    
    const duration = callStartTime ? Math.floor((Date.now() - callStartTime) / 1000) : 0;
    
    // Update backend
    if (currentCallId) {
        await fetch(`${API_URL}/call/hangup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                call_id: currentCallId,
                duration: duration
            })
        });
    }
    
    // Hide modals
    document.getElementById('active-call-modal').classList.remove('show');
    document.getElementById('incoming-call-modal').classList.remove('show');
    
    // Show reason if provided
    if (reason && reason !== 'Call ended') {
        showError(reason);
    }
    
    cleanupCall();
    
    // Re-enable call button
    const callBtn = document.getElementById('call-admin-btn');
    if (callBtn) callBtn.disabled = false;
}

function toggleMute() {
    if (!localStream) return;
    
    const audioTrack = localStream.getAudioTracks()[0];
    if (!audioTrack) return;
    
    audioTrack.enabled = !audioTrack.enabled;
    
    const muteBtn = document.getElementById('mute-btn');
    if (audioTrack.enabled) {
        muteBtn.textContent = '🔇';
        muteBtn.classList.remove('active');
    } else {
        muteBtn.textContent = '🔊';
        muteBtn.classList.add('active');
    }
}

function cleanupCall() {
    // Stop timers
    if (callTimerInterval) {
        clearInterval(callTimerInterval);
        callTimerInterval = null;
    }
    
    stopSignalPolling();
    
    // Stop media streams
    if (localStream) {
        localStream.getTracks().forEach(track => track.stop());
        localStream = null;
    }
    
    if (remoteStream) {
        remoteStream.getTracks().forEach(track => track.stop());
        remoteStream = null;
    }
    
    // Close peer connection
    if (peerConnection) {
        peerConnection.close();
        peerConnection = null;
    }
    
    // Reset state
    currentCallId = null;
    currentCallState = null;
    callStartTime = null;
    
    // Update status back to online
    updateMyStatus('online');
}

// ============= UI Functions =============

function showCallingUI() {
    const adminName = localStorage.getItem(`admin_name_for_user_${currentUser.id}`) || 'Ken';
    
    document.getElementById('active-call-name').textContent = adminName;
    document.getElementById('active-call-status').textContent = 'Calling...';
    document.getElementById('call-timer').textContent = '00:00';
    document.getElementById('active-call-modal').classList.add('show');
}

function startCallTimer() {
    callStartTime = Date.now();
    
    callTimerInterval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - callStartTime) / 1000);
        const minutes = Math.floor(elapsed / 60);
        const seconds = elapsed % 60;
        
        const timerDisplay = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        document.getElementById('call-timer').textContent = timerDisplay;
    }, 1000);
}

function playRingSound() {
    // Optional: Play a ring sound
    // Can be implemented with an audio element if needed
}

// ============= Missed Calls =============

async function loadMissedCalls() {
    if (currentUser.role !== 'administrator') return;
    
    try {
        const response = await fetch(`${API_URL}/call/missed`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        const missedCalls = await response.json();
        
        // Update badge
        const unseenCount = missedCalls.filter(call => !call.seen).length;
        const badge = document.getElementById('missed-calls-count');
        const indicator = document.getElementById('missed-calls-indicator');
        
        if (unseenCount > 0) {
            badge.textContent = unseenCount;
            badge.style.display = 'flex';
            indicator.style.display = 'block';
        } else {
            badge.style.display = 'none';
            if (missedCalls.length === 0) {
                indicator.style.display = 'none';
            }
        }
        
        return missedCalls;
        
    } catch (error) {
        console.error('Failed to load missed calls:', error);
        return [];
    }
}

async function showMissedCalls() {
    const missedCalls = await loadMissedCalls();
    
    if (missedCalls.length === 0) {
        showSuccess('No missed calls');
        return;
    }
    
    // Show modal with missed calls
    let html = '<div class="missed-calls-list">';
    
    for (const call of missedCalls) {
        const time = new Date(call.call_time).toLocaleString();
        const seenClass = call.seen ? 'seen' : '';
        
        html += `
            <div class="missed-call-item ${seenClass}">
                <div>
                    <strong>${call.caller_username}</strong><br>
                    <small>${time}</small>
                </div>
                <button class="btn-small" onclick="markCallSeen(${call.id})">✓</button>
            </div>
        `;
    }
    
    html += '</div>';
    
    showConfirmModal('Missed Calls', html, () => {
        // Mark all as seen
        missedCalls.forEach(call => markCallSeen(call.id));
    }, 'Mark All Seen', 'Close');
}

async function markCallSeen(callId) {
    try {
        await fetch(`${API_URL}/call/mark-seen/${callId}`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        await loadMissedCalls();
        
    } catch (error) {
        console.error('Failed to mark call as seen:', error);
    }
}

// ============= Helper Functions =============

async function loadAllUsersForCall() {
    // Load all users for getting caller names
    try {
        const response = await fetch(`${API_URL}/admin/users?include_deleted=false`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        return await response.json();
    } catch (error) {
        console.error('Failed to load users:', error);
        return [];
    }
}

// Export functions to global scope if needed
window.startHeartbeat = startHeartbeat;
window.stopHeartbeat = stopHeartbeat;
window.initiateCall = initiateCall;
window.answerCall = answerCall;
window.rejectCall = rejectCall;
window.hangupCall = hangupCall;
window.toggleMute = toggleMute;
window.showMissedCalls = showMissedCalls;
window.markCallSeen = markCallSeen;
window.updateStatusIndicator = updateStatusIndicator;
window.pollSignals = pollSignals;

console.log('📞 Voice call system loaded');
