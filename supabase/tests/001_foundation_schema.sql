begin;

select plan(8);

select has_table('public', 'guest_sessions', 'guest session table exists');
select has_table('public', 'pending_actions', 'pending action table exists');
select has_column('public', 'guest_sessions', 'token_hash', 'guest sessions retain only a token hash');
select col_is_unique('public', 'guest_sessions', 'token_hash', 'guest session token hashes are unique');
select col_has_check('public', 'guest_sessions', 'language', 'guest session language is constrained');
select has_fk('public', 'pending_actions', 'pending actions belong to a guest session');
select col_has_check('public', 'pending_actions', 'kind', 'pending action kind is constrained');
select row_security_active('public', 'pending_actions', 'pending actions enforce RLS');

select * from finish();

rollback;
