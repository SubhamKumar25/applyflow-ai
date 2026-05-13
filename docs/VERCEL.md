# Vercel (frontend live) + Google Sign-In

## 1. Google Cloud Console

1. Open [Google Cloud Console](https://console.cloud.google.com/) → create or pick a project.
2. **APIs & Services** → **OAuth consent screen** → External → fill app name, support email, save.
3. **Credentials** → **Create credentials** → **OAuth client ID** → type **Web application**.
4. **Authorized JavaScript origins** (add all you use):
   - `http://localhost:5173`
   - `https://YOUR-PROJECT.vercel.app` (after first Vercel deploy, copy exact URL)
5. **Authorized redirect URIs** — for this app (GIS button) you often only need origins above; if Google asks for redirect, add `https://YOUR-PROJECT.vercel.app` and `http://localhost:5173`.
6. Copy the **Client ID** (ends with `.apps.googleusercontent.com`).

Same Client ID string must be set in **two** places:

| Where | Variable |
|--------|----------|
| Vercel (frontend build) | `VITE_GOOGLE_CLIENT_ID` |
| Render / your API server | `GOOGLE_CLIENT_ID` |

Backend verifies the Google ID token with this audience (`aud`).

---

## 2. Vercel — site live

1. [vercel.com](https://vercel.com) → **Add New** → **Project** → import GitHub repo `applyflow-ai`.
2. **Root Directory**: `frontend`
3. **Framework Preset**: Vite  
4. **Environment Variables** (Production + Preview):
   - `VITE_API_URL` = your API URL, e.g. `https://applyflow-api.onrender.com` (no trailing slash; no `/api` unless you use a proxy).
   - `VITE_GOOGLE_CLIENT_ID` = the Web client ID from step 1.
5. **Deploy**.

After deploy, add the production URL to Google Console **Authorized JavaScript origins** if you did not already, then redeploy or wait for cache — Google is strict about origin match.

---

## 3. Backend (Render) — Google env

In Render dashboard for the API service, add:

- `GOOGLE_CLIENT_ID` = same value as `VITE_GOOGLE_CLIENT_ID`
- `CORS_ORIGINS` = `https://YOUR-PROJECT.vercel.app` (comma-separated if multiple)

Redeploy the API after saving env.

---

## 4. GitHub PR

```bash
git checkout -b feature/google-oauth
git add -A
git commit -m "feat: Google Sign-In + Vercel env docs"
git push -u origin feature/google-oauth
```

Then on GitHub: **Compare & pull request** → merge into `main`. Vercel can auto-deploy from `main` if connected.

---

## 5. Local test

`frontend/.env.local`:

```
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
```

`backend/.env`:

```
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
```

Run API + `npm run dev`, open Login → **Sign in with Google**.

---

## Hindi (संक्षेप)

1. Google Cloud में **OAuth Web client** बनाएं; **JavaScript origins** में `localhost:5173` और Vercel URL डालें।  
2. **Client ID** को Vercel में `VITE_GOOGLE_CLIENT_ID` और Render में `GOOGLE_CLIENT_ID` दोनों में same डालें।  
3. Vercel पर project का **Root Directory** = `frontend`, `VITE_API_URL` = backend URL।  
4. Render पर `CORS_ORIGINS` = Vercel का `https://...` URL।  
5. GitHub पर branch push करके **Pull Request** बनाएं और merge करें।
