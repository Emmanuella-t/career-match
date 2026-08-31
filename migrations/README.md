# Database migrations

Career Match uses provider-neutral PostgreSQL migrations for authenticated
persistence (Neon in production).

## Apply the schema

### Option A — Neon SQL Editor

1. Open your Neon project → **SQL Editor**
2. Paste and run `0001_initial_persistence.sql`

### Option B — psql

```bash
psql "$DATABASE_URL" -f migrations/0001_initial_persistence.sql
```

## Backend environment

Set on the FastAPI host only (see root `.env.example`):

```bash
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
CLERK_ISSUER=https://your-instance.clerk.accounts.dev
```

Neon may scale compute to zero when idle. The API uses SQLAlchemy
`pool_pre_ping=True` so stale connections are detected after a cold start.

Never expose `DATABASE_URL` to the Next.js client.
