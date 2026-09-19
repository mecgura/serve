#!/bin/bash
# MecGuraServe - remote deploy script.
# Runs ON THE VPS itself (over SSH, invoked by .github/workflows/deploy.yml).
set -e

APP_DIR=/var/www/mecguraserve
REPO_URL=https://github.com/mecgura/serve.git
BRANCH=main
PORT=8000
SERVER_IP=194.238.19.193

echo "=== Preparing app directory ==="
mkdir -p "$APP_DIR"

if [ ! -d "$APP_DIR/.git" ]; then
  git clone "$REPO_URL" "$APP_DIR"
fi

cd "$APP_DIR"
git fetch origin "$BRANCH"
git checkout "$BRANCH"
git reset --hard "origin/$BRANCH"

echo "=== Picking Python (Django 6 needs 3.12+) ==="
PYBIN=python3
PYOK=$(python3 -c 'import sys; print(1 if sys.version_info >= (3, 12) else 0)')
if [ "$PYOK" != "1" ]; then
  if ! command -v python3.12 >/dev/null 2>&1; then
    apt-get update -qq
    apt-get install -y -qq python3.12 python3.12-venv python3.12-dev || true
  fi
  if command -v python3.12 >/dev/null 2>&1; then
    PYBIN=python3.12
  fi
fi
if ! command -v nginx >/dev/null 2>&1; then
  apt-get update -qq
  apt-get install -y -qq nginx || true
fi
echo "Using: $($PYBIN --version)"

echo "=== Installing dependencies ==="
rm -rf venv
"$PYBIN" -m venv venv
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements-prod.txt

echo "=== Environment file ==="
if [ ! -f .env ]; then
  cp .env.example .env
  GENERATED_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
  sed -i "s#^SECRET_KEY=.*#SECRET_KEY=$GENERATED_SECRET#" .env
  sed -i "s#^DEBUG=.*#DEBUG=False#" .env
  sed -i "s#^ALLOWED_HOSTS=.*#ALLOWED_HOSTS=$SERVER_IP,localhost,127.0.0.1#" .env
  sed -i "s#^CSRF_TRUSTED_ORIGINS=.*#CSRF_TRUSTED_ORIGINS=http://$SERVER_IP#" .env
  echo "Fresh .env created. Edit Razorpay/WhatsApp keys later: nano $APP_DIR/.env"
fi

mkdir -p logs

echo "=== Django migrate + collectstatic ==="
python manage.py migrate --noinput
python manage.py collectstatic --noinput

echo "=== systemd service ==="
cat > /etc/systemd/system/mecguraserve.service <<UNIT
[Unit]
Description=MecGuraServe Django Application
After=network.target

[Service]
User=root
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 1 --config gunicorn.conf.py mecguraserve.asgi:application
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT
# NOTE: --workers 1 on purpose. CHANNEL_LAYERS uses InMemoryChannelLayer
# (settings.py), which does not share state across processes - more than
# one worker would break real-time kitchen/dashboard order updates.

systemctl daemon-reload
systemctl enable mecguraserve
systemctl restart mecguraserve
sleep 2
systemctl status mecguraserve --no-pager || true

echo "=== nginx reverse proxy ==="
if command -v nginx >/dev/null 2>&1; then
  cat > /etc/nginx/sites-available/mecguraserve <<NGINX
server {
    listen 80;
    server_name $SERVER_IP;

    location /static/ {
        alias $APP_DIR/staticfiles/;
    }

    location /media/ {
        alias $APP_DIR/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:$PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
NGINX
  ln -sf /etc/nginx/sites-available/mecguraserve /etc/nginx/sites-enabled/mecguraserve
  rm -f /etc/nginx/sites-enabled/default
  nginx -t
  systemctl enable nginx
  systemctl restart nginx
else
  echo "nginx not available - install manually: apt install -y nginx"
fi

echo "=== Done. Site should be live at http://$SERVER_IP/ ==="
