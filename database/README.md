# Database

MongoDB collections used by ApplyFlow AI:

| Collection | Purpose | Indexes |
|---|---|---|
| `users` | User accounts (`email`, `hashed_password`, `settings`) | `email` (unique) |
| `resumes` | Uploaded resumes + AI analysis | `user_id + uploaded_at`, `user_id + is_active` |
| `applications` | Application history (status, platform, AI answers) | `user_id + applied_at`, `user_id + status`, `user_id + platform` |
| `logs` | Activity log entries (optional) | `user_id + timestamp` |

## Initialization

Indexes are created automatically the first time the app writes to a collection,
but you can pre-create them for production by running:

```bash
docker exec -i applyflow-mongo mongosh < database/init-mongo.js
```

## Backups

See [`docs/DEPLOYMENT.md`](../docs/DEPLOYMENT.md) for backup / restore commands.
