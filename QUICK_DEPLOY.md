# 🚀 Quick Deploy Guide - GetCirclo Integration

**Status**: ✅ JWT Token Verified | ✅ Server Running | ✅ Ready to Deploy

---

## ⚡ Quick Start Options

### Option 1: Local Testing with ngrok (5 minutes)

**Best for**: Testing before production deployment

#### Step 1: Install ngrok

```bash
# Mac
brew install ngrok

# Or download from: https://ngrok.com/download
```

#### Step 2: Start ngrok tunnel

```bash
# In a new terminal
ngrok http 8000

# You'll see output like:
# Forwarding   https://abc123.ngrok.io -> http://localhost:8000
```

#### Step 3: Copy the HTTPS URL and register agent

```bash
# Copy the ngrok HTTPS URL (e.g., https://abc123.ngrok.io)

# Set as environment variable
export AGENT_WEBHOOK_URL=https://abc123.ngrok.io/circlo-webhook/hook

# Register agent
cd /Users/em/web/ai-hackthon
source .venv/bin/activate
python scripts/register_circlo_agent.py
```

#### Step 4: Test in GetCirclo

1. Open GetCirclo app
2. Search for `@trendscout-ai`
3. Start chatting!

**Sample queries**:
- "Carikan produk elektronik terlaris"
- "Cari supplier tas di Jakarta"
- "Produk apa yang lagi trending?"

---

### Option 2: Production Deployment (30 minutes)

**Best for**: Long-term production use

#### Prerequisites

- VPS/Cloud server (DigitalOcean, AWS, GCP, etc)
- Domain name (optional but recommended)
- SSH access to server

#### Quick Steps

1. **Setup Server**
   ```bash
   # SSH into server
   ssh user@your-server-ip
   
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install requirements
   sudo apt install python3 python3-pip python3-venv nginx certbot -y
   ```

2. **Clone & Setup**
   ```bash
   # Clone repo
   git clone https://github.com/your-repo/ai-hackthon.git
   cd ai-hackthon
   
   # Create virtual environment
   python3 -m venv .venv
   source .venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Setup .env file
   nano .env
   # Copy your local .env content, then save
   ```

3. **Setup Systemd Service**
   ```bash
   sudo nano /etc/systemd/system/trendscout.service
   ```
   
   Paste:
   ```ini
   [Unit]
   Description=TrendScout AI Agent
   After=network.target

   [Service]
   Type=simple
   User=your-username
   WorkingDirectory=/home/your-username/ai-hackthon
   Environment="PATH=/home/your-username/ai-hackthon/.venv/bin"
   ExecStart=/home/your-username/ai-hackthon/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```
   
   Enable:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable trendscout
   sudo systemctl start trendscout
   sudo systemctl status trendscout
   ```

4. **Setup Nginx**
   ```bash
   sudo nano /etc/nginx/sites-available/trendscout
   ```
   
   Paste:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```
   
   Enable:
   ```bash
   sudo ln -s /etc/nginx/sites-available/trendscout /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

5. **Setup SSL**
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

6. **Register Agent**
   ```bash
   export AGENT_WEBHOOK_URL=https://your-domain.com/circlo-webhook/hook
   python scripts/register_circlo_agent.py
   ```

---

## 🧪 Current Status

```
✅ JWT Token: Valid and authenticated
✅ GetCirclo API: Accessible (20 users found)
✅ Local Server: Running on port 8000
✅ Webhook Endpoint: Active at /circlo-webhook/hook
✅ All Tests: Passed
```

---

## 📝 What You Need

### Already Have ✅
- [x] JWT Token (in .env)
- [x] Server code (ready)
- [x] Webhook endpoint (working)
- [x] Local testing (passed)

### Need to Choose ⚙️
- [ ] Deployment method (ngrok or production)
- [ ] Webhook URL (ngrok or domain)

---

## 🎯 Recommendation

**For immediate testing**: Use Option 1 (ngrok)
- ✅ Quick setup (5 minutes)
- ✅ Test full integration
- ✅ No server needed
- ✅ Free to use

**For production**: Use Option 2 (VPS)
- ✅ Permanent URL
- ✅ Professional setup
- ✅ Full control
- ✅ Better reliability

---

## ⚡ Ultra-Quick Start (With ngrok)

```bash
# 1. Install ngrok (one-time)
brew install ngrok

# 2. Start ngrok (new terminal)
ngrok http 8000

# 3. Register agent (copy ngrok URL first)
export AGENT_WEBHOOK_URL=https://YOUR-NGROK-URL.ngrok.io/circlo-webhook/hook
python scripts/register_circlo_agent.py

# 4. Chat with agent in GetCirclo app!
# Search: @trendscout-ai
```

---

## 🐛 Troubleshooting

### Issue: ngrok not installed
```bash
# Mac
brew install ngrok

# Or download from: https://ngrok.com/download
```

### Issue: Server not running
```bash
# Check if server is running
curl http://localhost:8000/health

# If not, start it
cd /Users/em/web/ai-hackthon
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Issue: Agent registration fails
```bash
# Check JWT token
grep GETCIRCLO_JWT_TOKEN .env

# Test connection
python scripts/test_getcirclo_connection.py

# Try registration with verbose output
python scripts/register_circlo_agent.py
```

---

## 📊 What Happens After Registration

1. **Agent Profile Created** on GetCirclo
   - Name: TrendScout AI
   - Username: @trendscout-ai
   - Niche: E-commerce & Business

2. **Users Can Chat** with agent
   - Search for `@trendscout-ai` in GetCirclo
   - Start conversation
   - Get intelligent responses

3. **Webhook Receives Messages**
   - GetCirclo forwards user messages
   - Your server processes them
   - Returns helpful responses

4. **Monitor Activity**
   ```bash
   # Watch logs
   tail -f logs/server.log
   
   # Look for:
   # [GetCirclo Webhook] Received message from user...
   # [GetCirclo Webhook] Intent: find_bestsellers
   # [GetCirclo Webhook] Generated response...
   ```

---

## ✅ Success Checklist

Before registering agent, verify:

- [ ] Server is running (`curl http://localhost:8000/health`)
- [ ] Webhook is accessible (`curl http://localhost:8000/circlo-webhook/webhook-info`)
- [ ] JWT token is valid (test passed ✅)
- [ ] You have webhook URL (ngrok or domain)
- [ ] AGENT_WEBHOOK_URL environment variable is set

After registration:

- [ ] Agent profile created (check script output)
- [ ] Can find @trendscout-ai in GetCirclo
- [ ] Can send test message
- [ ] Receive intelligent response
- [ ] Logs show webhook activity

---

## 🎉 You're Almost There!

**Current Status**: Everything is ready! Just need to:

1. **Install ngrok** (for quick testing)
   ```bash
   brew install ngrok
   ```

2. **Start ngrok**
   ```bash
   ngrok http 8000
   ```

3. **Register agent**
   ```bash
   export AGENT_WEBHOOK_URL=https://YOUR-NGROK-URL.ngrok.io/circlo-webhook/hook
   python scripts/register_circlo_agent.py
   ```

4. **Start chatting** in GetCirclo! 🚀

---

**Need Help?**

- Full guide: `DEPLOYMENT_GUIDE.md`
- Connection issues: `scripts/test_getcirclo_connection.py`
- Logs: `tail -f logs/server.log`

**🎊 Ready to deploy!**
