# MecGuraServe - Production Deployment Guide

## Hosting Options

### Option 1: Railway (Recommended - Easiest)
- Free tier available
- Auto-scaling
- Built-in PostgreSQL & Redis
- Custom domain support

### Option 2: DigitalOcean App Platform
- $12-24/month
- Good performance
- Easy setup

### Option 3: VPS (Full Control)
- $5-20/month
- Full control
- Requires server management knowledge

---

## Option 1: Railway Deployment (Recommended)

### Step 1: Create Railway Account
1. Go to https://railway.app
2. Sign up with GitHub

### Step 2: Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub Repo"
3. Select your mecguraserve repository

### Step 3: Add Services
1. Click "New" → "Database" → "PostgreSQL"
2. Click "New" → "Redis"

### Step 4: Configure Environment Variables
Go to Settings → Variables and add:
```
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=mecguraserve.com,*.mecguraserve.com,localhost
RAZORPAY_KEY_ID=rzp_live_xxxxx
RAZORPAY_KEY_SECRET=xxxxx
WHATSAPP_TOKEN=your-whatsapp-token
WHATSAPP_PHONE_ID=your-phone-id
```

### Step 5: Custom Domain
1. Go to Settings → Networking
2. Add Domain: mecguraserve.com
3. Add Wildcard: *.mecguraserve.com
4. Update DNS records as shown

---

## Option 2: DigitalOcean App Platform

### Step 1: Create App
1. Go to https://cloud.digitalocean.com/apps
2. Click "Create App"
3. Connect GitHub repository

### Step 2: Add Components
1. Add Database (PostgreSQL)
2. Add Redis

### Step 3: Configure
- Build Command: `pip install -r requirements-prod.txt`
- Run Command: `gunicorn --config gunicorn.conf.py mecguraserve.asgi:application`
- Add environment variables

---

## Option 3: VPS Deployment (Ubuntu/Debian)

### Step 1: Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install packages
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib redis-server certbot python3-certbot-nginx

# Create app directory
sudo mkdir -p /var/www/mecguraserve
sudo chown $USER:$USER /var/www/mecguraserve
```

### Step 2: Upload Project
```bash
# Copy project files
scp -r ./* user@server:/var/www/mecguraserve/

# Or use git
cd /var/www/mecguraserve
git clone https://github.com/yourrepo/mecguraserve.git .
```

### Step 3: Setup Environment
```bash
cd /var/www/mecguraserve

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements-prod.txt

# Setup environment
cp .env.example .env
nano .env  # Edit with production values
```

### Step 4: Setup Database
```bash
# Create PostgreSQL database
sudo -u postgres psql
CREATE USER mecguraserve WITH PASSWORD 'your_password';
CREATE DATABASE mecguraserve OWNER mecguraserve;
ALTER USER mecguraserve CREATEDB;
\q

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Step 5: Setup Nginx
```bash
# Create Nginx config
sudo nano /etc/nginx/sites-available/mecguraserve
```

Add this config:
```nginx
server {
    listen 80;
    server_name mecguraserve.com *.mecguraserve.com;

    location /static/ {
        alias /var/www/mecguraserve/staticfiles/;
    }

    location /media/ {
        alias /var/www/mecguraserve/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/mecguraserve /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

### Step 6: Setup SSL
```bash
sudo certbot --nginx -d mecguraserve.com -d *.mecguraserve.com
```

### Step 7: Setup Gunicorn
```bash
# Test Gunicorn
gunicorn --bind 0.0.0.0:8000 mecguraserve.asgi:application -k uvicorn.workers.UvicornWorker
```

### Step 8: Setup Systemd Service
```bash
sudo nano /etc/systemd/system/mecguraserve.service
```

Add:
```ini
[Unit]
Description=MecGuraServe Django Application
After=network.target postgresql.service redis.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/mecguraserve
ExecStart=/var/www/mecguraserve/venv/bin/gunicorn --config gunicorn.conf.py mecguraserve.asgi:application
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable mecguraserve
sudo systemctl start mecguraserve
```

---

## DNS Configuration

### For MecGuraServe Domain
Add these DNS records:
```
Type    Name                    Value
A       mecguraserve.com        your-server-ip
A       *.mecguraserve.com      your-server-ip
CNAME   www                     mecguraserve.com
```

### Resort Subdomains
Once wildcard DNS is set up, resort subdomains work automatically:
- grand-resort.mecguraserve.com
- lake-view.mecguraserve.com

---

## Post-Deployment Checklist

1. [ ] Domain DNS configured
2. [ ] SSL certificate installed
3. [ ] Environment variables set
4. [ ] Database migrated
5. [ ] Superuser created
6. [ ] Static files collected
7. [ ] Razorpay live keys configured
8. [ ] WhatsApp API configured
9. [ ] Test admin login
10. [ ] Test customer flow
11. [ ] Test payment flow

---

## Cost Estimate

### Railway (Recommended for Start)
- Starter Plan: $5/month
- PostgreSQL: $1/month
- Redis: $1/month
- Domain: ~$10/year
- **Total: ~$7-8/month**

### DigitalOcean App Platform
- Basic App: $12/month
- PostgreSQL: $15/month
- Redis: $15/month
- **Total: ~$42/month**

### VPS (Full Control)
- Droplet (2GB): $12/month
- PostgreSQL: Free (self-hosted)
- Redis: Free (self-hosted)
- Domain: ~$10/year
- **Total: ~$12-15/month**

---

## Scaling

### For 10-50 Resorts
- Use Railway or DigitalOcean App Platform
- Auto-scaling handles traffic spikes
- Managed database for reliability

### For 50-100 Resorts
- Upgrade to larger instance
- Add read replicas for database
- Use CDN for static files

### For 100+ Resorts
- Consider dedicated servers
- Implement caching layers
- Use load balancers

---

## Support

For deployment issues:
1. Check application logs
2. Verify environment variables
3. Test database connection
4. Check DNS resolution
5. Verify SSL certificate

---

**Last Updated:** September 2026
**Version:** 1.0.0
