-- Synthetic reservation and bill data is accessible only through a session-scoped policy.
-- FastAPI remains the application boundary and uses the server-only service-role credential.

create table public.reservations (
  id uuid primary key default extensions.gen_random_uuid(),
  reservation_code text not null unique,
  guest_display_name text not null,
  arrival_date date not null,
  departure_date date not null,
  room_number text null,
  status text not null default 'reserved',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint reservations_code_not_empty check (char_length(reservation_code) > 0),
  constraint reservations_display_name_not_empty check (char_length(guest_display_name) > 0),
  constraint reservations_stay_dates_check check (departure_date > arrival_date),
  constraint reservations_room_after_check_in_check check (
    status not in ('checked_in', 'checked_out') or room_number is not null
  ),
  constraint reservations_status_check check (
    status in ('reserved', 'checked_in', 'checked_out', 'cancelled')
  )
);

comment on table public.reservations is
  'A synthetic hotel booking used by the demo.';
comment on column public.reservations.id is
  'Primary key.';
comment on column public.reservations.reservation_code is
  'Unique demo lookup code; never use a real guest code.';
comment on column public.reservations.guest_display_name is
  'Synthetic display name; reveal only after a successful lookup.';
comment on column public.reservations.arrival_date is
  'Required.';
comment on column public.reservations.departure_date is
  'Must be after arrival.';
comment on column public.reservations.room_number is
  'Required after check-in; not a door credential.';
comment on column public.reservations.status is
  'reserved, checked_in, checked_out, or cancelled.';
comment on column public.reservations.created_at is
  'Server managed.';
comment on column public.reservations.updated_at is
  'Server managed.';

create table public.bills (
  id uuid primary key default extensions.gen_random_uuid(),
  reservation_id uuid not null unique references public.reservations(id) on delete restrict,
  items jsonb not null,
  currency text not null,
  total_amount_minor integer not null,
  status text not null default 'open',
  updated_at timestamptz not null default now(),
  constraint bills_items_array_check check (jsonb_typeof(items) = 'array'),
  constraint bills_currency_iso_4217_check check (currency ~ '^[A-Z]{3}$'),
  constraint bills_total_non_negative_check check (total_amount_minor >= 0),
  constraint bills_status_check check (status in ('open', 'reviewed', 'closed'))
);

comment on table public.bills is
  'Synthetic charges for a reservation, shown for review during checkout.';
comment on column public.bills.id is
  'Primary key.';
comment on column public.bills.reservation_id is
  'References one reservation.';
comment on column public.bills.items is
  'Synthetic item description, quantity, unit amount, and line total in minor currency units.';
comment on column public.bills.currency is
  'Required ISO 4217 currency code.';
comment on column public.bills.total_amount_minor is
  'Must equal the sum of line totals; avoids floating-point currency arithmetic.';
comment on column public.bills.status is
  'open, reviewed, or closed; does not imply payment.';
comment on column public.bills.updated_at is
  'Server managed.';

create function public.bill_items_total_minor(line_items jsonb)
returns integer
language plpgsql
immutable
strict
set search_path = pg_catalog
as $$
declare
  line_item jsonb;
  total integer := 0;
begin
  if jsonb_typeof(line_items) <> 'array' then
    raise exception 'Bill items must be a JSON array';
  end if;

  for line_item in select value from jsonb_array_elements(line_items)
  loop
    if jsonb_typeof(line_item) <> 'object'
      or jsonb_typeof(line_item -> 'lineTotalMinor') <> 'number'
    then
      raise exception 'Each bill item must include a numeric lineTotalMinor';
    end if;

    total := total + (line_item ->> 'lineTotalMinor')::integer;
  end loop;

  return total;
end;
$$;

alter table public.bills
  add constraint bills_total_matches_items_check
  check (total_amount_minor = public.bill_items_total_minor(items));

create function public.set_updated_at()
returns trigger
language plpgsql
set search_path = pg_catalog
as $$
begin
  new.updated_at := now();
  return new;
end;
$$;

create trigger reservations_set_updated_at
  before update on public.reservations
  for each row execute function public.set_updated_at();

create trigger bills_set_updated_at
  before update on public.bills
  for each row execute function public.set_updated_at();

alter table public.guest_sessions
  add constraint guest_sessions_reservation_id_fkey
  foreign key (reservation_id) references public.reservations(id) on delete restrict;

create function public.has_active_guest_session_for_reservation(expected_reservation_id uuid)
returns boolean
language sql
stable
security definer
set search_path = public, pg_catalog
as $$
  select exists (
    select 1
    from public.guest_sessions
    where id = (
      (nullif(current_setting('request.jwt.claims', true), '')::jsonb ->> 'guest_session_id')::uuid
    )
      and reservation_id = expected_reservation_id
      and status = 'active'
      and expires_at > now()
  );
$$;

revoke all on function public.has_active_guest_session_for_reservation(uuid) from public;
grant execute on function public.has_active_guest_session_for_reservation(uuid) to authenticated;

alter table public.reservations enable row level security;
alter table public.reservations force row level security;
alter table public.bills enable row level security;
alter table public.bills force row level security;

revoke all on table public.reservations, public.bills from anon, authenticated;
grant select on table public.reservations, public.bills to authenticated;
grant select, insert, update, delete on table public.reservations, public.bills to service_role;

create policy "guests read their active reservation"
  on public.reservations
  for select
  to authenticated
  using (public.has_active_guest_session_for_reservation(id));

create policy "guests read the bill for their active reservation"
  on public.bills
  for select
  to authenticated
  using (public.has_active_guest_session_for_reservation(reservation_id));

create policy "service_role manages reservations"
  on public.reservations
  for all
  to service_role
  using (true)
  with check (true);

create policy "service_role manages bills"
  on public.bills
  for all
  to service_role
  using (true)
  with check (true);
