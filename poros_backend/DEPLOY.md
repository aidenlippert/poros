# Poros Protocol - Deployment Guide

## 🚀 Deploy to Railway

### Step 1: Push to GitHub

```bash
cd poros_backend
git init
git add .
git commit -m "Initial Poros Protocol backend"
git remote add origin https://github.com/yourusername/poros-protocol
git push -u origin main
```

### Step 2: Deploy on Railway

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose `poros-protocol` repo
5. Railway auto-detects and deploys!

### Step 3: Get Your Live URL

Railway gives you: `https://poros-backend.up.railway.app`

### Step 4: Test It

```bash
# Health check
curl https://poros-backend.up.railway.app/health

# Create user
curl -X POST https://poros-backend.up.railway.app/api/registry/users \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'
```

## 🔧 Environment Variables

Set these in Railway dashboard:

- `SECRET_KEY` - Generate with: `openssl rand -hex 32`
- `ENVIRONMENT` - Set to `production`
- `DATABASE_URL` - Railway auto-provides PostgreSQL

## 📊 Next Steps

Once deployed:

1. **Agent builders** can register agents pointing to YOUR live API
2. **Clients** can query your orchestrator
3. **You** control the ranking and make money!

---

**Your Poros Protocol is now LIVE! 🎉**
