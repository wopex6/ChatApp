# 🧪 Test Voice Calls: Windows + Mac on Same WiFi

## ✅ **Yes! This is the BEST way to test!**

Your Windows PC IP: **192.168.0.214**

---

## 🚀 **Quick Start Guide**

### **On Windows (Server/Admin):**

1. **Restart server:**
   ```bash
   python chatapp_simple.py
   ```

2. **Open browser:** `http://localhost:5001`

3. **Login as Ken Tse**

---

### **On Mac (Client/User):**

1. **Open browser:** `http://192.168.0.214:5001`

2. **Sign up** as a new user (e.g., "testuser")

3. **Login** with your new account

---

## 📞 **Test Calls**

### **Test 1: Mac → Windows (User calls Admin)**

**On Mac:** Click **📞 Call** button → Allow microphone  
**On Windows:** Incoming call popup → Click **📞 Answer** → Allow microphone  
**Result:** Connected! Can talk!

### **Test 2: Windows → Mac (Admin calls User)**

**On Windows:** Click **📞** next to user in list  
**On Mac:** Incoming call popup → Click **📞 Answer**  
**Result:** Connected!

---

## 🔥 **Firewall Issue?**

If Mac can't connect, run this on **Windows** (as Administrator):

```powershell
netsh advfirewall firewall add rule name="Flask App" dir=in action=allow protocol=TCP localport=5001
```

---

## ✅ **What to Expect**

- ✅ Both can hear each other
- ✅ Timer counts up during call
- ✅ Mute button works
- ✅ Hang up ends call
- ✅ Missed calls are logged
- ✅ Status indicators update (online/offline/in call)

---

**Server is now configured to accept connections from your Mac!** 🎉

Just restart the server and try it!
