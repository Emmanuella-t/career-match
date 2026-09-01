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
for optional Postgres-backed job discovery. When `ADZUNA_APP_ID` and
`ADZUNA_APP_KEY` are configured, live listings come from Adzuna during search
(ephemeral — not written to this table). The catalog remains available for synced
or seeded jobs; user bookmarks stay in `saved_jobs`.

## Backend environment

Set on the FastAPI host only (see root `.env.example`):

```bash
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
CLERK_ISSUER=https://your-instance.clerk.accounts.dev
```

Neon may scale compute to zero when idle. The API uses SQLAlchemy
`pool_pre_ping=True` so stale connections are detected after a cold start.

Never expose `DATABASE_URL` to the Next.js client.

## Optional Clerk JWKS override

If your Clerk instance requires a custom JWKS URL:

```bash
CLERK_JWKS_URL=https://your-instance.clerk.accounts.dev/.well-known/jwks.json
```

## Deploy order

1. Run migrations (`0001`, then `0002`)
2. Set `DATABASE_URL` and `CLERK_ISSUER` on the API host
3. Deploy the FastAPI service
4. Deploy the Next.js frontend with Clerk keys and `NEXT_PUBLIC_API_URL`
