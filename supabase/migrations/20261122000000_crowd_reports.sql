-- "How's the queue here?": people standing at a pandal say Short, Medium or Long. It turns the crowd-by-hour
-- model (a guess, app/footfall.js and crowdIndex) into a live signal, shown beside it as "People here say…",
-- never in place of it.
--
-- Rules, like check-ins (20261002000000_community.sql):
--  * Only through report_crowd(): RLS on, no table access for anon/authenticated.
--  * A report only counts when the phone is at the pandal: within radius_m plus the reported accuracy (capped at
--    100 m), the same test record_visit uses. Raw coordinates are used for that check and never stored; the
--    distance and accuracy are kept so the team can judge the reports.
--  * One report per pandal per person every 20 minutes, and at most 30 a day.
--  * The app reads only aggregates for the last 45 minutes (crowd_now): one vote per person (their latest), no ids.
--  * delete_my_data() removes the account from auth.users; reports go with it (foreign key, on delete cascade).
-- The team reads them in the dashboard: Table editor, schema "analytics", view crowd_reports.

create table if not exists public.crowd_reports (
  id          bigint generated always as identity primary key,
  place_id    text not null references public.places (id) on delete cascade,
  level       text not null check (level in ('short', 'medium', 'long')),
  reporter    uuid not null,
  distance_m  integer,
  accuracy_m  integer,
  created_at  timestamptz not null default now()
);
create index if not exists crowd_reports_place_recent on public.crowd_reports (place_id, created_at desc);
create index if not exists crowd_reports_reporter on public.crowd_reports (reporter, created_at desc);
alter table public.crowd_reports enable row level security;
revoke all on public.crowd_reports from anon, authenticated;

-- "Delete all my data" deletes the auth user; take that person's reports with it. (No auth.users on a plain
-- Postgres test database, so only where it exists. NOT VALID: rows from before the key aren't re-checked.)
do $$ begin
  if to_regclass('auth.users') is not null
     and not exists (select 1 from pg_constraint where conname = 'crowd_reports_reporter_fkey' and conrelid = 'public.crowd_reports'::regclass) then
    alter table public.crowd_reports
      add constraint crowd_reports_reporter_fkey foreign key (reporter) references auth.users (id) on delete cascade not valid;
  end if;
end $$;

-- ---------------------------------------------------------------- read: the last 45 minutes, aggregates only
-- {reports, short, medium, long, window_min}. Each person counts once, with their latest report. The app shows
-- it only from 3 reports up (app/core.js crowdSummary): too few voices is worse than none.
create or replace function public.crowd_now(p_place text) returns jsonb
language sql stable security definer set search_path = public as $$
  with latest as (
    select distinct on (reporter) level
    from crowd_reports
    where place_id = p_place and created_at > now() - interval '45 minutes'
    order by reporter, created_at desc
  )
  select jsonb_build_object(
    'reports', count(*),
    'short',   count(*) filter (where level = 'short'),
    'medium',  count(*) filter (where level = 'medium'),
    'long',    count(*) filter (where level = 'long'),
    'window_min', 45)
  from latest
$$;
revoke all on function public.crowd_now(text) from public;
grant execute on function public.crowd_now(text) to anon, authenticated;

-- ---------------------------------------------------------------- write: one report, from the pandal
create or replace function public.report_crowd(
  p_place text, p_level text, p_lat double precision, p_lng double precision, p_accuracy double precision default null)
returns jsonb language plpgsql security definer set search_path = public as $$
declare
  v_uid   uuid := auth.uid();
  v_place places%rowtype;
  v_dist  double precision;
begin
  if v_uid is null then raise exception 'sign-in required' using errcode = '28000'; end if;
  if p_level is null or p_level not in ('short', 'medium', 'long') then
    return jsonb_build_object('status', 'bad_level');
  end if;
  select * into v_place from places where id = p_place;
  if not found then return jsonb_build_object('status', 'unknown_place'); end if;
  if v_place.kind <> 'pandal' then return jsonb_build_object('status', 'not_pandal'); end if;
  if p_lat is null or p_lng is null then return jsonb_build_object('status', 'no_location'); end if;

  v_dist := distance_m(p_lat, p_lng, v_place.lat, v_place.lng);
  if v_dist > v_place.radius_m + least(greatest(coalesce(p_accuracy, 50), 0), 100) then
    return jsonb_build_object('status', 'too_far', 'distance_m', round(v_dist));
  end if;

  -- One person's taps arrive one at a time, so two quick taps can't both slip past the limits below.
  perform pg_advisory_xact_lock(hashtext('crowd_report:' || v_uid::text));
  if exists (select 1 from crowd_reports where reporter = v_uid and place_id = p_place
             and created_at > now() - interval '20 minutes') then
    return jsonb_build_object('status', 'too_soon') || crowd_now(p_place);
  end if;
  if (select count(*) from crowd_reports where reporter = v_uid and created_at > now() - interval '24 hours') >= 30 then
    return jsonb_build_object('status', 'rate_limited');
  end if;

  insert into crowd_reports (place_id, level, reporter, distance_m, accuracy_m)
  values (p_place, p_level, v_uid, round(v_dist),
          case when p_accuracy is null then null else round(least(greatest(p_accuracy, 0), 5000)) end);
  return jsonb_build_object('status', 'ok') || crowd_now(p_place);
end $$;
revoke all on function public.report_crowd(text, text, double precision, double precision, double precision) from public, anon;
grant execute on function public.report_crowd(text, text, double precision, double precision, double precision) to authenticated;

-- ---------------------------------------------------------------- the team's view
-- Who reported is a short tag (same person, same tag), enough to spot one phone flooding a pandal.
create schema if not exists analytics;
drop view if exists analytics.crowd_reports;
create view analytics.crowd_reports as
  select r.id, r.place_id, p.name as place, p.zone, r.level, r.distance_m, r.accuracy_m,
         left(md5(r.reporter::text), 8) as reporter_tag,
         r.created_at, (r.created_at at time zone 'Asia/Kolkata') as created_ist
  from public.crowd_reports r
  join public.places p on p.id = r.place_id
  order by r.created_at desc;
revoke all on analytics.crowd_reports from anon, authenticated;
