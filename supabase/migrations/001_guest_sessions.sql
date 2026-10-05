-- Guest sessions are owned by the trusted FastAPI service.
-- The browser never receives a database credential or accesses this table directly.

create extension if not exists pgcrypto with schema extensions;

create table public.guest_sessions (
  id uuid primary key default extensions.gen_random_uuid(),
  token_hash text not null unique,
  language text not null,
  reservation_id uuid null,
  status text not null default 'active',
  created_at timestamptz not null default now(),
  expires_at timestamptz not null,
  constraint guest_sessions_token_hash_not_empty check (char_length(token_hash) > 0),
  constraint guest_sessions_language_check check (language in ('en', 'vi')),
  constraint guest_sessions_status_check check (status in ('active', 'ended', 'expired')),
  constraint guest_sessions_expires_after_creation_check check (expires_at > created_at)
);

comment on table public.guest_sessions is
  'An expiring interaction context for one kiosk guest.';
comment on column public.guest_sessions.id is
  'Internal primary key.';
comment on column public.guest_sessions.token_hash is
  'Unique hash of a random bearer token; return the raw token once and never persist it.';
comment on column public.guest_sessions.language is
  'en or vi, selected before the voice session.';
comment on column public.guest_sessions.reservation_id is
  'Set only after a valid reservation lookup and guest confirmation.';
comment on column public.guest_sessions.status is
  'active, ended, or expired.';
comment on column public.guest_sessions.created_at is
  'Server managed; expire on idle timeout or guest completion.';
comment on column public.guest_sessions.expires_at is
  'Server managed; expire on idle timeout or guest completion.';

create index guest_sessions_active_expires_at_idx
  on public.guest_sessions (expires_at)
  where status = 'active';

alter table public.guest_sessions enable row level security;
alter table public.guest_sessions force row level security;

revoke all on table public.guest_sessions from anon, authenticated;
grant select, insert, update, delete on table public.guest_sessions to service_role;

create policy "service_role manages guest sessions"
  on public.guest_sessions
  for all
  to service_role
  using (true)
  with check (true);
