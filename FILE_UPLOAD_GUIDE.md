# 📎 File Upload Feature Guide

**ChatApp now supports full file, audio, and video attachments!**

---

## ✨ Features Added

### 1. **File Upload Button**
- 📎 Attachment button next to the send button
- Click to select files from your device
- Preview selected file before sending

### 2. **Supported File Types**

#### Images 🖼️
- `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.svg`
- **Display:** Inline preview (max 300x200px)
- **Click:** Opens full size in new tab

#### Videos 🎥
- `.mp4`, `.webm`, `.mov`, `.avi`
- **Display:** Inline video player with controls
- **Max Size:** 400x300px player

#### Audio 🎵
- `.mp3`, `.wav`, `.ogg`, `.m4a`
- **Display:** Inline audio player with controls
- **Full width** player in messages

#### Documents 📄
- `.pdf`, `.doc`, `.docx`, `.txt`
- **Display:** Download link with icon
- **Click:** Downloads file

#### Archives 🗜️
- `.zip`, `.rar`
- **Display:** Download link with icon

### 3. **File Size Limit**
- **Maximum:** 50 MB per file
- **Error shown** if file exceeds limit

---

## 🎯 How to Use

### For Users:

1. **Click the 📎 button** next to the message input
2. **Select a file** from your device
3. **Preview appears** showing filename and size
4. **Type optional message** (or just send the file)
5. **Click Send** - file uploads then message sends

### For Ken Tse (Admin):

Same as users, plus:
- Can send files to any selected user
- File uploads work in all conversations

---

## 🔧 Technical Details

### Backend (`chatapp_simple.py`)

**Upload Endpoint:** `POST /api/upload`
- Accepts multipart/form-data
- Generates unique UUID filename
- Preserves original file extension
- Returns file metadata

**Download Endpoint:** `GET /api/files/<filename>`
- Serves files inline (not as download)
- Supports original filename parameter
- Works for all file types

### Frontend (`chatapp_frontend.html`)

**File Selection:**
```javascript
handleFileSelect(event)  // When user picks file
removeFile()              // Remove selected file
uploadFile()              // Upload to server
```

**File Display:**
```javascript
renderAttachment()        // Render based on type
getFileIcon()            // Get emoji for file type
formatFileSize()         // Format bytes to KB/MB
```

**Message Flow:**
1. User selects file → Preview shown
2. User clicks Send → File uploads first
3. File URL added to message → Message sent
4. File renders inline in chat

---

## 📊 File Type Detection

**By Extension:**
- Images: Show `<img>` tag
- Videos: Show `<video>` tag with controls
- Audio: Show `<audio>` tag with controls
- Documents: Show download link with icon

**Icons Used:**
- 📄 PDF files
- 📝 Word/Text files
- 📊 Excel files
- 🗜️ Archive files
- 📎 Other files

---

## 🎨 UI Features

### File Preview (Before Send)
```
┌─────────────────────────────┐
│ 📎 myfile.pdf (2.3 MB)   ✕ │
└─────────────────────────────┘
```

### Image Display
- Inline preview
- Click to open full size
- Rounded corners
- Filename and size below

### Video Display
- Native HTML5 player
- Play/pause controls
- Volume control
- Fullscreen option

### Audio Display
- Native HTML5 player
- Play/pause, volume
- Timeline scrubber
- Full width

### Document Display
- Download button style
- File icon
- Filename and size
- Hover effect

---

## 🔒 Security Features

✅ **File Size Validation** - Client and server side  
✅ **File Type Validation** - Allowed extensions only  
✅ **Unique Filenames** - UUID to prevent conflicts  
✅ **Secure Filename** - Werkzeug sanitization  
✅ **Authentication Required** - Must be logged in

---

## 💾 Storage

**Location:** `uploads/` directory  
**Naming:** `<uuid>.<extension>`  
**Example:** `a1b2c3d4-5e6f-7g8h-9i0j.jpg`

**Original filename preserved in:**
- Database (file_name column)
- Download link parameter
- Display in messages

---

## 🧪 Testing File Uploads

### Test Image
1. Login to ChatApp
2. Click 📎 button
3. Select any image file
4. See preview
5. Send message
6. Image appears inline in chat
7. Click image to view full size

### Test Video
1. Select video file (mp4, webm)
2. Send message
3. Video player appears
4. Click play to watch

### Test Audio
1. Select audio file (mp3, wav)
2. Send message
3. Audio player appears
4. Click play to listen

### Test Document
1. Select PDF or document
2. Send message
3. Download link appears
4. Click to download

---

## 🐛 Troubleshooting

### "Failed to upload file"
- Check file size (< 50MB)
- Verify file type is allowed
- Ensure you're logged in
- Check server is running

### File not displaying
- Check file extension matches type
- Verify file uploaded successfully
- Refresh the page
- Check browser console for errors

### Video won't play
- Browser may not support codec
- Try different video format
- Check file isn't corrupted

### Audio won't play
- Browser may not support format
- Try MP3 format (most compatible)

---

## 📱 Browser Compatibility

**Fully Supported:**
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

**File Types:**
- Images: All browsers
- MP4 videos: All browsers
- MP3 audio: All browsers
- PDF inline: Chrome, Edge, Firefox

---

## 🚀 Performance Tips

1. **Compress large files** before upload
2. **Use web-optimized formats:**
   - Images: JPEG/PNG
   - Video: MP4/H.264
   - Audio: MP3
3. **Limit video resolution** to 1080p max
4. **Use appropriate quality** for purpose

---

## 📝 Database Schema

**`admin_messages` table includes:**
```sql
file_url      TEXT      -- /api/files/<uuid>
file_name     TEXT      -- original filename
file_size     INTEGER   -- bytes
```

---

## ✅ Summary

**File upload is fully integrated and working!**

✅ Upload any supported file type  
✅ Inline preview for media files  
✅ Download links for documents  
✅ File metadata stored in messages  
✅ Unique filenames prevent conflicts  
✅ 50MB size limit enforced  
✅ Secure file handling  

**Just click 📎 and start sharing files!** 🚀
