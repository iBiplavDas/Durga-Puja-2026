-- Behavioural tests for supabase/migrations/*_client_errors.sql (the app's error beacon and the team's view).
\set ON_ERROR_STOP on
set client_min_messages = warning;
delete from public.client_errors;

-- Anyone can log (no sign-in); the server truncates and masks whatever the client sent.
do $$ declare r jsonb; begin
  perform set_config('request.jwt.claims', '', false);
  set local role anon;
  r := public.log_client_error('TypeError: x is undefined', 'https://example.org/app.js?v=12#top', 10, 5,
                               'error', '79e85f33a482', 'Chrome 130 Android', 'explore', '/index.html?src=ig');
  assert r->>'status' = 'ok', r::text;
  r := public.log_client_error('TypeError: x is undefined', '/app.js', 10, 5, 'error', 'v1', 'Safari 17 iOS', 'home');
  assert r->>'status' = 'ok', r::text;
  r := public.log_client_error('Call me on +91 98300 12345 or mail a.b@example.com, token eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9xyz', null,
                               -4, 20000000, 'weird-kind', repeat('ab ', 40), null, 'me', repeat('p/', 150));
  assert r->>'status' = 'ok', r::text;
  r := public.log_client_error(repeat('é', 1000), repeat('s/', 450));
  assert r->>'status' = 'ok', r::text;
  r := public.log_client_error('   ', '/app.js');
  assert r->>'status' = 'ignored', r::text;
  r := public.log_client_error(null);
  assert r->>'status' = 'ignored', r::text;
  -- Nothing is readable from the app.
  begin perform 1 from public.client_errors; assert false, 'client_errors must not be readable';
  exception when insufficient_privilege then null; end;
  begin perform 1 from analytics.client_errors_daily; assert false, 'the errors view must not be readable from the app';
  exception when insufficient_privilege then null; end;
  begin insert into public.client_errors (message) values ('x'); assert false, 'client_errors must not be writable';
  exception when insufficient_privilege then null; end;
end $$;

do $$ declare r jsonb; begin
  perform set_config('request.jwt.claims', json_build_object('sub', '11111111-1111-1111-1111-111111111111', 'role', 'authenticated')::text, false);
  set local role authenticated;                                 -- signed-in guests can log too
  r := public.log_client_error('Unhandled: Failed to fetch', '/community.js', 3, 1, 'rejection');
  assert r->>'status' = 'ok', r::text;
end $$;

do $$ declare e record; d record; begin
  select * into e from public.client_errors where source = '/app.js' or source like 'https://example.org/%' order by id limit 1;
  assert e.source = 'https://example.org/app.js', 'query string and hash dropped: ' || e.source;
  assert e.page = '/index.html' and e.version = '79e85f33a482' and e.browser = 'Chrome 130 Android' and e.view = 'explore', e::text;
  select * into e from public.client_errors where message like 'Call me%';
  assert e.message not like '%98300%' and e.message like '%<number>%', 'phone masked: ' || e.message;
  assert e.message not like '%@example.com%' and e.message like '%<email>%', 'email masked: ' || e.message;
  assert e.message like '%<token>%', 'token masked: ' || e.message;
  assert e.kind = 'error' and e.line is null and char_length(e.version) = 40 and char_length(e.page) = 100, e::text;
  select * into e from public.client_errors where message like 'é%';
  assert char_length(e.message) = 300 and char_length(e.source) = 200, 'truncated';
  assert (select kind from public.client_errors where source = '/community.js') = 'rejection';
  -- The team's view groups by day, message and file.
  select * into d from analytics.client_errors_daily where message = 'TypeError: x is undefined' and source = '/app.js';
  assert d.n = 1 and d.day = public.ist_today() and d.browsers = 'Safari 17 iOS' and d.lines = '10', d::text;
  assert (select count(*) from analytics.client_errors_daily) = 5, 'one row per day, message and file';
  assert (select sum(n) from analytics.client_errors_daily) = 5;
end $$;

-- A global ceiling: once 5,000 rows arrived in the last hour, further calls store nothing.
insert into public.client_errors (message, at) select 'flood', now() - interval '10 minutes' from generate_series(1, 4995);
do $$ declare r jsonb; begin
  set local role anon;
  r := public.log_client_error('still fine', '/app.js');
  assert r->>'status' = 'rate_limited', r::text;
end $$;
do $$ begin
  assert not exists (select 1 from public.client_errors where message = 'still fine'), 'nothing stored over the limit';
  update public.client_errors set at = now() - interval '2 hours' where message = 'flood';
end $$;
do $$ declare r jsonb; begin
  set local role anon;
  r := public.log_client_error('fine again', '/app.js');
  assert r->>'status' = 'ok', 'the limit is per hour: ' || r::text;
end $$;

delete from public.client_errors;
select 'client errors SQL tests passed' as result;
