# 🚀 Quick Deploy Commands

**Copy and paste these commands in order!**

---

## Step 1: Git Setup

```bash
# Navigate to ChatApp
cd C:\Users\trabc\CascadeProjects\ChatApp

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Ready for Railway deployment"
```

---

## Step 2: Generate Secrets

```bash
# Generate SECRET_KEY
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# Generate JWT_SECRET
python -c "import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(32))"
```

**Copy these outputs!** You'll need them for Railway environment variables.

---

## Step 3: Create GitHub Repo

1. Go to: https://github.com/new
2. Name: **ChatApp**
3. Privacy: **Private**
4. Click **"Create Repository"**

---

## Step 4: Push to GitHub

**Replace YOUR_USERNAME with your GitHub username:**

```bash
git remote add origin https://github.com/YOUR_USERNAME/ChatApp.git
git branch -M main
git push -u origin main
```

---

## Step 5: Railway Deployment

1. Go to: https://railway.app/new
2. Click **"Deploy from GitHub repo"**
3. Select **ChatApp**
4. Click **"Deploy"**

---

## Step 6: Add PostgreSQL

1. In Railway project, click **"New"**
2. Select **"Database"** → **"PostgreSQL"**
3. Done! (Railway auto-links it)

---

## Step 7: Add Environment Variables

In Railway → Your Service → Variables tab, add:

```
SECRET_KEY=<paste-from-step-2>
JWT_SECRET=<paste-from-step-2>
DISABLE_AUTO_DOCS=true
```

**If keeping AI (for now):**
```
OPENAI_API_KEY=<your-key>
ANTHROPIC_API_KEY=<your-key>
GOOGLE_API_KEY=<your-key>
GROK_API_KEY=<your-key>
```

---

## Step 8: Generate Domain

1. Go to **Settings** → **Domains**
2. Click **"Generate Domain"**
3. Copy your URL: `https://chatapp-production-xxxx.up.railway.app`

---

## ✅ Done!

Visit your URL and test:
- [ ] Homepage loads
- [ ] Can signup/login
- [ ] Can send messages

---

## 🔄 To Update Later

```bash
# Make changes
# Then:
git add .
git commit -m "Update: description of changes"
git push

# Railway auto-deploys! 🚀
```

---

## 📞 Need Help?

Read full guide: `RAILWAY_DEPLOYMENT_GUIDE.md`

Or ask me! 💬
