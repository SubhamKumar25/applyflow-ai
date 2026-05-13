// Optional MongoDB initialization script.
// Run with: docker exec -i applyflow-mongo mongosh < database/init-mongo.js
// Or mount into /docker-entrypoint-initdb.d/ in docker-compose if you want
// it to run automatically on first container start.

db = db.getSiblingDB('applyflow_ai');

// Useful indexes
db.users.createIndex({ email: 1 }, { unique: true });
db.resumes.createIndex({ user_id: 1, uploaded_at: -1 });
db.resumes.createIndex({ user_id: 1, is_active: 1 });
db.applications.createIndex({ user_id: 1, applied_at: -1 });
db.applications.createIndex({ user_id: 1, status: 1 });
db.applications.createIndex({ user_id: 1, platform: 1 });
db.logs.createIndex({ user_id: 1, timestamp: -1 });

print('ApplyFlow AI indexes created');
