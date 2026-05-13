# Deployment Guide

## Production deployment with Docker Compose

### 1. Provision a VPS
Any Linux VPS with ≥2 vCPU, 4 GB RAM, 30 GB disk works (DigitalOcean, Linode, Hetzner, AWS EC2 t3.medium).

### 2. Install Docker
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```
Log out / back in.

### 3. Clone & configure
```bash
git clone https://github.com/SubhamKumar25/applyflow-ai.git
cd applyflow-ai
cp .env.example .env
nano .env  # fill in real values
```

**Critical variables to change in production:**
- `SECRET_KEY` — random 32+ chars
- `JWT_SECRET_KEY` — random 32+ chars
- `MONGODB_URL` — use authenticated connection string if Mongo is exposed
- `OPENAI_API_KEY` / `GEMINI_API_KEY`
- `PLAYWRIGHT_HEADLESS=true`

Generate a secret:
```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

### 4. Bring it up
```bash
docker compose up -d --build
docker compose logs -f
```

### 5. Reverse proxy with Nginx + HTTPS

Create `/etc/nginx/sites-available/applyflow`:
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    client_max_body_size 20M;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Then:
```bash
sudo ln -s /etc/nginx/sites-available/applyflow /etc/nginx/sites-enabled/
sudo certbot --nginx -d yourdomain.com
sudo systemctl reload nginx
```

### 6. Backups
MongoDB lives in the `mongo_data` volume:
```bash
docker exec applyflow-mongo mongodump --archive --gzip > backup-$(date +%F).gz
```
Restore:
```bash
docker exec -i applyflow-mongo mongorestore --archive --gzip < backup.gz
```

### 7. Updates
```bash
git pull
docker compose up -d --build
```

### 8. Monitoring
- `docker compose logs -f backend` — application logs
- `docker stats` — resource usage
- Consider Uptime Kuma or Prometheus + Grafana for production

---

## Scaling considerations

- **Backend**: Stateless — scale horizontally behind a load balancer
- **Playwright**: CPU-bound. Move scraping/applying into a separate worker container (Celery / RQ) for high throughput
- **MongoDB**: Use a managed service (Atlas) past ~10K users
- **AI calls**: Cache resume analysis (already keyed on user_id + resume hash)
