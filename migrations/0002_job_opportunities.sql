-- Career Match discoverable job opportunities (provider-neutral catalog).
--
-- This table stores available job postings ingested from external providers.
-- It is separate from saved_jobs (user-curated bookmarks).
--
-- Apply after 0001_initial_persistence.sql:
--   psql "$DATABASE_URL" -f migrations/0002_job_opportunities.sql
--
-- Production starts empty until a real job provider sync is configured.
-- Do not seed fake production jobs.

-- ---------------------------------------------------------------------------
-- job_opportunities
-- ---------------------------------------------------------------------------
create table if not exists public.job_opportunities (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  company text,
  location text,
  description text not null,
  source text not null,
  source_url text,
  apply_url text,
  employment_type text,
  external_id text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint job_opportunities_title_not_blank check (char_length(trim(title)) > 0),
  constraint job_opportunities_description_not_blank
    check (char_length(trim(description)) > 0),
  constraint job_opportunities_source_not_blank check (char_length(trim(source)) > 0)
);

create unique index if not exists job_opportunities_source_external_id_idx
  on public.job_opportunities (source, external_id)
  where external_id is not null;

create index if not exists job_opportunities_source_idx
  on public.job_opportunities (source);

create index if not exists job_opportunities_location_idx
  on public.job_opportunities (location);

create index if not exists job_opportunities_employment_type_idx
  on public.job_opportunities (employment_type);

create index if not exists job_opportunities_updated_at_idx
  on public.job_opportunities (updated_at desc);

drop trigger if exists job_opportunities_set_updated_at on public.job_opportunities;
create trigger job_opportunities_set_updated_at
  before update on public.job_opportunities
  for each row execute function public.set_updated_at();
