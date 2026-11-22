-- Client error monitoring: uncaught errors and unhandled promise rejections from the app (app/errors.js), so
-- the team sees breakage on festival nights before users report it (docs/product/ANALYTICS.md).
--
-- A record is the error message, the script file and line, the data version, the browser family, the screen
-- and the page path. No device id, account, name or location. The client sends each distinct error once per
-- page load and at most 10; the server truncates and masks again, and stops storing once 5,000 rows have
-- arrived in the last hour, so the RPC can't be used to fill the database or run up egress.
-- The team reads analytics.client_errors_daily in the dashboard; the analytics-report workflow sums it daily.

create table if not exists public.client_errors (
  id       bigint generated always as identity primary key,
  at       timestamptz not null default now(),
  kind     text not null default 'error' check (kind in ('error', 'rejection')),
  message  text not null check (char_length(message) <= 300),
  source   text check (char_length(source) <= 200),
  line     integer,
  col      integer,
  version  text check (char_length(version) <= 40),
  browser  text check (char_length(browser) <= 40),
  view     text check (char_length(view) <= 20),
  page     text check (char_length(page) <= 100)
);
create index if not exists client_errors_at on public.client_errors (at desc);
alter table public.client_errors enable row level security;
revoke all on public.client_errors from anon, authenticated;

-- Masks e-mails, long numbers (phones) and token-like strings, drops URL query strings, then cuts to n.
create or replace function public._scrub_error_text(p text, n integer) returns text
language sql immutable set search_path = public as $$
  select nullif(left(btrim(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(
           coalesce(p, ''),
           '(https?://[^\s?#''"]+)[?#][^\s''"]*', '\1', 'g'),
           '[A-Za-z0-9_.+-]+@[A-Za-z0-9-]+\.[A-Za-z0-9.-]+', '<email>', 'g'),
           '[A-Za-z0-9_-]{32,}', '<token>', 'g'),
           '\+?[0-9][0-9 -]{6,}[0-9]', '<number>', 'g'),
           '\s+', ' ', 'g')), n), '')
$$;
revoke all on function public._scrub_error_text(text, integer) from public, anon, authenticated;

create or replace function public.log_client_error(
  p_message text, p_source text default null, p_line integer default null, p_col integer default null,
  p_kind text default 'error', p_version text default null, p_browser text default null,
  p_view text default null, p_page text default null)
returns jsonb language plpgsql security definer set search_path = public as $$
declare
  v_msg text := _scrub_error_text(p_message, 300);
begin
  if v_msg is null then return jsonb_build_object('status', 'ignored'); end if;
  -- One global ceiling: a broken release can flood this, and so could someone scripting the RPC.
  if (select count(*) from client_errors where at > now() - interval '1 hour') >= 5000 then
    return jsonb_build_object('status', 'rate_limited');
  end if;
  insert into client_errors (kind, message, source, line, col, version, browser, view, page)
  values (case when p_kind = 'rejection' then 'rejection' else 'error' end, v_msg,
          _scrub_error_text(split_part(split_part(p_source, '?', 1), '#', 1), 200),
          case when p_line between 0 and 10000000 then p_line end, case when p_col between 0 and 10000000 then p_col end,
          _scrub_error_text(p_version, 40), _scrub_error_text(p_browser, 40),
          _scrub_error_text(p_view, 20), _scrub_error_text(split_part(p_page, '?', 1), 100));
  -- Housekeeping, now and then: keep 30 days.
  if random() < 0.01 then delete from client_errors where at < now() - interval '30 days'; end if;
  return jsonb_build_object('status', 'ok');
end $$;
revoke all on function public.log_client_error(text, text, integer, integer, text, text, text, text, text) from public;
grant execute on function public.log_client_error(text, text, integer, integer, text, text, text, text, text) to anon, authenticated;

-- ---------------------------------------------------------------- the team's view
create schema if not exists analytics;
drop view if exists analytics.client_errors_daily;
create view analytics.client_errors_daily as
  select (e.at at time zone 'Asia/Kolkata')::date as day, e.message, coalesce(e.source, '') as source,
         count(*) as n, min(e.at) as first_seen, max(e.at) as last_seen,
         string_agg(distinct e.browser, ', ') as browsers,
         string_agg(distinct e.view, ', ') as views,
         string_agg(distinct e.version, ', ') as versions,
         string_agg(distinct e.line::text, ', ') as lines
  from public.client_errors e
  group by 1, 2, 3
  order by 1 desc, 4 desc;
revoke all on analytics.client_errors_daily from anon, authenticated;
