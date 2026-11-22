-- Behavioural tests for supabase/migrations/*_moderation.sql: the moments queue, moderate_moment(), and the
-- place photo count staying equal to the visible, non-menu moments through reports, hides, restores and deletes.
\set ON_ERROR_STOP on
set client_min_messages = warning;

create or replace function pg_temp.as_user(u text) returns void language sql as $$
  select set_config('request.jwt.claims', json_build_object('sub', u, 'role', 'authenticated')::text, false);
$$;
create or replace function pg_temp.photos_count(p text) returns integer language sql as $$
  select coalesce((select photos from public.place_counters where place_id = p), 0)
$$;
-- Reports as that guest, then back to the test's own role.
create or replace function pg_temp.report(u text, p uuid, reason text) returns jsonb language plpgsql as $$
declare r jsonb;
begin
  perform pg_temp.as_user(u);
  set local role authenticated;
  r := public.report_photo(p, reason);
  reset role;
  return r;
end $$;

insert into public.places (id, kind, name, zone, lat, lng, radius_m) values
  ('m_pandal', 'pandal', 'Moderation Pandal', 'north', 22.60, 88.37, 300),
  ('m_food', 'food', 'Moderation Cabin', 'north', 22.61, 88.37, 300)
on conflict (id) do nothing;
insert into private.project_settings values ('supabase_url', 'https://example.supabase.co')
  on conflict (key) do update set value = excluded.value;
insert into storage.objects (bucket_id, name) values
  ('moments', 'aaaaaaaa-0000-0000-0000-00000000000a/a.jpg'),
  ('moments', 'bbbbbbbb-0000-0000-0000-00000000000b/b.jpg'),
  ('moments', 'cccccccc-0000-0000-0000-00000000000c/menu.jpg');

-- Two moments at the pandal and a menu photo at the eatery (menus aren't counted as moments).
do $$ declare r jsonb; begin
  perform pg_temp.as_user('aaaaaaaa-0000-0000-0000-00000000000a');
  set local role authenticated;
  r := public.add_photo('m_pandal', 'aaaaaaaa-0000-0000-0000-00000000000a/a.jpg', 'aaaaaaaa-0000-0000-0000-00000000000a/a.jpg', 'image', 'Moment A');
  perform set_config('pp.a', r->>'id', false);
  perform pg_temp.as_user('bbbbbbbb-0000-0000-0000-00000000000b');
  r := public.add_photo('m_pandal', 'bbbbbbbb-0000-0000-0000-00000000000b/b.jpg', 'bbbbbbbb-0000-0000-0000-00000000000b/b.jpg', 'image', 'Moment B');
  perform set_config('pp.b', r->>'id', false);
  perform pg_temp.as_user('cccccccc-0000-0000-0000-00000000000c');
  r := public.add_photo('m_food', 'cccccccc-0000-0000-0000-00000000000c/menu.jpg', 'cccccccc-0000-0000-0000-00000000000c/menu.jpg', 'image',
                        null, null, null, null, 'menu');
  perform set_config('pp.c', r->>'id', false);
end $$;

do $$ begin
  assert pg_temp.photos_count('m_pandal') = 2 and pg_temp.photos_count('m_food') = 0, 'starting counts';
  assert not exists (select 1 from analytics.moments_queue where place_id in ('m_pandal', 'm_food')), 'nothing to review yet';
end $$;

-- Three reports hide A; the queue shows it first with the reasons and clickable links.
do $$ declare a uuid := current_setting('pp.a')::uuid; q record; begin
  perform pg_temp.report('d0000000-0000-0000-0000-000000000001', a, 'spam');
  perform pg_temp.report('d0000000-0000-0000-0000-000000000002', a, 'spam');
  assert pg_temp.photos_count('m_pandal') = 2, 'two reports: still visible';
  perform pg_temp.report('d0000000-0000-0000-0000-000000000003', a, 'not this pandal');
  assert pg_temp.photos_count('m_pandal') = 1, 'hidden by reports: count drops once';
  assert (pg_temp.report('d0000000-0000-0000-0000-000000000004', a, null))->>'hidden' = 'true';
  assert pg_temp.photos_count('m_pandal') = 1, 'a fourth report does not drop it again';
  select * into q from analytics.moments_queue where id = a;
  assert q.status = 'hidden by reports' and q.reports = 4 and q.hidden and q.place = 'Moderation Pandal' and q.caption = 'Moment A', q::text;
  assert q.reasons = 'spam ×2, (no reason), not this pandal', q.reasons;
  assert q.url = 'https://example.supabase.co/storage/v1/object/public/moments/aaaaaaaa-0000-0000-0000-00000000000a/a.jpg', q.url;
  assert (select id from analytics.moments_queue limit 1) = a, 'most reported first';
end $$;

-- Restore: visible again, counted again, out of the queue; old reporters can't hide it again.
do $$ declare a uuid := current_setting('pp.a')::uuid; r jsonb; q record; begin
  r := public.moderate_moment(a, 'restore');
  assert r->>'status' = 'ok' and r->>'hidden' = 'false', r::text;
  assert pg_temp.photos_count('m_pandal') = 2, 'restore adds it back to the count';
  assert not exists (select 1 from analytics.moments_queue where id = a), 'restored: out of the queue';
  assert (select reviewed_at is not null and moderation = 'restored' and reports = 0 from public.photos where id = a);
  r := public.moderate_moment(a, 'restore');                                 -- twice is harmless
  assert pg_temp.photos_count('m_pandal') = 2, 'a second restore does not count it twice';
  assert (pg_temp.report('d0000000-0000-0000-0000-000000000001', a, 'spam'))->>'status' = 'already_reported';
  assert (pg_temp.report('d0000000-0000-0000-0000-000000000002', a, 'spam'))->>'status' = 'already_reported';
  assert (pg_temp.report('d0000000-0000-0000-0000-000000000003', a, 'spam'))->>'status' = 'already_reported';
  assert exists (select 1 from public.photos_feed where id = a), 'old reports do not hide a restored moment';
end $$;
do $$ declare a uuid := current_setting('pp.a')::uuid; r jsonb; q record; begin
  -- A new report (a later transaction, as in real life) puts it back in the queue, with only the new reason.
  r := pg_temp.report('d0000000-0000-0000-0000-000000000005', a, 'blurry');
  assert r->>'status' = 'ok' and r->>'hidden' = 'false', r::text;
  select * into q from analytics.moments_queue where id = a;
  assert q.status = 'reported' and q.reports = 1 and q.reasons = 'blurry', q::text;
end $$;

-- A team hide sticks, and later reports don't drop the count a second time.
do $$ declare b uuid := current_setting('pp.b')::uuid; r jsonb; begin
  r := public.moderate_moment(b, 'hide');
  assert r->>'status' = 'ok', r::text;
  assert pg_temp.photos_count('m_pandal') = 1, 'team hide drops the count';
  r := public.moderate_moment(b, 'hide');
  assert pg_temp.photos_count('m_pandal') = 1, 'hiding twice drops it once';
  perform pg_temp.report('d0000000-0000-0000-0000-000000000001', b, 'x');
  perform pg_temp.report('d0000000-0000-0000-0000-000000000002', b, 'x');
  perform pg_temp.report('d0000000-0000-0000-0000-000000000003', b, 'x');
  assert pg_temp.photos_count('m_pandal') = 1, 'reports on a hidden moment leave the count alone';
  assert (select status from analytics.moments_queue where id = b) = 'hidden by team';
  assert (select status from analytics.moments_queue offset 0 limit 1) <> 'hidden by team', 'what needs review comes first';
  assert not exists (select 1 from public.photos_feed where id = b);
end $$;

-- Menu photos never touch the moments count.
do $$ declare c uuid := current_setting('pp.c')::uuid; begin
  perform pg_temp.report('d0000000-0000-0000-0000-000000000001', c, 'x');
  perform pg_temp.report('d0000000-0000-0000-0000-000000000002', c, 'x');
  perform pg_temp.report('d0000000-0000-0000-0000-000000000003', c, 'x');
  assert pg_temp.photos_count('m_food') = 0, 'a hidden menu photo was never counted';
  perform public.moderate_moment(c, 'restore');
  assert pg_temp.photos_count('m_food') = 0, 'a restored menu photo is still not a moment';
end $$;

-- Delete: a visible moment leaves the count, a hidden one doesn't; the file paths come back for Storage.
do $$ declare a uuid := current_setting('pp.a')::uuid; b uuid := current_setting('pp.b')::uuid; r jsonb; begin
  r := public.moderate_moment(b, 'delete');
  assert r->>'status' = 'ok' and r->>'path' = 'bbbbbbbb-0000-0000-0000-00000000000b/b.jpg', r::text;
  assert pg_temp.photos_count('m_pandal') = 1, 'deleting a hidden moment leaves the count';
  r := public.moderate_moment(a, 'delete');
  assert r->>'status' = 'ok' and r->>'thumb_path' like 'aaaaaaaa-%', r::text;
  assert pg_temp.photos_count('m_pandal') = 0, 'deleting a visible moment drops the count';
  assert not exists (select 1 from public.photo_reports where photo_id in (a, b)), 'reports go with it';
  assert (public.moderate_moment(a, 'delete'))->>'status' = 'not_found';
  assert (public.moderate_moment(current_setting('pp.c')::uuid, 'approve'))->>'status' = 'bad_action';
  assert (public.moderate_moment(current_setting('pp.c')::uuid, null))->>'status' = 'bad_action';
end $$;

-- The owner's own delete of a menu photo no longer subtracts from the moments count.
do $$ declare r jsonb; begin
  insert into public.place_counters (place_id, photos) values ('m_food', 5) on conflict (place_id) do update set photos = 5;
  perform pg_temp.as_user('cccccccc-0000-0000-0000-00000000000c');
  set local role authenticated;
  r := public.delete_photo(current_setting('pp.c')::uuid);
  assert r->>'status' = 'ok', r::text;
end $$;
do $$ begin
  assert pg_temp.photos_count('m_food') = 5, 'menu delete leaves the moments count';
  update public.place_counters set photos = 0 where place_id = 'm_food';
end $$;

-- Only the team (SQL editor) can moderate or read the queue.
do $$ begin
  perform pg_temp.as_user('aaaaaaaa-0000-0000-0000-00000000000a');
  set local role authenticated;
  begin perform public.moderate_moment(gen_random_uuid(), 'hide'); assert false, 'authenticated must not moderate';
  exception when insufficient_privilege then null; end;
  begin perform 1 from analytics.moments_queue; assert false, 'the queue must not be readable from the app';
  exception when insufficient_privilege then null; end;
  begin perform 1 from private.project_settings; assert false, 'settings must not be readable from the app';
  exception when insufficient_privilege then null; end;
end $$;
do $$ begin
  perform set_config('request.jwt.claims', '', false);
  set local role anon;
  begin perform public.moderate_moment(gen_random_uuid(), 'restore'); assert false, 'anon must not moderate';
  exception when insufficient_privilege then null; end;
end $$;

delete from private.project_settings where key = 'supabase_url';
select 'moderation SQL tests passed' as result;
