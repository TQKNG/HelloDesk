-- Pending actions make an untrusted model or browser request reviewable before it changes state.

create table public.pending_actions (
  id uuid primary key default extensions.gen_random_uuid(),
  session_id uuid not null references public.guest_sessions(id) on delete restrict,
  kind text not null,
  summary text not null,
  details jsonb not null,
  status text not null default 'pending',
  expires_at timestamptz not null,
  request_id uuid null,
  constraint pending_actions_kind_check check (kind in ('check_in', 'check_out', 'staff_help', 'uber_ride')),
  constraint pending_actions_summary_not_empty check (char_length(summary) > 0),
  constraint pending_actions_details_object_check check (jsonb_typeof(details) = 'object'),
  constraint pending_actions_status_check check (status in ('pending', 'confirmed', 'cancelled', 'expired', 'failed'))
);

comment on table public.pending_actions is
  'A server-side proposal requiring an explicit guest decision before a write is committed.';
comment on column public.pending_actions.id is
  'Unique action identifier shown to the client as opaque.';
comment on column public.pending_actions.session_id is
  'References the creating guest session.';
comment on column public.pending_actions.kind is
  'check_in, check_out, staff_help, or uber_ride.';
comment on column public.pending_actions.summary is
  'Human-readable, localized details shown and spoken before confirmation.';
comment on column public.pending_actions.details is
  'Validated server-side, action-specific data; never trusted from the model alone.';
comment on column public.pending_actions.status is
  'pending, confirmed, cancelled, expired, or failed.';
comment on column public.pending_actions.expires_at is
  'Short-lived; confirmation after expiry is rejected.';
comment on column public.pending_actions.request_id is
  'Idempotency key for a commit attempt.';

create index pending_actions_session_status_expires_at_idx
  on public.pending_actions (session_id, status, expires_at);

create unique index pending_actions_request_id_key
  on public.pending_actions (request_id)
  where request_id is not null;

alter table public.pending_actions enable row level security;
alter table public.pending_actions force row level security;

revoke all on table public.pending_actions from anon, authenticated;
grant select, insert, update, delete on table public.pending_actions to service_role;

create policy "service_role manages pending actions"
  on public.pending_actions
  for all
  to service_role
  using (true)
  with check (true);
