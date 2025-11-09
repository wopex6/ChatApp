"""
ChatApp - Simplified Flask Server
One-to-many messaging: Ken Tse can chat with multiple users individually
No AI, just human-to-human communication with file support
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from chatapp_database import ChatAppDatabase
from werkzeug.utils import secure_filename
from functools import wraps
from dotenv import load_dotenv
import jwt
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
UPLOAD_FOLDER = Path('uploads')
UPLOAD_FOLDER.mkdir(exist_ok=True)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm', 'mov', 'mp3', 'wav', 'm4a', 'pdf', 'docx', 'txt'}

app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Initialize database
db = ChatAppDatabase()

# ============= Auto-create Admin Account =============

def ensure_admin_exists():
    """Ensure admin account exists on startup"""
    admin = db.get_admin_user()
    if not admin:
        print("🔧 Creating default admin account...")
        user_id = db.create_user("Ken Tse", "ken@chatapp.com", "admin123")
        if user_id:
            db.update_user_role(user_id, 'administrator')
            print("✅ Admin account created!")
            print("   Email: ken@chatapp.com")
            print("   Password: admin123")
        else:
            print("❌ Failed to create admin account")
    else:
        print(f"✅ Admin account exists: {admin['username']}")

# Create admin on startup
ensure_admin_exists()

# ============= Helper Functions =============

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            request.user_id = data['user_id']
            request.user_role = data.get('role', 'user')
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def require_admin(f):
    """Decorator to require admin role (Ken Tse only)"""
    @wraps(f)
    @require_auth
    def decorated_function(*args, **kwargs):
        if request.user_role != 'administrator':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# ============= Authentication Endpoints =============

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """User registration"""
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if username belongs to a deleted user
        deleted_user = db.check_deleted_user(username)
        if deleted_user:
            return jsonify({
                'error': 'account_deleted',
                'message': 'This account has been deleted. Please submit a restoration request to regain access.',
                'username': username
            }), 403
        
        user_id = db.create_user(username, email, password)
        
        if not user_id:
            return jsonify({'error': 'Username or email already exists'}), 409
        
        # Generate token
        token = jwt.encode({
            'user_id': user_id,
            'role': 'user',
            'exp': datetime.utcnow() + timedelta(days=30)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'message': 'User created successfully',
            'token': token,
            'user': {'id': user_id, 'username': username, 'email': email}
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        user = db.authenticate_user(username, password)
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate token
        token = jwt.encode({
            'user_id': user['id'],
            'role': user.get('role', 'user'),
            'exp': datetime.utcnow() + timedelta(days=30)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        # Get admin ID for regular users (for voice calls)
        admin_id = None
        if user.get('role') != 'administrator':
            admin_user = db.get_admin_user()
            if admin_user:
                admin_id = admin_user['id']
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user,
            'admin_id': admin_id
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/user')
@require_auth
def get_current_user():
    """Get current user info"""
    try:
        user = db.get_user_by_id(request.user_id)
        return jsonify(user), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/change-password', methods=['POST'])
@require_auth
def change_password():
    """Change user password"""
    try:
        data = request.json
        current_password = data.get('currentPassword') or data.get('current_password')
        new_password = data.get('newPassword') or data.get('new_password')
        
        if not all([current_password, new_password]):
            return jsonify({'error': 'Current and new passwords are required'}), 400
        
        # Get user info
        user = db.get_user_by_id(request.user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Verify current password
        auth_user = db.authenticate_user(user['username'], current_password)
        if not auth_user:
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Update password
        success = db.update_user_password(request.user_id, new_password)
        if success:
            return jsonify({'success': True, 'message': 'Password updated successfully'}), 200
        else:
            return jsonify({'error': 'Failed to update password'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= Restoration Request Endpoints =============

@app.route('/api/auth/request-restoration', methods=['POST'])
def request_restoration():
    """Submit a restoration request for deleted account"""
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        message = data.get('message', '')
        
        if not all([username, email]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Verify that this username is actually deleted
        deleted_user = db.check_deleted_user(username)
        if not deleted_user:
            return jsonify({'error': 'Username not found or not deleted'}), 404
        
        request_id = db.submit_restoration_request(username, email, message)
        return jsonify({
            'message': 'Restoration request submitted successfully. An administrator will review your request.',
            'request_id': request_id
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/restoration-requests', methods=['GET'])
@require_admin
def get_restoration_requests():
    """Get all restoration requests (admin only)"""
    try:
        status = request.args.get('status')  # Optional filter: pending, approved, denied
        requests = db.get_restoration_requests(status)
        return jsonify(requests), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/restoration-requests/<int:request_id>/approve', methods=['POST'])
@require_admin
def approve_restoration(request_id):
    """Approve a restoration request (admin only)"""
    try:
        success = db.approve_restoration_request(request_id, request.user_id)
        if success:
            return jsonify({'message': 'User account restored successfully'}), 200
        else:
            return jsonify({'error': 'Request not found or already processed'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/restoration-requests/<int:request_id>/deny', methods=['POST'])
@require_admin
def deny_restoration(request_id):
    """Deny a restoration request (admin only)"""
    try:
        success = db.deny_restoration_request(request_id, request.user_id)
        if success:
            return jsonify({'message': 'Restoration request denied'}), 200
        else:
            return jsonify({'error': 'Request not found or already processed'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= Profile Endpoints =============

@app.route('/api/user/profile')
@require_auth
def get_profile():
    """Get user profile"""
    try:
        profile = db.get_profile(request.user_id)
        return jsonify(profile), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/profile', methods=['PUT'])
@require_auth
def update_profile():
    """Update user profile"""
    try:
        data = request.json
        success = db.update_profile(request.user_id, data)
        
        if success:
            return jsonify({'message': 'Profile updated successfully'}), 200
        else:
            return jsonify({'error': 'Failed to update profile'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= Messaging Endpoints =============

@app.route('/api/messages', methods=['GET'])
@require_auth
def get_messages():
    """Get messages for current user"""
    try:
        messages = db.get_messages(request.user_id)
        return jsonify(messages), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/messages/mark-read', methods=['POST'])
@require_auth
def mark_messages_read():
    """Mark all messages as read for current user"""
    try:
        success = db.mark_messages_read(request.user_id)
        return jsonify({'success': success}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/messages/send', methods=['POST'])
@require_auth
def send_message():
    """Send a message to Ken Tse (or user if admin)"""
    try:
        data = request.json
        message = data.get('message', '')
        file_url = data.get('file_url')
        file_name = data.get('file_name')
        file_size = data.get('file_size')
        reply_to = data.get('reply_to')
        
        # Determine sender type
        sender_type = 'admin' if request.user_role == 'administrator' else 'user'
        
        # If admin is sending, get target user_id
        target_user_id = data.get('user_id', request.user_id)
        
        message_id = db.send_message(
            target_user_id, sender_type, message,
            file_url, file_name, file_size, reply_to
        )
        
        return jsonify({
            'message': 'Message sent successfully',
            'message_id': message_id
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/messages/unread-count', methods=['GET'])
@require_auth
def get_unread_count():
    """Get count of unread messages from Ken Tse"""
    try:
        # Users see unread from admin, admin sees unread from users
        sender_type = 'user' if request.user_role == 'administrator' else 'admin'
        count = db.get_unread_count(request.user_id, sender_type)
        return jsonify({'count': count}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/messages/<int:message_id>', methods=['DELETE'])
@require_auth
def delete_message(message_id):
    """Delete a message"""
    try:
        success = db.delete_message(message_id, request.user_id, request.user_role)
        
        if success:
            return jsonify({'message': 'Message deleted successfully'}), 200
        else:
            return jsonify({'error': 'Failed to delete message'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= Admin Endpoints (Ken Tse) =============

@app.route('/api/admin/conversations', methods=['GET'])
@require_admin
def get_all_conversations():
    """Get all user conversations (Ken Tse only)"""
    try:
        conversations = db.get_all_conversations()
        return jsonify(conversations), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/users', methods=['GET'])
@require_auth
def get_admin_users():
    """Get list of all users (for admin) or users with conversations"""
    try:
        if request.user_role != 'administrator':
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Check if include_deleted parameter is passed
        include_deleted = request.args.get('include_deleted', 'false').lower() == 'true'
        
        # Get all users
        users = db.get_all_users_for_admin(include_deleted=include_deleted)
        return jsonify(users), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/users/<int:user_id>/delete', methods=['POST'])
@require_admin
def delete_user(user_id):
    """Soft delete a user (Ken Tse only)"""
    try:
        # Don't allow deleting yourself
        if user_id == request.user_id:
            return jsonify({'error': 'Cannot delete your own account'}), 400
        
        success = db.soft_delete_user(user_id)
        if success:
            return jsonify({'success': True, 'message': 'User deleted successfully'}), 200
        else:
            return jsonify({'error': 'Failed to delete user'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/users/<int:user_id>/restore', methods=['POST'])
@require_admin
def restore_user(user_id):
    """Restore a soft-deleted user (Ken Tse only)"""
    try:
        print(f"[API Restore] Request to restore user_id: {user_id}")
        success = db.restore_user(user_id)
        if success:
            print(f"[API Restore] Success - user {user_id} restored")
            return jsonify({'success': True, 'message': 'User restored'}), 200
        else:
            print(f"[API Restore] Failed - no rows updated for user {user_id}")
            return jsonify({'error': 'Failed to restore user'}), 500
    except Exception as e:
        print(f"[API Restore] Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/users/<int:user_id>/permanent-delete', methods=['POST'])
@require_admin
def permanent_delete_user(user_id):
    """Permanently delete a user and all their data (Ken Tse only)"""
    try:
        print(f"[API Permanent Delete] Request to permanently delete user_id: {user_id}")
        
        # Don't allow deleting yourself
        if user_id == request.user_id:
            print(f"[API Permanent Delete] Blocked - cannot delete self")
            return jsonify({'error': 'Cannot delete your own account'}), 400
        
        success = db.permanent_delete_user(user_id)
        if success:
            print(f"[API Permanent Delete] Success - user {user_id} permanently deleted")
            return jsonify({'success': True, 'message': 'User permanently deleted'}), 200
        else:
            print(f"[API Permanent Delete] Failed - no rows deleted for user {user_id}")
            return jsonify({'error': 'Failed to permanently delete user'}), 500
    except Exception as e:
        print(f"[API Permanent Delete] Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/users/bulk-delete-deleted', methods=['POST'])
@require_admin
def bulk_delete_deleted_users():
    """Permanently delete all soft-deleted users (Ken Tse only)"""
    try:
        deleted_count = db.bulk_delete_deleted_users()
        return jsonify({
            'success': True,
            'message': f'Permanently deleted {deleted_count} users',
            'deleted_count': deleted_count
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/users/<int:user_id>/role', methods=['POST'])
@require_admin
def change_user_role(user_id):
    """Change a user's role (Ken Tse only)"""
    try:
        data = request.json
        new_role = data.get('role')
        
        # Validate role
        valid_roles = ['guest', 'user', 'paid', 'administrator']
        if new_role not in valid_roles:
            return jsonify({'error': 'Invalid role'}), 400
        
        # Don't allow changing own role
        if user_id == request.user_id:
            return jsonify({'error': 'Cannot change your own role'}), 400
        
        success = db.update_user_role(user_id, new_role)
        if success:
            return jsonify({'success': True, 'message': f'User role changed to {new_role}'}), 200
        else:
            return jsonify({'error': 'Failed to change user role'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/users/<int:user_id>/messages', methods=['GET'])
@require_admin
def get_user_messages(user_id):
    """Get messages for a specific user (Ken Tse only)"""
    try:
        messages = db.get_messages(user_id)
        return jsonify(messages), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/users/<int:user_id>/mark-read', methods=['POST'])
@require_admin
def mark_user_messages_read(user_id):
    """Mark all messages from a specific user as read (Ken Tse only)"""
    try:
        success = db.mark_user_messages_read_by_admin(user_id)
        return jsonify({'success': success}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= File Upload Endpoints =============

@app.route('/api/upload', methods=['POST'])
@require_auth
def upload_file():
    """Upload a file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Generate unique filename with original extension
        original_filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())
        file_extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
        unique_filename = f"{unique_id}.{file_extension}" if file_extension else unique_id
        
        filepath = app.config['UPLOAD_FOLDER'] / unique_filename
        file.save(filepath)
        
        file_size = filepath.stat().st_size
        
        return jsonify({
            'success': True,
            'filename': unique_filename,
            'original_filename': original_filename,
            'file_size': file_size,
            'file_url': f'/api/files/{unique_filename}'
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/<filename>')
def get_file(filename):
    """Serve uploaded file"""
    try:
        original_filename = request.args.get('original_name', filename)
        return send_from_directory(
            app.config['UPLOAD_FOLDER'], 
            filename,
            as_attachment=False,  # Allow inline viewing
            download_name=original_filename
        )
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

# ============= Health Check =============

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'ChatApp is running'}), 200

@app.route('/favicon.ico')
def favicon():
    """Prevent favicon 404"""
    return '', 204

@app.route('/')
def index():
    """Serve the main chat interface"""
    return send_from_directory('.', 'chatapp_login_only.html')

@app.route('/user_logon')
def user_logon():
    """Serve the chat login interface (login-only, no signup)"""
    return send_from_directory('.', 'chatapp_login_only.html')

@app.route('/signup')
def signup():
    """Legacy signup route - redirects to main login"""
    return send_from_directory('.', 'chatapp_login_only.html')

# ============= Voice Call & Status Endpoints =============

@app.route('/api/status/heartbeat', methods=['POST'])
@require_auth
def heartbeat():
    """Update user's last seen timestamp"""
    try:
        user_id = request.user_id
        db.heartbeat(user_id)
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status/user/<int:user_id>', methods=['GET'])
@require_auth
def get_user_status(user_id):
    """Get user's online status"""
    try:
        status = db.get_user_status(user_id)
        return jsonify(status), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status/update', methods=['POST'])
@require_auth
def update_status():
    """Update user status (online, offline, in_call, busy)"""
    try:
        user_id = request.user_id
        data = request.json
        status = data.get('status')
        current_call_with = data.get('current_call_with')
        
        db.update_user_status(user_id, status, current_call_with)
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/call/initiate', methods=['POST'])
@require_auth
def initiate_call():
    """Initiate a voice call"""
    try:
        caller_id = request.user_id
        data = request.json
        callee_id = data.get('callee_id')
        
        if not callee_id:
            return jsonify({'error': 'callee_id required'}), 400
        
        # Check callee status
        callee_status = db.get_user_status(callee_id)
        
        # If callee is busy or in a call, log as missed and return busy
        if callee_status['status'] in ['in_call', 'busy']:
            call_id = db.log_call_attempt(caller_id, callee_id)
            db.update_call_status(call_id, 'missed')
            return jsonify({
                'success': False,
                'reason': 'busy',
                'message': 'User is currently unavailable'
            }), 200
        
        # If callee is offline (no recent heartbeat in last 30 seconds)
        if callee_status['status'] == 'offline':
            call_id = db.log_call_attempt(caller_id, callee_id)
            db.update_call_status(call_id, 'missed')
            return jsonify({
                'success': False,
                'reason': 'offline',
                'message': 'User is offline'
            }), 200
        
        # Log call and update statuses
        call_id = db.log_call_attempt(caller_id, callee_id)
        db.update_user_status(caller_id, 'in_call', callee_id)
        
        return jsonify({
            'success': True,
            'call_id': call_id,
            'callee_status': callee_status['status']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/call/answer', methods=['POST'])
@require_auth
def answer_call():
    """Answer an incoming call"""
    try:
        user_id = request.user_id
        data = request.json
        call_id = data.get('call_id')
        caller_id = data.get('caller_id')
        
        if not call_id or not caller_id:
            return jsonify({'error': 'call_id and caller_id required'}), 400
        
        # Update call status and user statuses
        db.update_call_status(call_id, 'answered')
        db.update_user_status(user_id, 'in_call', caller_id)
        
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/call/reject', methods=['POST'])
@require_auth
def reject_call():
    """Reject an incoming call"""
    try:
        data = request.json
        call_id = data.get('call_id')
        
        if not call_id:
            return jsonify({'error': 'call_id required'}), 400
        
        db.update_call_status(call_id, 'rejected')
        
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/call/hangup', methods=['POST'])
@require_auth
def hangup_call():
    """End a call"""
    try:
        user_id = request.user_id
        data = request.json
        call_id = data.get('call_id')
        duration = data.get('duration', 0)  # seconds
        
        if not call_id:
            return jsonify({'error': 'call_id required'}), 400
        
        # Update call status
        db.update_call_status(call_id, 'ended', duration)
        
        # Update user status back to online
        db.update_user_status(user_id, 'online', None)
        
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/call/missed', methods=['GET'])
@require_auth
def get_missed_calls():
    """Get missed calls for current user (admin)"""
    try:
        user_id = request.user_id
        missed_calls = db.get_missed_calls(user_id)
        return jsonify(missed_calls), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/call/mark-seen/<int:call_id>', methods=['POST'])
@require_auth
def mark_call_seen(call_id):
    """Mark missed call as seen"""
    try:
        db.mark_missed_call_seen(call_id)
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# WebRTC signaling endpoint (for offer/answer/ICE candidates)
call_signals = {}  # In-memory store for signaling (use Redis in production)

@app.route('/api/call/signal', methods=['POST'])
@require_auth
def signal():
    """WebRTC signaling (offer, answer, ICE candidate)"""
    try:
        user_id = request.user_id
        data = request.json
        target_user_id = data.get('target_user_id')
        signal_data = data.get('signal')
        
        print(f"[SIGNAL] From user {user_id} to user {target_user_id}")
        print(f"[SIGNAL] Signal type: {signal_data.get('type') if signal_data else 'none'}")
        print(f"[SIGNAL] Current call_signals keys: {list(call_signals.keys())}")
        
        if not target_user_id or not signal_data:
            return jsonify({'error': 'target_user_id and signal required'}), 400
        
        # Store signal for target user to retrieve
        if target_user_id not in call_signals:
            call_signals[target_user_id] = []
            print(f"[SIGNAL] Created new signal queue for user {target_user_id}")
        
        call_signals[target_user_id].append({
            'from': user_id,
            'signal': signal_data,
            'timestamp': datetime.now().isoformat()
        })
        
        print(f"[SIGNAL] Stored! Queue for user {target_user_id} now has {len(call_signals[target_user_id])} signals")
        
        return jsonify({'success': True}), 200
    except Exception as e:
        print(f"[SIGNAL ERROR] {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/call/signals', methods=['GET'])
@require_auth
def get_signals():
    """Get pending signals for current user"""
    try:
        user_id = request.user_id
        
        print(f"[GET SIGNALS] User {user_id} polling for signals")
        print(f"[GET SIGNALS] Current call_signals keys: {list(call_signals.keys())}")
        print(f"[GET SIGNALS] Signals for user {user_id}: {len(call_signals.get(user_id, []))} signals")
        
        # Get and clear signals for this user
        signals = call_signals.get(user_id, [])
        if user_id in call_signals:
            call_signals[user_id] = []
            print(f"[GET SIGNALS] Cleared signals for user {user_id}")
        
        return jsonify(signals), 200
    except Exception as e:
        print(f"[GET SIGNALS ERROR] {str(e)}")
        return jsonify({'error': str(e)}), 500

# DEBUG endpoint to inspect call_signals
@app.route('/api/debug/signals', methods=['GET'])
def debug_signals():
    """Debug endpoint to see all signals in memory"""
    return jsonify({
        'call_signals': {str(k): v for k, v in call_signals.items()},
        'keys': list(call_signals.keys()),
        'count': len(call_signals)
    }), 200

# ============= Main =============

if __name__ == '__main__':
    print(f"Starting ChatApp server on port 5001...")
    print("=" * 50)
    print("📝 One-to-many messaging platform")
    print("👤 Ken Tse can chat with multiple users")
    print("💬 No AI - just human-to-human communication")
    print("🌐 Server accessible on local network at: http://192.168.0.214:5001")
    print("🌐 Server running on: http://localhost:5001")
    print("=" * 50)
    # Disable reloader to prevent multiple processes (needed for in-memory signal storage)
    app.run(debug=True, host='0.0.0.0', port=5001, use_reloader=False)
