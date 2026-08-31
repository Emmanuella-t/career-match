# Database migrations

Career Match uses provider-neutral PostgreSQL migrations for authenticated
persistence (Neon in production).

## Apply the schema

### Option A — Neon SQL Editor

1. Open your Neon project → **SQL Editor**
2. Paste and run `0001_initial_persistence.sql`
3. Paste and run `0002_job_opportunities.sql` (job discovery catalog)

### Option B — psql

```bash
psql "$DATABASE_URL" -f migrations/0001_initial_persistence.sql
psql "$DATABASE_URL" -f migrations/0002_job_opportunities.sql
```

`0002_job_opportunities.sql` adds the provider-neutral `job_opportunities` catalog
for authenticated job discovery. The table starts empty in production until a real
job provider sync is configured.

## Backend environment

Set on the FastAPI host only (see root `.env.example`):

```bash
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
CLERK_ISSUER=https://your-instance.clerk.accounts.dev
```

Neon may scale compute to zero when idle. The API uses SQLAlchemy
`pool_pre_ping=True` so stale connections are detected after a cold start.

Never expose `DATABASE_URL` to the Next.js client.
