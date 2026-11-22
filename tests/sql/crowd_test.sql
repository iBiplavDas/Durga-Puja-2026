-- Behavioural tests for supabase/migrations/*_crowd_reports.sql ("How's the queue here?").
\set ON_ERROR_STOP on
set client_min_messages = warning;

create or replace function pg_temp.as_user(u text) returns void language sql as $$
  select set_config('request.jwt.claims', json_build_object('sub', u, 'role', 'authenticated')::text, false);
$$;

-- Fixture places, independent of the real data: a pandal (300 m radius), another pandal, and an eatery.
insert into public.places (id, kind, name, zone, lat, lng, radius_m) values
  ('cr_pandal', 'pandal', 'Crowd Test Pandal', 'south_lakemarket', 22.5185, 88.3489, 300),
  ('cr_other', 'pandal', 'Crowd Test Other', 'north', 22.6000, 88.3700, 300),
  ('cr_food', 'food', 'Crowd Test Cabin', 'north', 22.5945, 88.3660, 300);

-- Reporting: at the pandal only, valid levels only, pandals only, sign-in required.
do $$ declare r jsonb; begin
  perform pg_temp.as_user('c0c0c0c0-0000-0000-0000-000000000001');
  set local role authenticated;

  r := public.report_crowd('cr_pandal', 'long', 22.5185, 88.3489, 10);
  assert r->>'status' = 'ok', r::text;
  assert (r->>'reports')::int = 1 and (r->>'long')::int = 1 and (r->>'short')::int = 0, 'ok returns the aggregate: ' || r::text;

  r := public.report_crowd('cr_pandal', 'short', 22.5186, 88.3490, 10);
  assert r->>'status' = 'too_soon' and (r->>'long')::int = 1, 'one report per pandal per 20 minutes: ' || r::text;

  r := public.report_crowd('cr_other', 'short', 22.5726, 88.3639, 10);     -- from College Street, 3 km off
  assert r->>'status' = 'too_far' and (r->>'distance_m')::int > 2000, r::text;
  r := public.report_crowd('cr_other', 'short', 22.6000 + 0.0032, 88.3700, 80);   -- ~356 m: within 300 + 80
  assert r->>'status' = 'ok', 'radius plus accuracy: ' || r::text;
  r := public.report_crowd('cr_pandal', 'short', 22.5185 + 0.0040, 88.3489, 5000);  -- ~445 m: accuracy counts up to 100 m only
  assert r->>'status' = 'too_far', 'accuracy is capped: ' || r::text;

  r := public.report_crowd('cr_pandal', 'huge', 22.5185, 88.3489, 10);
  assert r->>'status' = 'bad_level', r::text;
  r := public.report_crowd('cr_food', 'short', 22.5945, 88.3660, 10);
  assert r->>'status' = 'not_pandal', r::text;
  r := public.report_crowd('nowhere', 'short', 22.5185, 88.3489, 10);
  assert r->>'status' = 'unknown_place', r::text;
  r := public.report_crowd('cr_pandal', 'short', null, null, null);
  assert r->>'status' = 'no_location', r::text;
end $$;

do $$ begin
  perform set_config('request.jwt.claims', '{"role": "authenticated"}', false);   -- no user
  set local role authenticated;
  begin
    perform public.report_crowd('cr_pandal', 'short', 22.5185, 88.3489, 10);
    assert false, 'reporting needs a sign-in';
  exception when invalid_authorization_specification then null; end;
end $$;

-- Raw coordinates are not stored; distance and accuracy are.
do $$ declare r record; begin
  select * into r from public.crowd_reports where place_id = 'cr_other';
  assert r.distance_m between 340 and 370 and r.accuracy_m = 80, r::text;
  assert not exists (select 1 from information_schema.columns where table_schema = 'public' and table_name = 'crowd_reports' and column_name in ('lat', 'lng'));
end $$;

-- The aggregate: one vote per person (their latest in the window), only the last 45 minutes.
do $$ declare r jsonb; begin
  insert into public.crowd_reports (place_id, level, reporter, created_at) values
    ('cr_pandal', 'short',  'c0c0c0c0-0000-0000-0000-000000000002', now() - interval '5 minutes'),
    ('cr_pandal', 'long',   'c0c0c0c0-0000-0000-0000-000000000003', now() - interval '40 minutes'),
    ('cr_pandal', 'short',  'c0c0c0c0-0000-0000-0000-000000000003', now() - interval '10 minutes'),  -- changed their mind
    ('cr_pandal', 'medium', 'c0c0c0c0-0000-0000-0000-000000000004', now() - interval '30 minutes'),
    ('cr_pandal', 'long',   'c0c0c0c0-0000-0000-0000-000000000005', now() - interval '50 minutes');  -- too old
  set local role anon;
  r := public.crowd_now('cr_pandal');
  assert (r->>'reports')::int = 4, r::text;
  assert (r->>'short')::int = 2 and (r->>'medium')::int = 1 and (r->>'long')::int = 1, r::text;
  assert (r->>'window_min')::int = 45, r::text;
  assert not (r ? 'reporter'), 'aggregates only';
  r := public.crowd_now('nowhere');
  assert (r->>'reports')::int = 0, r::text;
end $$;

-- Daily cap: 30 reports a day per person, across pandals.
do $$ declare r jsonb; begin
  insert into public.crowd_reports (place_id, level, reporter, created_at)
    select 'cr_other', 'short', 'c0c0c0c0-0000-0000-0000-000000000006', now() - (i * interval '30 minutes')
    from generate_series(1, 30) i where i * 30 < 24 * 60;
  perform pg_temp.as_user('c0c0c0c0-0000-0000-0000-000000000006');
  set local role authenticated;
  r := public.report_crowd('cr_pandal', 'short', 22.5185, 88.3489, 10);
  assert r->>'status' = 'rate_limited', r::text;
end $$;

-- Clients can't touch the table or the team's view; anon can't report.
do $$ begin
  perform pg_temp.as_user('c0c0c0c0-0000-0000-0000-000000000001');
  set local role authenticated;
  begin perform 1 from public.crowd_reports limit 1; assert false, 'crowd_reports must not be selectable';
  exception when insufficient_privilege then null; end;
  begin insert into public.crowd_reports (place_id, level, reporter) values ('cr_pandal', 'long', auth.uid());
    assert false, 'crowd_reports must not be insertable';
  exception when insufficient_privilege then null; end;
  begin perform 1 from analytics.crowd_reports limit 1; assert false, 'the team view is not for the app';
  exception when insufficient_privilege then null; end;
end $$;
do $$ begin
  set local role anon;
  begin perform public.report_crowd('cr_pandal', 'short', 22.5185, 88.3489, 10); assert false, 'anon must not report';
  exception when insufficient_privilege then null; end;
end $$;

-- The team's view: place name, level, a short reporter tag (not the id).
do $$ declare r record; begin
  select * into r from analytics.crowd_reports where place_id = 'cr_other' and reporter_tag is not null limit 1;
  assert r.place = 'Crowd Test Other' and length(r.reporter_tag) = 8, r::text;
  assert not exists (select 1 from information_schema.columns where table_schema = 'analytics' and table_name = 'crowd_reports' and column_name = 'reporter');
end $$;

-- With Supabase's auth.users present, "delete all my data" takes the person's reports with it.
begin;
create table auth.users (id uuid primary key);
\ir ../../supabase/migrations/20261122000000_crowd_reports.sql
insert into auth.users values ('c0c0c0c0-0000-0000-0000-0000000000aa');
do $$ declare r jsonb; begin
  perform pg_temp.as_user('c0c0c0c0-0000-0000-0000-0000000000aa');
  set local role authenticated;
  r := public.report_crowd('cr_other', 'medium', 22.6000, 88.3700, 10);
  assert r->>'status' = 'ok', r::text;
  r := public.delete_my_data();
  assert r->>'status' = 'ok', r::text;
end $$;
reset role;   -- set local lasts to the end of this transaction
do $$ begin
  assert not exists (select 1 from public.crowd_reports where reporter = 'c0c0c0c0-0000-0000-0000-0000000000aa'), 'reports deleted with the account';
end $$;
rollback;

-- Leave nothing behind for the other tests.
delete from public.crowd_reports where place_id like 'cr\_%';
delete from public.places where id in ('cr_pandal', 'cr_other', 'cr_food');
select 'crowd ok';
