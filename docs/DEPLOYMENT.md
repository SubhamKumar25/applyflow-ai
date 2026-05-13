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

---

## Vercel (frontend) + Render (API) + MongoDB Atlas (free)

This stack works without a VPS: the React app on Vercel calls a long-running FastAPI container on Render. Playwright runs inside the API container (same as Docker Compose).

### 1. MongoDB Atlas

1. Create a free cluster at [https://www.mongodb.com/atlas](https://www.mongodb.com/atlas).
2. Database Access: add a user + password.
3. Network Access: allow `0.0.0.0/0` for development (tighten to Render egress IPs for production).
4. Connect → Drivers → copy the SRV connection string, e.g. `mongodb+srv://USER:PASS@cluster.../applyflow_ai?retryWrites=true&w=majority`.

### 2. Render (backend)

1. Push this repo to GitHub.
2. In Render: **New +** → **Blueprint** (or **Web Service** from repo).
3. If using the included `render.yaml`, set **sync: false** secrets in the dashboard: `MONGODB_URL`, `OPENAI_API_KEY` (and optional `JWT_SECRET_KEY` if you do not want a generated value).
4. Add environment variables:
   - `MONGODB_URL` — Atlas URI
   - `JWT_SECRET_KEY` — long random string (`python -c "import secrets; print(secrets.token_urlsafe(48))"`)
   - `OPENAI_API_KEY` or `GEMINI_API_KEY` / `AI_PROVIDER`
   - `CORS_ORIGINS` — your Vercel URL, e.g. `https://your-app.vercel.app` (no trailing slash). Comma-separate multiple origins.
5. Deploy. Note the public URL, e.g. `https://applyflow-api.onrender.com`.

Render free tier sleeps after inactivity; first request after sleep can take ~30–60s.

### 3. Vercel (frontend)

1. Import the GitHub repo in Vercel.
2. Set **Root Directory** to `frontend`.
3. Build: default `npm run build`, output `dist`.
4. Environment variable: `VITE_API_URL` = your Render API URL (e.g. `https://applyflow-api.onrender.com`) with **no** `/api` suffix unless you put the API behind that path.

### 4. GitHub

Commit and push to your account. Connect Vercel and Render to the same repository; redeploy when you merge to `main`.

### 5. Production notes

- **Resume uploads** on Render use ephemeral disk unless you attach a persistent disk or switch to S3-style storage.
- Set `SCHEDULER_ENABLED=true` on Render only if you want the daily automation cron; keep `SCHEDULER_CRON_*` in UTC.
- Never commit real `.env` files; use host dashboards for secrets.
