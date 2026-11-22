-- Moments moderation: the team's review queue and actions for reported or hidden photos and videos
-- (docs/product/COMMUNITY.md, "Moderation").
--
--   Table editor → schema "analytics" → moments_queue        what needs a look, worst first
--   SQL editor:  select public.moderate_moment('<id>', 'hide' | 'restore' | 'delete');
--
-- Three distinct reports still hide a moment on their own (report_photo). A restore unhides it, resets its report
-- count and stamps reviewed_at: the old reports stay on file only so the same people can't report it again, and
-- no longer count, so a restored moment needs three *new* reports to be hidden again. A team hide sticks whatever
-- the reports say. place_counters.photos (the "N moments" count on place pages) always equals the place's visible
-- moments that aren't menu photos; every path below keeps it so.
-- Idempotent: safe to re-run.

alter table public.photos add column if not exists reviewed_at timestamptz;
alter table public.photos add column if not exists moderation text check (moderation in ('hidden', 'restored'));

-- ---------------------------------------------------------------- reports and owner deletes, count-safe
-- Same signatures as the community migration (grants carry over). The count only drops when a moment actually goes
-- from visible to hidden, and menu photos (never counted) don't touch it.
create or replace function public.report_photo(p_photo uuid, p_reason text default null) returns jsonb
language plpgsql security definer set search_path = public as $$
declare v_uid uuid := auth.uid(); v_row photos%rowtype; v_hidden boolean;
begin
  if v_uid is null then raise exception 'sign-in required' using errcode = '28000'; end if;
  select * into v_row from photos where id = p_photo for update;
  if not found then return jsonb_build_object('status', 'not_found'); end if;
  insert into photo_reports (photo_id, user_id, reason) values (p_photo, v_uid, left(p_reason, 60))
    on conflict do nothing;
  if not found then
    return jsonb_build_object('status', 'already_reported');
  end if;
  update photos set reports = reports + 1, hidden = hidden or reports + 1 >= 3
    where id = p_photo returning hidden into v_hidden;
  if v_hidden and not v_row.hidden and v_row.tag is null then
    update place_counters set photos = greatest(photos - 1, 0) where place_id = v_row.place_id;
  end if;
  return jsonb_build_object('status', 'ok', 'hidden', v_hidden);
end $$;

create or replace function public.delete_photo(p_photo uuid) returns jsonb
language plpgsql security definer set search_path = public as $$
declare v_uid uuid := auth.uid(); v_row photos%rowtype;
begin
  if v_uid is null then raise exception 'sign-in required' using errcode = '28000'; end if;
  select * into v_row from photos where id = p_photo and user_id = v_uid;
  if not found then return jsonb_build_object('status', 'not_found'); end if;
  delete from photos where id = p_photo;
  if not v_row.hidden and v_row.tag is null then
    update place_counters set photos = greatest(photos - 1, 0) where place_id = v_row.place_id;
  end if;
  -- The client removes the storage objects itself (storage policy: owners may delete).
  return jsonb_build_object('status', 'ok', 'path', v_row.path, 'thumb_path', v_row.thumb_path);
end $$;

-- Heal any drift from before this migration (menu photos used to be subtracted when reported or deleted).
update public.place_counters c set photos = x.n
from (select pc.place_id, (select count(*) from public.photos ph
                           where ph.place_id = pc.place_id and not ph.hidden and ph.tag is null)::integer as n
      from public.place_counters pc) x
where x.place_id = c.place_id and c.photos is distinct from x.n;

-- ---------------------------------------------------------------- the team's actions (SQL editor only)
create or replace function public.moderate_moment(p_id uuid, p_action text) returns jsonb
language plpgsql security definer set search_path = public as $$
declare v_row photos%rowtype;
begin
  if p_action is null or p_action not in ('hide', 'restore', 'delete') then
    return jsonb_build_object('status', 'bad_action', 'actions', 'hide, restore, delete');
  end if;
  select * into v_row from photos where id = p_id for update;
  if not found then return jsonb_build_object('status', 'not_found'); end if;

  if p_action = 'hide' then
    update photos set hidden = true, moderation = 'hidden', reviewed_at = now() where id = p_id;
    if not v_row.hidden and v_row.tag is null then
      update place_counters set photos = greatest(photos - 1, 0) where place_id = v_row.place_id;
    end if;
    return jsonb_build_object('status', 'ok', 'action', 'hide', 'hidden', true);
  elsif p_action = 'restore' then
    update photos set hidden = false, reports = 0, moderation = 'restored', reviewed_at = now() where id = p_id;
    if v_row.hidden and v_row.tag is null then
      insert into place_counters (place_id, photos) values (v_row.place_id, 1)
        on conflict (place_id) do update set photos = place_counters.photos + 1;
    end if;
    return jsonb_build_object('status', 'ok', 'action', 'restore', 'hidden', false);
  end if;

  delete from photos where id = p_id;                       -- its likes and reports go with it
  if not v_row.hidden and v_row.tag is null then
    update place_counters set photos = greatest(photos - 1, 0) where place_id = v_row.place_id;
  end if;
  -- Files can't be removed from SQL: delete these two in Storage → moments.
  return jsonb_build_object('status', 'ok', 'action', 'delete', 'path', v_row.path, 'thumb_path', v_row.thumb_path);
end $$;
revoke all on function public.moderate_moment(uuid, text) from public, anon, authenticated;

-- ---------------------------------------------------------------- the queue
-- The project URL, for clickable media links. supabase-setup fills it; or once in the SQL editor:
--   insert into private.project_settings values ('supabase_url', 'https://<ref>.supabase.co') on conflict (key) do update set value = excluded.value;
create schema if not exists private;
revoke all on schema private from public, anon, authenticated;
create table if not exists private.project_settings (
  key   text primary key,
  value text not null
);
revoke all on private.project_settings from public, anon, authenticated;

create schema if not exists analytics;
drop view if exists analytics.moments_queue;
create view analytics.moments_queue as
  select q.* from (
    select ph.id,
           case when ph.hidden and ph.moderation = 'hidden' then 'hidden by team'
                when ph.hidden then 'hidden by reports'
                else 'reported' end as status,
           pl.name as place, ph.place_id, ph.media_type, ph.tag, ph.caption, ph.reports, ph.hidden,
           (select string_agg(r.reason || case when r.n > 1 then ' ×' || r.n else '' end, ', ' order by r.n desc, r.reason)
            from (select coalesce(nullif(btrim(pr.reason), ''), '(no reason)') as reason, count(*) as n
                  from public.photo_reports pr
                  where pr.photo_id = ph.id and pr.created_at > coalesce(ph.reviewed_at, '-infinity')
                  group by 1) r) as reasons,
           (select max(pr.created_at) from public.photo_reports pr where pr.photo_id = ph.id) as last_report_at,
           s.value || '/storage/v1/object/public/moments/' || ph.path as url,
           s.value || '/storage/v1/object/public/moments/' || ph.thumb_path as thumb_url,
           ph.path, ph.on_site, ph.likes, ph.created_at, ph.reviewed_at
    from public.photos ph
    join public.places pl on pl.id = ph.place_id
    left join private.project_settings s on s.key = 'supabase_url'
    where ph.hidden or ph.reports > 0
  ) q
  order by (q.status = 'hidden by team'), q.reports desc, q.created_at desc;
revoke all on analytics.moments_queue from anon, authenticated;
