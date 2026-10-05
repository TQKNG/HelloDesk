begin;

select plan(4);

insert into public.reservations (
  id,
  reservation_code,
  guest_display_name,
  arrival_date,
  departure_date,
  room_number,
  status
)
values
  (
    '00000000-0000-4000-8000-000000000101',
    'TEST-SESSION-ONE',
    'Test Guest One',
    current_date,
    current_date + 1,
    '401',
    'reserved'
  ),
  (
    '00000000-0000-4000-8000-000000000102',
    'TEST-SESSION-TWO',
    'Test Guest Two',
    current_date,
    current_date + 1,
    '402',
    'reserved'
  );

insert into public.bills (id, reservation_id, items, currency, total_amount_minor)
values
  (
    '00000000-0000-4000-8000-000000000201',
    '00000000-0000-4000-8000-000000000101',
    '[{"description":"Test charge","quantity":1,"unitAmountMinor":100,"lineTotalMinor":100}]'::jsonb,
    'CAD',
    100
  ),
  (
    '00000000-0000-4000-8000-000000000202',
    '00000000-0000-4000-8000-000000000102',
    '[{"description":"Test charge","quantity":1,"unitAmountMinor":200,"lineTotalMinor":200}]'::jsonb,
    'CAD',
    200
  );

insert into public.guest_sessions (
  id,
  token_hash,
  language,
  reservation_id,
  status,
  expires_at
)
values
  (
    '00000000-0000-4000-8000-000000000301',
    'test-token-hash-active',
    'en',
    '00000000-0000-4000-8000-000000000101',
    'active',
    timezone('utc', now()) + interval '5 minutes'
  ),
  (
    '00000000-0000-4000-8000-000000000302',
    'test-token-hash-expired',
    'vi',
    '00000000-0000-4000-8000-000000000102',
    'expired',
    timezone('utc', now()) - interval '1 minute'
  );

set local request.jwt.claims = '{"guest_session_id":"00000000-0000-4000-8000-000000000301"}';
set local role authenticated;
create temporary table active_reservation_result as
  select id from public.reservations order by id;
create temporary table active_bill_result as
  select id from public.bills order by id;
reset role;

select results_eq(
  'select id from active_reservation_result',
  $$values ('00000000-0000-4000-8000-000000000101'::uuid)$$,
  'an active guest session can read only its reservation'
);
select results_eq(
  'select id from active_bill_result',
  $$values ('00000000-0000-4000-8000-000000000201'::uuid)$$,
  'an active guest session can read only its bill'
);

set local request.jwt.claims = '{"guest_session_id":"00000000-0000-4000-8000-000000000302"}';
set local role authenticated;
create temporary table expired_reservation_result as
  select id from public.reservations order by id;
create temporary table expired_bill_result as
  select id from public.bills order by id;
reset role;

select is_empty(
  'select id from expired_reservation_result',
  'an expired guest session cannot read reservations'
);
select is_empty(
  'select id from expired_bill_result',
  'an expired guest session cannot read bills'
);

select * from finish();

rollback;
