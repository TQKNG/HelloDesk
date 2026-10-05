create table public.help_requests (
  id uuid primary key default extensions.gen_random_uuid(),
  session_id uuid not null references public.guest_sessions(id) on delete restrict,
  reservation_id uuid null references public.reservations(id) on delete restrict,
  summary text not null check (char_length(summary) between 1 and 500),
  status text not null default 'pending' check (status in ('pending', 'acknowledged')),
  created_at timestamptz not null default now(),
  acknowledged_at timestamptz null
);
comment on table public.help_requests is 'A staff work item created from a guest-confirmed request.';
comment on column public.help_requests.id is 'Primary key.';
comment on column public.help_requests.session_id is 'References the guest interaction.';
comment on column public.help_requests.reservation_id is 'Linked only when available in the guest session.';
comment on column public.help_requests.summary is 'Guest-confirmed summary; do not store the full voice transcript.';
comment on column public.help_requests.status is 'pending or acknowledged.';
comment on column public.help_requests.created_at is 'Server managed.';
comment on column public.help_requests.acknowledged_at is 'Set when a staff member acknowledges.';

create function public.stamp_help_request_acknowledgement()
returns trigger
language plpgsql
set search_path = pg_catalog
as $$
begin
  if old.status = 'acknowledged' and new.status <> 'acknowledged' then
    raise exception 'Acknowledged help requests cannot be reopened';
  end if;
  if new.status = 'acknowledged' then
    new.acknowledged_at := coalesce(old.acknowledged_at, now());
  else
    new.acknowledged_at := null;
  end if;
  return new;
end;
$$;

create trigger help_requests_stamp_acknowledgement
  before update on public.help_requests
  for each row execute function public.stamp_help_request_acknowledgement();

create function public.has_active_guest_session(expected_session_id uuid)
returns boolean
language sql
stable
security definer
set search_path = public, pg_catalog
as $$
  select exists (
    select 1
    from public.guest_sessions
    where id = (nullif(current_setting('request.jwt.claims', true), '')::jsonb ->> 'guest_session_id')::uuid
      and id = expected_session_id
      and status = 'active'
      and expires_at > now()
  );
$$;

create function public.is_staff()
returns boolean
language sql
stable
set search_path = pg_catalog
as $$
  select coalesce(
    nullif(current_setting('request.jwt.claims', true), '')::jsonb #>> '{app_metadata,role}' = 'staff',
    false
  );
$$;

revoke all on function public.has_active_guest_session(uuid) from public;
revoke all on function public.is_staff() from public;
grant execute on function public.has_active_guest_session(uuid), public.is_staff() to authenticated;

alter table public.help_requests enable row level security;
alter table public.help_requests force row level security;
revoke all on public.help_requests from anon, authenticated;
grant select on public.help_requests to authenticated;
grant update (status) on public.help_requests to authenticated;
grant select, insert, update, delete on public.help_requests to service_role;
create policy "service_role manages help requests" on public.help_requests for all to service_role using (true) with check (true);
create policy "guests read their own help request status"
  on public.help_requests for select to authenticated
  using (public.has_active_guest_session(session_id));
create policy "staff can list help requests"
  on public.help_requests for select to authenticated
  using (public.is_staff());
create policy "staff can acknowledge help requests"
  on public.help_requests for update to authenticated
  using (public.is_staff())
  with check (public.is_staff());
