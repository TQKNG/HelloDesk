begin;

select plan(4);

insert into public.guest_sessions (id, token_hash, language, status, expires_at)
values
  (
    '00000000-0000-4000-8000-000000000401',
    'test-help-session-one',
    'en',
    'active',
    now() + interval '5 minutes'
  ),
  (
    '00000000-0000-4000-8000-000000000402',
    'test-help-session-two',
    'vi',
    'active',
    now() + interval '5 minutes'
  );

insert into public.help_requests (id, session_id, summary)
values
  (
    '00000000-0000-4000-8000-000000000501',
    '00000000-0000-4000-8000-000000000401',
    'Test request one'
  ),
  (
    '00000000-0000-4000-8000-000000000502',
    '00000000-0000-4000-8000-000000000402',
    'Test request two'
  );

set local request.jwt.claims = '{"guest_session_id":"00000000-0000-4000-8000-000000000401"}';
set local role authenticated;
create temporary table guest_help_request_result as
  select id from public.help_requests order by id;
create temporary table guest_acknowledgement_result as
  with updated as (
    update public.help_requests
    set status = 'acknowledged'
    where id = '00000000-0000-4000-8000-000000000501'
    returning id
  )
  select id from updated;
reset role;

select results_eq(
  'select id from guest_help_request_result',
  $$values ('00000000-0000-4000-8000-000000000501'::uuid)$$,
  'a guest can read only its own help-request status'
);
select is_empty(
  'select id from guest_acknowledgement_result',
  'a guest cannot acknowledge a help request'
);

set local request.jwt.claims = '{"app_metadata":{"role":"staff"}}';
set local role authenticated;
create temporary table staff_help_request_result as
  select id from public.help_requests order by id;
create temporary table staff_acknowledgement_result as
  update public.help_requests
  set status = 'acknowledged'
  where id = '00000000-0000-4000-8000-000000000501'
  returning id, acknowledged_at;
reset role;

select results_eq(
  'select id from staff_help_request_result',
  $$values
    ('00000000-0000-4000-8000-000000000501'::uuid),
    ('00000000-0000-4000-8000-000000000502'::uuid)$$,
  'staff can list every help request'
);
select ok(
  exists (
    select 1
    from staff_acknowledgement_result
    where id = '00000000-0000-4000-8000-000000000501'
      and acknowledged_at is not null
  ),
  'staff acknowledgement records its server-managed timestamp'
);

select * from finish();

rollback;
