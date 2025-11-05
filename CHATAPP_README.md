# ChatApp - One-to-Many Messaging Platform

**Version:** 1.0  
**Last Updated:** November 2, 2025

---

## Overview

ChatApp is a simplified messaging platform where **Ken Tse** can chat individually with multiple users. This is a human-to-human communication system with no AI features.

### Key Features

✅ **User Authentication** - Secure signup/login system  
✅ **Direct Messaging** - Users chat directly with Ken Tse  
✅ **File Attachments** - Send images, videos, audio, documents  
✅ **Message Threading** - Reply to specific messages  
✅ **Read Receipts** - See when messages are read  
✅ **Real-time Updates** - Live message notifications  
✅ **Admin Dashboard** - Ken Tse sees all user conversations

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_simple.txt
```

### 2. Run Migration (If Coming from AI Version)

```bash
python migrate_to_chatapp.py
```

This will:
- Backup your current database
- Remove AI-related tables
- Create Ken Tse's administrator account
- Verify migration success

### 3. Start the Server

```bash
python chatapp_simple.py
```

The server will start on `http://localhost:5001`

### 4. Login Credentials

**Ken Tse (Administrator):**
- Username: `Ken Tse`
- Email: `ken@chatapp.com`
- Password: `KenTse2025!` ⚠️ **Change this after first login!**

**Regular Users:**
- Can sign up at `/signup`

---

## Architecture

### Database Tables

#### 1. `users`
User authentication and account info
- `id`, `username`, `email`, `password_hash`
- `role` (user/administrator)
- `is_deleted`, `is_verified`
- `created_at`, `updated_at`

#### 2. `user_profiles`
Basic user profile information
- `user_id`, `first_name`, `last_name`
- `bio`, `avatar_url`

#### 3. `admin_messages`
All messages between Ken Tse and users
- `user_id`, `sender_type` (user/admin)
- `message`, `is_read`
- `file_url`, `file_name`, `file_size`
- `reply_to` (for threading)
- `timestamp`

---

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Register new user |
| POST | `/api/auth/login` | User login |
| GET | `/api/auth/user` | Get current user |
| POST | `/api/auth/change-password` | Change password |

### Messaging (Users)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/messages` | Get all messages |
| POST | `/api/messages/send` | Send message to Ken Tse |
| GET | `/api/messages/unread-count` | Get unread count |
| POST | `/api/messages/mark-read` | Mark messages as read |
| DELETE | `/api/messages/<id>` | Delete a message |

### Admin (Ken Tse Only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/conversations` | Get all user conversations |
| GET | `/api/admin/users` | Get all users |
| GET | `/api/admin/users/<id>/messages` | Get user's messages |

### File Upload

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload` | Upload file (images, videos, audio, docs) |
| GET | `/api/files/<filename>` | Download/view file |

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Server health status |

---

## User Experience

### For Regular Users

1. **Sign Up / Log In**
   - Create account or log in with existing credentials

2. **Send Messages**
   - Type messages to Ken Tse
   - Attach files (images, videos, audio, documents)
   - Reply to specific messages

3. **View History**
   - See full conversation history with Ken Tse
   - Know when messages are read

4. **Notifications**
   - Get notified when Ken Tse replies
   - See unread message count

### For Ken Tse (Administrator)

1. **View All Conversations**
   - See list of all users who have messaged
   - See unread message counts per user
   - Sort by most recent activity

2. **Chat with Any User**
   - Click on a user to view conversation
   - Reply to users
   - Send files to users

3. **Manage Messages**
   - Delete any message
   - Reply to specific messages (threading)
   - Mark conversations as read

---

## File Upload Support

### Supported File Types

**Images:** `.png`, `.jpg`, `.jpeg`, `.gif`  
**Videos:** `.mp4`, `.webm`, `.mov`  
**Audio:** `.mp3`, `.wav`, `.m4a`  
**Documents:** `.pdf`, `.docx`, `.txt`

### Limits

- **Max File Size:** 50 MB
- **Storage:** Local filesystem (`uploads/` directory)

---

## Security Features

✅ **Password Hashing** - bcrypt with salt  
✅ **JWT Authentication** - 30-day token expiry  
✅ **Role-Based Access** - User vs Administrator  
✅ **Secure File Upload** - Filename sanitization  
✅ **SQL Injection Protection** - Parameterized queries

---

## Development

### Project Structure

```
ChatApp/
├── chatapp_simple.py          # Main Flask server
├── chatapp_database.py        # Database layer
├── migrate_to_chatapp.py      # Migration script
├── requirements_simple.txt    # Dependencies
├── uploads/                   # File storage
├── templates/                 # HTML templates (if using)
├── static/                    # CSS/JS files
└── integrated_users.db        # SQLite database
```

### Adding New Features

1. **New Endpoint:** Add route in `chatapp_simple.py`
2. **Database Method:** Add method in `chatapp_database.py`
3. **Migration:** Update `migrate_to_chatapp.py` if schema changes

---

## Configuration

### Environment Variables

Create a `.env` file:

```env
SECRET_KEY=your-secret-key-here
MAX_FILE_SIZE=52428800  # 50MB in bytes
UPLOAD_FOLDER=uploads
```

### Default Configuration

- **Port:** 5000
- **Host:** 0.0.0.0 (accessible from network)
- **Debug Mode:** True (development only)
- **Database:** SQLite (`integrated_users.db`)

---

## Troubleshooting

### Common Issues

**1. "Database locked" error**
- Close any database browsers or connections
- Restart the server

**2. "Invalid token" on login**
- Clear browser localStorage
- Log in again

**3. File upload fails**
- Check file size (< 50MB)
- Verify file type is allowed
- Ensure `uploads/` directory exists

**4. Can't see messages**
- Verify you're logged in
- Check user_id matches in database
- Verify sender_type is correct

---

## Migration Notes

### Coming from AI Version

The migration script (`migrate_to_chatapp.py`) will:

✅ **Remove These Tables:**
- `ai_conversations`
- `messages` (AI messages)
- `psychology_traits`
- `user_interactions`

✅ **Keep These Tables:**
- `users`
- `user_profiles`
- `admin_messages` (renamed conceptually to "messages")

✅ **Create:**
- Ken Tse administrator account
- Database backup

### Manual Steps After Migration

1. Update frontend to use new endpoints
2. Change "Admin" labels to "Ken Tse" in UI
3. Test file upload functionality
4. Change Ken Tse's default password

---

## Future Enhancements

### Possible Features

- [ ] **Typing Indicators** - "Ken Tse is typing..."
- [ ] **Message Reactions** - 👍 ❤️ 😂
- [ ] **Voice Messages** - Record and send audio
- [ ] **Video Calls** - WebRTC integration
- [ ] **Push Notifications** - Mobile/desktop alerts
- [ ] **Message Search** - Search conversation history
- [ ] **Archive Conversations** - Hide old chats
- [ ] **Export History** - Download conversation as PDF

---

## Support

For issues or questions about ChatApp:

1. Check this documentation
2. Review error messages in console
3. Check database integrity with migration script
4. Verify API endpoints are responding

---

## License

This is a private messaging platform for internal use.

---

## Changelog

### Version 1.0 (November 2, 2025)
- Initial release
- Converted from AI-powered platform
- Basic messaging with file attachments
- Admin dashboard for Ken Tse
- User authentication system
- Message threading support

---

**Built with ❤️ for simple, effective communication**
