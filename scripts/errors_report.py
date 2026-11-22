"""Daily health lines for the analytics report: app errors in the last 24 hours, and database / storage size.

    SUPABASE_ACCESS_TOKEN=… python -m scripts.errors_report

Reads analytics.client_errors_daily (supabase/migrations/*_client_errors.sql) through the Supabase Management API
and prints Markdown for the job summary. Error text comes from browsers, so every cell is cut short and put in a
code span (nothing in it renders as a link or HTML). Never fails the job: a missing token, a missing view (the
migration not applied yet) or an API error each print one line and exit 0. Stdlib only.

Quota: the Management API has no cheap, documented endpoint for plan usage (egress, monthly active users), so
this reports what SQL can measure exactly: database size and the moments bucket against the Free plan limits.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = "https://api.supabase.com/v1"
FREE_DB_MB, FREE_STORAGE_MB = 500, 1024        # Supabase Free plan (docs/product/COMMUNITY.md, "Free-tier budget")

ERRORS_SQL = """
select message, source, sum(n)::int as n, max(last_seen) as last_seen,
       string_agg(distinct browsers, ', ') as browsers, string_agg(distinct views, ', ') as views
from analytics.client_errors_daily
where last_seen > now() - interval '24 hours'
group by 1, 2 order by 3 desc, 4 desc limit 10
"""
TOTAL_SQL = "select coalesce(sum(n), 0)::int as n, count(*)::int as kinds from analytics.client_errors_daily where last_seen > now() - interval '24 hours'"
SIZE_SQL = """
select pg_database_size(current_database())::bigint as db_bytes,
       (select coalesce(sum((metadata->>'size')::bigint), 0) from storage.objects where bucket_id = 'moments')::bigint as storage_bytes,
       (select count(*) from storage.objects where bucket_id = 'moments')::int as files
"""


def project_ref():
    s = (ROOT / "app" / "config.js").read_text(encoding="utf-8")
    m = re.search(r"url: 'https://([a-z0-9]+)\.supabase\.co'", s)
    return m.group(1) if m else None


def query(token, ref, sql):
    req = urllib.request.Request(f"{API}/projects/{ref}/database/query", data=json.dumps({"query": sql}).encode(),
                                 headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json",
                                          "User-Agent": "pujo-parikrama-report"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def cell(s, n=90):
    """Untrusted text → one short, inert table cell."""
    s = " ".join(str(s or "").split()).replace("`", "'").replace("|", "/")
    s = s if len(s) <= n else s[: n - 1] + "…"
    return f"`{s}`" if s else ""


def errors_md(rows, total):
    out = ["## Errors (last 24 h)", ""]
    if not total or not int(total.get("n") or 0):
        return out + ["No app errors reported in the last 24 hours.", ""]
    out += [f"**{total['n']}** error reports, {total['kinds']} distinct (each phone sends an error once per page load). "
            "Counts cover each error's day (IST). Full list: `analytics.client_errors_daily`.", "",
            "| Error | File | Times | Browsers | Screens |", "|---|---|---:|---|---|"]
    out += [f"| {cell(r.get('message'))} | {cell(r.get('source'), 40)} | {r.get('n', 0)} | {cell(r.get('browsers'), 50)} | "
            f"{cell(r.get('views'), 30)} |" for r in rows]
    return out + [""]


def size_md(s):
    db, st = float(s.get("db_bytes") or 0) / 2**20, float(s.get("storage_bytes") or 0) / 2**20   # bigints may come back as strings
    return ["## Backend size", "",
            f"Database **{db:.0f} MB** of {FREE_DB_MB} MB ({db / FREE_DB_MB:.0%}) · Moments storage **{st:.0f} MB** of "
            f"{FREE_STORAGE_MB} MB ({st / FREE_STORAGE_MB:.0%}, {s.get('files', 0)} files), against the Free plan limits. "
            "Egress and monthly active users aren't available from the API: see Supabase → Usage.", ""]


def build(token, ref, q=query):
    out = []
    try:
        out += errors_md(q(token, ref, ERRORS_SQL), (q(token, ref, TOTAL_SQL) or [{}])[0])
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace") if hasattr(e, "read") else ""
        why = "the client_errors migration isn't applied yet" if "client_errors_daily" in body or "does not exist" in body \
            else f"the API answered {e.code}"
        out += ["## Errors (last 24 h)", "", f"Not available: {why}.", ""]
    except Exception as e:  # network, JSON: never fail the report
        out += ["## Errors (last 24 h)", "", f"Not available ({type(e).__name__}).", ""]
    try:
        out += size_md((q(token, ref, SIZE_SQL) or [{}])[0])
    except Exception as e:
        out += ["## Backend size", "", f"Not available ({type(e).__name__}).", ""]
    return "\n".join(out)


def main():
    token = os.environ.get("SUPABASE_ACCESS_TOKEN")
    ref = project_ref()
    if not token or not ref:
        print("## Errors (last 24 h)\n\nSkipped: " + ("SUPABASE_ACCESS_TOKEN is not set." if not token else "no Supabase project in app/config.js."))
        return
    print(build(token, ref))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # belt and braces: this section must never fail the daily report
        print(f"## Errors (last 24 h)\n\nNot available ({type(e).__name__}).")
    sys.exit(0)
