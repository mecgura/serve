#!/bin/bash

# MecGuraServe Deployment Script
# Run this on your Ubuntu/Debian server

set -e

echo "🚀 Starting MecGuraServe deployment..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx redis-server postgresql postgresql-contrib

# Create deployment directory
sudo mkdir -p /var/www/mecguraserve
sudo chown $USER:$USER /var/www/mecguraserve

# Copy project files
cp -r . /var/www/mecguraserve/
cd /var/www/mecguraserve

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements-prod.txt

# Setup environment variables
cp .env.example .env
echo "⚠️  Please edit .env file with your production settings!"

# Create logs directory
mkdir -p logs

# Setup PostgreSQL database
sudo -u postgres psql -c "CREATE USER mecguraserve WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "CREATE DATABASE mecguraserve OWNER mecguraserve;"
sudo -u postgres psql -c "ALTER USER mecguraserve CREATEDB;"

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
echo "Creating superuser..."
python manage.py createsuperuser

# Setup Nginx
sudo cp nginx.conf /etc/nginx/sites-available/mecguraserve
sudo ln -sf /etc/nginx/sites-available/mecguraserve /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

# Setup SSL with Certbot
sudo certbot --nginx -d mecguraserve.com -d *.mecguraserve.com

# Setup systemd service
sudo tee /etc/systemd/system/mecguraserve.service > /dev/null <<EOF
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
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable mecguraserve
sudo systemctl start mecguraserve

# Setup auto-renewal for SSL
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

echo "✅ Deployment complete!"
echo "🌐 Your site is live at https://mecguraserve.com"
echo ""
echo "Next steps:"
echo "1. Edit /var/www/mecguraserve/.env with production values"
echo "2. Configure Razorpay production keys"
echo "3. Setup WhatsApp Business API"
echo "4. Test all functionality"
