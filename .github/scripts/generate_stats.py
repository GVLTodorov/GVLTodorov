#!/usr/bin/env python3
"""Generate GitHub profile stat cards (SVG + JSON) from the GraphQL API.

Uses the token's own account (`viewer`), so private repositories and private
contributions are included when the token has the `repo` + `read:user` scopes.
Only aggregate numbers are written out - no private repository names.

Environment:
  GH_STATS_TOKEN   personal access token (required)
  OUTPUT_DIR       where to write files (default: .github/stats)
  AFFILIATIONS     repo affiliations to include, comma separated
                   (default: OWNER; can add COLLABORATOR,ORGANIZATION_MEMBER)
  INCLUDE_FORKS    "true" to count forked repos (default: false)
  INCLUDE_ARCHIVED "true"/"false" (default: true)
  EXCLUDE_REPOS    comma-separated repo names (or owner/name) to skip
  EXCLUDE_LANGS    comma-separated languages to skip (e.g. "HTML,CSS")
  LANGS_COUNT      number of languages on the card (default: 8)
"""

from __future__ import annotations

import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.request
from html import escape
from pathlib import Path

API = "https://api.github.com/graphql"


def env_list(name: str) -> list[str]:
    return [x.strip() for x in os.environ.get(name, "").split(",") if x.strip()]


def env_bool(name: str, default: bool) -> bool:
    v = os.environ.get(name)
    return default if v is None or v == "" else v.strip().lower() in ("1", "true", "yes")


TOKEN = os.environ.get("GH_STATS_TOKEN") or os.environ.get("GITHUB_TOKEN")
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", ".github/stats"))
AFFILIATIONS = [a.upper() for a in env_list("AFFILIATIONS")] or ["OWNER"]
INCLUDE_FORKS = env_bool("INCLUDE_FORKS", False)
INCLUDE_ARCHIVED = env_bool("INCLUDE_ARCHIVED", True)
EXCLUDE_REPOS = {r.lower() for r in env_list("EXCLUDE_REPOS")}
EXCLUDE_LANGS = {l.lower() for l in env_list("EXCLUDE_LANGS")}
LANGS_COUNT = int(os.environ.get("LANGS_COUNT") or 8)


# --------------------------------------------------------------------------- API

def gql(query: str, variables: dict | None = None, retries: int = 4) -> dict:
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    for attempt in range(retries):
        req = urllib.request.Request(
            API,
            data=body,
            headers={
                "Authorization": f"bearer {TOKEN}",
                "Content-Type": "application/json",
                "User-Agent": "profile-stats-generator",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                payload = json.load(resp)
        except urllib.error.HTTPError as e:
            if e.code in (502, 503, 504) and attempt < retries - 1:
                time.sleep(2 ** attempt * 3)
                continue
            raise SystemExit(f"GraphQL HTTP {e.code}: {e.read().decode(errors='replace')}")
        except urllib.error.URLError:
            if attempt < retries - 1:
                time.sleep(2 ** attempt * 3)
                continue
            raise
        if payload.get("errors"):
            # Contribution queries occasionally time out on the server side.
            if attempt < retries - 1 and not payload.get("data"):
                time.sleep(2 ** attempt * 3)
                continue
            raise SystemExit(f"GraphQL errors: {json.dumps(payload['errors'], indent=2)}")
        return payload["data"]
    raise SystemExit("GraphQL request failed after retries")


Q_USER = """
query {
  viewer {
    login name createdAt
    followers { totalCount }
    pullRequests { totalCount }
    mergedPullRequests: pullRequests(states: MERGED) { totalCount }
    issues { totalCount }
    contributionsCollection { contributionYears }
  }
}
"""

Q_REPOS = """
query($cursor: String, $aff: [RepositoryAffiliation]) {
  viewer {
    repositories(first: 100, after: $cursor, ownerAffiliations: $aff) {
      pageInfo { hasNextPage endCursor }
      nodes {
        name nameWithOwner isPrivate isFork isArchived
        stargazerCount forkCount
        languages(first: 30, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
  }
}
"""

Q_CONTRIB = """
query($from: DateTime!, $to: DateTime!) {
  viewer {
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      totalPullRequestReviewContributions
      totalRepositoryContributions
      restrictedContributionsCount
      commitContributionsByRepository(maxRepositories: 100) { repository { nameWithOwner } }
      pullRequestContributionsByRepository(maxRepositories: 100) { repository { nameWithOwner } }
      issueContributionsByRepository(maxRepositories: 100) { repository { nameWithOwner } }
      pullRequestReviewContributionsByRepository(maxRepositories: 100) { repository { nameWithOwner } }
    }
  }
}
"""


def iso(d: dt.datetime) -> str:
    return d.strftime("%Y-%m-%dT%H:%M:%SZ")


def contributions(start: dt.datetime, end: dt.datetime) -> dict:
    c = gql(Q_CONTRIB, {"from": iso(start), "to": iso(end)})["viewer"]["contributionsCollection"]
    repos = set()
    for key in (
        "commitContributionsByRepository",
        "pullRequestContributionsByRepository",
        "issueContributionsByRepository",
        "pullRequestReviewContributionsByRepository",
    ):
        repos.update(x["repository"]["nameWithOwner"] for x in c[key])
    return {
        "commits": c["totalCommitContributions"] + c["restrictedContributionsCount"],
        "prs": c["totalPullRequestContributions"],
        "issues": c["totalIssueContributions"],
        "reviews": c["totalPullRequestReviewContributions"],
        "repos_created": c["totalRepositoryContributions"],
        "repos": repos,
    }


def collect() -> dict:
    user = gql(Q_USER)["viewer"]
    login = user["login"]

    # ---- repositories & languages
    repos, cursor = [], None
    while True:
        page = gql(Q_REPOS, {"cursor": cursor, "aff": AFFILIATIONS})["viewer"]["repositories"]
        repos.extend(page["nodes"])
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]

    def keep(r: dict) -> bool:
        if r["isFork"] and not INCLUDE_FORKS:
            return False
        if r["isArchived"] and not INCLUDE_ARCHIVED:
            return False
        if r["name"].lower() in EXCLUDE_REPOS or r["nameWithOwner"].lower() in EXCLUDE_REPOS:
            return False
        return True

    repos = [r for r in repos if keep(r)]

    langs: dict[str, dict] = {}
    for r in repos:
        for e in r["languages"]["edges"]:
            name = e["node"]["name"]
            if name.lower() in EXCLUDE_LANGS:
                continue
            entry = langs.setdefault(name, {"name": name, "color": e["node"]["color"], "size": 0, "repos": 0})
            entry["size"] += e["size"]
            entry["repos"] += 1
    total_bytes = sum(l["size"] for l in langs.values()) or 1
    languages = sorted(langs.values(), key=lambda l: l["size"], reverse=True)
    for l in languages:
        l["percent"] = round(l["size"] * 100 / total_bytes, 2)

    # ---- contributions (API limits each window to one year)
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    all_time = {"commits": 0, "prs": 0, "issues": 0, "reviews": 0, "repos_created": 0}
    contributed: set[str] = set()
    per_year = {}
    for year in sorted(user["contributionsCollection"]["contributionYears"]):
        start = dt.datetime(year, 1, 1, tzinfo=dt.timezone.utc)
        end = min(dt.datetime(year, 12, 31, 23, 59, 59, tzinfo=dt.timezone.utc), now)
        c = contributions(start, end)
        per_year[str(year)] = c["commits"]
        for k in all_time:
            all_time[k] += c[k]
        contributed |= c["repos"]
    last_year = contributions(now - dt.timedelta(days=365), now)

    own = {r["nameWithOwner"].lower() for r in repos}
    external = {r for r in contributed if not r.lower().startswith(login.lower() + "/") and r.lower() not in own}

    return {
        "generated_at": iso(now),
        "login": login,
        "name": user["name"] or login,
        "followers": user["followers"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in repos),
        "forks": sum(r["forkCount"] for r in repos),
        "repos_total": len(repos),
        "repos_public": sum(1 for r in repos if not r["isPrivate"]),
        "repos_private": sum(1 for r in repos if r["isPrivate"]),
        "commits_last_year": last_year["commits"],
        "commits_all_time": all_time["commits"],
        "commits_per_year": per_year,
        "prs_total": user["pullRequests"]["totalCount"],
        "prs_merged": user["mergedPullRequests"]["totalCount"],
        "issues_total": user["issues"]["totalCount"],
        "reviews_all_time": all_time["reviews"],
        "contributed_to": len(contributed),
        "contributed_to_external": len(external),
        "languages": languages,
        "languages_total_bytes": total_bytes,
        "settings": {
            "affiliations": AFFILIATIONS,
            "include_forks": INCLUDE_FORKS,
            "include_archived": INCLUDE_ARCHIVED,
            "excluded_repos": len(EXCLUDE_REPOS),
            "excluded_languages": sorted(EXCLUDE_LANGS),
        },
    }


# --------------------------------------------------------------------------- SVG

FONTS = """
  .title { font: 600 18px 'Segoe UI', Ubuntu, -apple-system, sans-serif; }
  .label { font: 400 14px 'Segoe UI', Ubuntu, -apple-system, sans-serif; }
  .value { font: 600 14px 'Segoe UI', Ubuntu, -apple-system, sans-serif; }
  .muted { font: 400 11px 'Segoe UI', Ubuntu, -apple-system, sans-serif; }
  .lang  { font: 400 12px 'Segoe UI', Ubuntu, -apple-system, sans-serif; }
  .seg   { stroke-width: 2; }
"""

PALETTES = {
    "light": {"bg": "#ffffff", "border": "#d0d7de", "title": "#0969da", "label": "#424a53",
              "value": "#1f2328", "muted": "#6e7781", "icon": "#0969da", "track": "#eaeef2"},
    "dark": {"bg": "#0d1117", "border": "#30363d", "title": "#58a6ff", "label": "#c9d1d9",
             "value": "#f0f6fc", "muted": "#8b949e", "icon": "#58a6ff", "track": "#21262d"},
}


def colors(p: dict) -> str:
    return (
        f".bg {{ fill: {p['bg']}; stroke: {p['border']}; }} .title {{ fill: {p['title']}; }} "
        f".label, .lang {{ fill: {p['label']}; }} .value {{ fill: {p['value']}; }} "
        f".muted {{ fill: {p['muted']}; }} .icon {{ fill: {p['icon']}; }} "
        f".track {{ fill: {p['track']}; }} .seg {{ stroke: {p['bg']}; }}"
    )


# THEME: "dark" (default), "light", or "auto" (follows the viewer's OS/GitHub theme)
THEME = (os.environ.get("THEME") or "dark").strip().lower()
if THEME == "auto":
    STYLE = FONTS + colors(PALETTES["light"]) + \
        "\n  @media (prefers-color-scheme: dark) { " + colors(PALETTES["dark"]) + " }\n"
else:
    STYLE = FONTS + colors(PALETTES.get(THEME, PALETTES["dark"])) + "\n"

# Octicons (16px), MIT licensed - https://primer.style/octicons
ICONS = {
    "star": "M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Zm0 2.445L6.615 5.5a.75.75 0 0 1-.564.41l-3.097.45 2.24 2.184a.75.75 0 0 1 .216.664l-.528 3.084 2.769-1.456a.75.75 0 0 1 .698 0l2.77 1.456-.53-3.084a.75.75 0 0 1 .216-.664l2.24-2.183-3.096-.45a.75.75 0 0 1-.564-.41L8 2.694Z",
    "commit": "M11.93 8.5a4.002 4.002 0 0 1-7.86 0H.75a.75.75 0 0 1 0-1.5h3.32a4.002 4.002 0 0 1 7.86 0h3.32a.75.75 0 0 1 0 1.5Zm-1.43-.75a2.5 2.5 0 1 0-5 0 2.5 2.5 0 0 0 5 0Z",
    "history": "m.427 1.927 1.215 1.215a8.002 8.002 0 1 1-1.6 5.685.75.75 0 1 1 1.493-.154 6.5 6.5 0 1 0 1.18-4.458l1.358 1.358A.25.25 0 0 1 3.896 6H.25A.25.25 0 0 1 0 5.75V2.104a.25.25 0 0 1 .427-.177ZM7.75 4a.75.75 0 0 1 .75.75v2.992l2.028.812a.75.75 0 0 1-.557 1.392l-2.5-1A.751.751 0 0 1 7 8.25v-3.5A.75.75 0 0 1 7.75 4Z",
    "pr": "M1.5 3.25a2.25 2.25 0 1 1 3 2.122v5.256a2.251 2.251 0 1 1-1.5 0V5.372A2.25 2.25 0 0 1 1.5 3.25Zm5.677-.177L9.573.677A.25.25 0 0 1 10 .854V2.5h1A2.5 2.5 0 0 1 13.5 5v5.628a2.251 2.251 0 1 1-1.5 0V5a1 1 0 0 0-1-1h-1v1.646a.25.25 0 0 1-.427.177L7.177 3.427a.25.25 0 0 1 0-.354ZM3.75 2.5a.75.75 0 1 0 0 1.5.75.75 0 0 0 0-1.5Zm0 9.5a.75.75 0 1 0 0 1.5.75.75 0 0 0 0-1.5Zm8.25.75a.75.75 0 1 0 1.5 0 .75.75 0 0 0-1.5 0Z",
    "issue": "M8 9.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3Z M8 0a8 8 0 1 1 0 16A8 8 0 0 1 8 0ZM1.5 8a6.5 6.5 0 1 0 13 0 6.5 6.5 0 0 0-13 0Z",
    "eye": "M8 2c1.981 0 3.671.992 4.933 2.078 1.27 1.091 2.187 2.345 2.637 3.023a1.62 1.62 0 0 1 0 1.798c-.45.678-1.367 1.932-2.637 3.023C11.67 13.008 9.981 14 8 14c-1.981 0-3.671-.992-4.933-2.078C1.797 10.83.88 9.576.43 8.898a1.62 1.62 0 0 1 0-1.798c.45-.677 1.367-1.931 2.637-3.022C4.33 2.992 6.019 2 8 2ZM1.679 7.932a.12.12 0 0 0 0 .136c.411.622 1.241 1.75 2.366 2.717C5.176 11.758 6.527 12.5 8 12.5c1.473 0 2.825-.742 3.955-1.715 1.124-.967 1.954-2.096 2.366-2.717a.12.12 0 0 0 0-.136c-.412-.621-1.242-1.75-2.366-2.717C10.824 4.242 9.473 3.5 8 3.5c-1.473 0-2.825.742-3.955 1.715-1.124.967-1.954 2.096-2.366 2.717ZM8 10a2 2 0 1 1-.001-3.999A2 2 0 0 1 8 10Z",
    "repo": "M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 0 1 .25-.25h3.5a.25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2l-1.45-1.087a.249.249 0 0 0-.3 0L5.4 15.7a.25.25 0 0 1-.4-.2Z",
    "people": "M2 5.5a3.5 3.5 0 1 1 5.898 2.549 5.508 5.508 0 0 1 3.034 4.084.75.75 0 1 1-1.482.235 4 4 0 0 0-7.9 0 .75.75 0 0 1-1.482-.236A5.507 5.507 0 0 1 3.102 8.05 3.493 3.493 0 0 1 2 5.5ZM11 4a3.001 3.001 0 0 1 2.22 5.018 5.01 5.01 0 0 1 2.56 3.012.749.749 0 0 1-.885.954.752.752 0 0 1-.549-.514 3.507 3.507 0 0 0-2.522-2.372.75.75 0 0 1-.574-.73v-.352a.75.75 0 0 1 .416-.672A1.5 1.5 0 0 0 11 5.5.75.75 0 0 1 11 4Zm-5.5-.5a2 2 0 1 0-.001 3.999A2 2 0 0 0 5.5 3.5Z",
}


def fmt(n: int) -> str:
    return f"{n:,}"


def card(width: int, height: int, title: str, body: str, footer: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">
<title>{escape(title)}</title>
<style>{STYLE}</style>
<rect class="bg" x="0.5" y="0.5" rx="6" width="{width - 1}" height="{height - 1}"/>
<text class="title" x="25" y="36">{escape(title)}</text>
{body}
<text class="muted" x="{width - 25}" y="{height - 14}" text-anchor="end">{escape(footer)}</text>
</svg>
"""


def stats_svg(s: dict) -> str:
    rows = [
        ("star", "Stars earned", fmt(s["stars"])),
        ("commit", "Commits (last 12 months)", fmt(s["commits_last_year"])),
        ("history", "Commits (all time)", fmt(s["commits_all_time"])),
        ("pr", "Pull requests (merged)", f"{fmt(s['prs_total'])} ({fmt(s['prs_merged'])})"),
        ("issue", "Issues opened", fmt(s["issues_total"])),
        ("eye", "Code reviews", fmt(s["reviews_all_time"])),
        ("repo", "Repositories (public / private)", f"{fmt(s['repos_public'])} / {fmt(s['repos_private'])}"),
        ("people", "Repos contributed to (external)", f"{fmt(s['contributed_to'])} ({fmt(s['contributed_to_external'])})"),
    ]
    width, top, step = 495, 62, 26
    parts = []
    for i, (icon, label, value) in enumerate(rows):
        y = top + i * step
        parts.append(
            f'<g transform="translate(25,{y})">'
            f'<path class="icon" d="{ICONS[icon]}"/>'
            f'<text class="label" x="26" y="12.5">{escape(label)}:</text>'
            f'<text class="value" x="{width - 50}" y="12.5" text-anchor="end">{escape(value)}</text>'
            f"</g>"
        )
    height = top + len(rows) * step + 30
    updated = s["generated_at"][:10]
    return card(width, height, f"{s['name']}'s GitHub Stats", "\n".join(parts), f"Public + private · updated {updated}")


def languages_svg(s: dict) -> str:
    langs = s["languages"][:LANGS_COUNT]
    shown = sum(l["size"] for l in langs) or 1
    other = max(s["languages_total_bytes"] - shown, 0)
    width, bar_x, bar_w, bar_y = 495, 25, 445, 54

    segments, x = [], float(bar_x)
    for l in langs:
        w = bar_w * l["size"] / s["languages_total_bytes"]
        segments.append(f'<rect class="seg" x="{x:.2f}" y="{bar_y - 1}" width="{w:.2f}" height="10" fill="{l["color"] or "#8b949e"}"/>')
        x += w
    if other:
        segments.append(f'<rect class="track" x="{x:.2f}" y="{bar_y}" width="{bar_x + bar_w - x:.2f}" height="8"/>')

    legend, cols, col_w, row_h = [], 2, 222, 24
    for i, l in enumerate(langs):
        cx = bar_x + (i % cols) * col_w
        cy = bar_y + 32 + (i // cols) * row_h
        legend.append(
            f'<g transform="translate({cx},{cy})">'
            f'<circle cx="5" cy="-4" r="5" fill="{l["color"] or "#8b949e"}"/>'
            f'<text class="lang" x="16" y="0">{escape(l["name"])} {l["percent"]:.2f}%</text>'
            f"</g>"
        )
    rows = (len(langs) + cols - 1) // cols
    height = bar_y + 32 + rows * row_h + 18

    body = (
        f'<clipPath id="bar"><rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="8" rx="4"/></clipPath>'
        f'<rect class="track" x="{bar_x}" y="{bar_y}" width="{bar_w}" height="8" rx="4"/>'
        f'<g clip-path="url(#bar)">{"".join(segments)}</g>\n' + "\n".join(legend)
    )
    footer = f"{s['repos_total']} repos · updated {s['generated_at'][:10]}"
    return card(width, height, "Most Used Languages", body, footer)


# --------------------------------------------------------------------------- main

def main() -> None:
    if not TOKEN:
        sys.exit("GH_STATS_TOKEN is not set")
    stats = collect()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "stats.svg").write_text(stats_svg(stats), encoding="utf-8")
    (OUTPUT_DIR / "languages.svg").write_text(languages_svg(stats), encoding="utf-8")
    (OUTPUT_DIR / "stats.json").write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")

    print(f"Stats for {stats['login']} written to {OUTPUT_DIR}/")
    for k in ("stars", "commits_last_year", "commits_all_time", "prs_total", "issues_total",
              "reviews_all_time", "repos_public", "repos_private", "contributed_to"):
        print(f"  {k:20} {stats[k]}")
    for l in stats["languages"][:LANGS_COUNT]:
        print(f"  {l['name']:20} {l['percent']:6.2f}%")


if __name__ == "__main__":
    main()
