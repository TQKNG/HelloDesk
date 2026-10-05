create table public.ride_requests (
  id uuid primary key default extensions.gen_random_uuid(),
  session_id uuid not null references public.guest_sessions(id) on delete restrict,
  destination_id text not null,
  destination_label text not null,
  status text not null default 'pending',
  provider_reference text null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint ride_requests_destination_id_not_empty check (char_length(destination_id) > 0),
  constraint ride_requests_destination_label_not_empty check (char_length(destination_label) > 0),
  constraint ride_requests_status_check check (
    status in ('pending', 'simulated', 'unavailable', 'failed', 'cancelled')
  )
);
comment on table public.ride_requests is 'A guest-confirmed simulated ride request.';
comment on column public.ride_requests.id is 'Primary key.';
comment on column public.ride_requests.session_id is 'References the guest session.';
comment on column public.ride_requests.destination_id is 'Identifies a configured demo destination selected and confirmed by the guest.';
comment on column public.ride_requests.destination_label is 'Guest-visible destination label copied from configuration.';
comment on column public.ride_requests.provider_reference is 'Uber sandbox identifier; server-side only.';
comment on column public.ride_requests.status is 'pending, simulated, unavailable, failed, or cancelled.';
comment on column public.ride_requests.created_at is 'Server managed.';
comment on column public.ride_requests.updated_at is 'Server managed.';
create index ride_requests_session_created_at_idx on public.ride_requests (session_id, created_at desc);
create trigger ride_requests_set_updated_at before update on public.ride_requests for each row execute function public.set_updated_at();
alter table public.ride_requests enable row level security;
alter table public.ride_requests force row level security;
revoke all on public.ride_requests from anon, authenticated;
grant select on public.ride_requests to authenticated;
grant select, insert, update, delete on public.ride_requests to service_role;
create policy "guests read their own ride requests"
  on public.ride_requests for select to authenticated
  using (public.has_active_guest_session(session_id));
create policy "service_role manages ride requests" on public.ride_requests for all to service_role using (true) with check (true);
