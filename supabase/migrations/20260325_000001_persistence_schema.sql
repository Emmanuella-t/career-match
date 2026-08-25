-- Career Match authenticated persistence schema (Supabase Postgres).
-- Identity: Clerk user IDs (clerk_user_id). No passwords stored here.
-- Apply with the Supabase SQL editor or CLI:
--   supabase db push
--   or: psql "$DATABASE_URL" -f supabase/migrations/20260325_000001_persistence_schema.sql
--
-- App access uses the service-role key from the FastAPI backend only.
-- Row Level Security is enabled as defense-in-depth; service role bypasses RLS.
-- Never expose SUPABASE_SERVICE_ROLE_KEY to the Next.js client.

create extension if not exists "pgcrypto";

-- ---------------------------------------------------------------------------
-- user_profiles
-- ---------------------------------------------------------------------------
create table if not exists public.user_profiles (
  id uuid primary key default gen_random_uuid(),
  clerk_user_id text not null unique,
  email text,
  display_name text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists user_profiles_clerk_user_id_idx
  on public.user_profiles (clerk_user_id);

-- ---------------------------------------------------------------------------
-- resumes
-- ---------------------------------------------------------------------------
create table if not exists public.resumes (
  id uuid primary key default gen_random_uuid(),
  clerk_user_id text not null,
  name text not null,
  resume_text text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint resumes_name_not_blank check (char_length(trim(name)) > 0),
  constraint resumes_text_not_blank check (char_length(trim(resume_text)) > 0)
);

create index if not exists resumes_clerk_user_id_idx
  on public.resumes (clerk_user_id);

create index if not exists resumes_clerk_user_id_updated_at_idx
  on public.resumes (clerk_user_id, updated_at desc);

-- ---------------------------------------------------------------------------
-- match_analyses
-- ---------------------------------------------------------------------------
create table if not exists public.match_analyses (
  id uuid primary key default gen_random_uuid(),
  clerk_user_id text not null,
  resume_id uuid references public.resumes (id) on delete set null,
  job_title text,
  company text,
  job_description text not null,
  matcher text not null,
  matcher_version text,
  overall_score double precision not null,
  matched_skills jsonb not null default '[]'::jsonb,
  missing_skills jsonb not null default '[]'::jsonb,
  weak_or_negated_skills jsonb not null default '[]'::jsonb,
  semantic_score double precision,
  tfidf_score double precision,
  skill_overlap_score double precision,
  disclaimer text,
  created_at timestamptz not null default now(),
  constraint match_analyses_job_description_not_blank
    check (char_length(trim(job_description)) > 0)
);

create index if not exists match_analyses_clerk_user_id_idx
  on public.match_analyses (clerk_user_id);

create index if not exists match_analyses_clerk_user_id_created_at_idx
  on public.match_analyses (clerk_user_id, created_at desc);

-- ---------------------------------------------------------------------------
-- saved_jobs
-- ---------------------------------------------------------------------------
create table if not exists public.saved_jobs (
  id uuid primary key default gen_random_uuid(),
  clerk_user_id text not null,
  title text not null,
  company text,
  job_description text not null,
  source_url text,
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint saved_jobs_title_not_blank check (char_length(trim(title)) > 0),
  constraint saved_jobs_description_not_blank
    check (char_length(trim(job_description)) > 0)
);

create index if not exists saved_jobs_clerk_user_id_idx
  on public.saved_jobs (clerk_user_id);

create index if not exists saved_jobs_clerk_user_id_updated_at_idx
  on public.saved_jobs (clerk_user_id, updated_at desc);

-- ---------------------------------------------------------------------------
-- updated_at helper
-- ---------------------------------------------------------------------------
create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists user_profiles_set_updated_at on public.user_profiles;
create trigger user_profiles_set_updated_at
  before update on public.user_profiles
  for each row execute function public.set_updated_at();

drop trigger if exists resumes_set_updated_at on public.resumes;
create trigger resumes_set_updated_at
  before update on public.resumes
  for each row execute function public.set_updated_at();

drop trigger if exists saved_jobs_set_updated_at on public.saved_jobs;
create trigger saved_jobs_set_updated_at
  before update on public.saved_jobs
  for each row execute function public.set_updated_at();

-- ---------------------------------------------------------------------------
-- RLS (defense-in-depth; backend uses service role which bypasses RLS)
-- ---------------------------------------------------------------------------
alter table public.user_profiles enable row level security;
alter table public.resumes enable row level security;
alter table public.match_analyses enable row level security;
alter table public.saved_jobs enable row level security;

-- No policies for anon/authenticated roles: direct client access is denied.
-- All reads/writes go through FastAPI with a verified Clerk identity.
