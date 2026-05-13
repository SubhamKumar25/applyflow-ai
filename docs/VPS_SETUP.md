# Ubuntu VPS — Step-by-step

Tested on Ubuntu 22.04 LTS.

## 1. Initial server hardening

```bash
# As root
adduser deploy
usermod -aG sudo deploy
rsync --archive --chown=deploy:deploy ~/.ssh /home/deploy
```

Edit `/etc/ssh/sshd_config`:
```
PermitRootLogin no
PasswordAuthentication no
```
```bash
systemctl restart sshd
```

UFW:
```bash
ufw default deny incoming
ufw default allow outgoing
ufw allow OpenSSH
ufw allow 80,443/tcp
ufw enable
```

## 2. Install deps

```bash
sudo apt update && sudo apt -y upgrade
sudo apt install -y curl git nginx certbot python3-certbot-nginx
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker deploy
```
Log out & back in.

## 3. DNS

Point `A` record `yourdomain.com` → server IP.

## 4. Clone + deploy

```bash
cd /opt
sudo git clone https://github.com/SubhamKumar25/applyflow-ai.git
sudo chown -R deploy:deploy applyflow-ai
cd applyflow-ai
cp .env.example .env
nano .env  # fill values
docker compose up -d --build
```

## 5. HTTPS

```bash
sudo cp docs/nginx-prod.conf /etc/nginx/sites-available/applyflow
sudo ln -s /etc/nginx/sites-available/applyflow /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d yourdomain.com
```

## 6. Auto-update systemd timer (optional)

```bash
sudo tee /etc/systemd/system/applyflow-update.service > /dev/null <<EOF
[Unit]
Description=ApplyFlow daily git pull + rebuild

[Service]
Type=oneshot
WorkingDirectory=/opt/applyflow-ai
User=deploy
ExecStart=/bin/bash -c 'git pull && docker compose up -d --build'
EOF

sudo tee /etc/systemd/system/applyflow-update.timer > /dev/null <<EOF
[Unit]
Description=Run ApplyFlow update daily

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now applyflow-update.timer
```

## 7. Logs

```bash
docker compose logs -f backend
journalctl -u nginx -f
```

## 8. Backup cron

```bash
crontab -e
# Add:
0 3 * * * docker exec applyflow-mongo mongodump --archive --gzip > /opt/backups/applyflow-$(date +\%F).gz
```
