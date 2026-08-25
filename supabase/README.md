# Supabase persistence

Career Match stores authenticated user data in Supabase Postgres.

- **Auth identity:** Clerk (`clerk_user_id`)
- **Access path:** FastAPI backend with `SUPABASE_SERVICE_ROLE_KEY`
- **Not used from the browser:** never put the service-role key in Next.js

## Apply the schema

### Option A — Supabase SQL editor

1. Open your project → SQL → New query
2. Paste and run `migrations/20260325_000001_persistence_schema.sql`

### Option B — Supabase CLI

```bash
supabase link --project-ref <your-project-ref>
supabase db push
```

### Option C — psql

```bash
psql "$DATABASE_URL" -f supabase/migrations/20260325_000001_persistence_schema.sql
```

## Backend environment

Set on the FastAPI host only (see root `.env.example`):

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
CLERK_ISSUER=https://your-instance.clerk.accounts.dev
```

`CLERK_ISSUER` is used to fetch JWKS and verify Bearer session tokens from the frontend.
