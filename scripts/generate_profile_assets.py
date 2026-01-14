from __future__ import annotations

import datetime as dt
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "generated"


@dataclass(frozen=True)
class RepoCommitStat:
    name_with_owner: str
    url: str
    commit_contributions: int


@dataclass(frozen=True)
class RepoInfo:
    name_with_owner: str
    url: str
    stars: int
    primary_language: str | None
    pushed_at: str | None
    total_commits: int


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


def _graphql(token: str, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    response = requests.post(
        "https://api.github.com/graphql",
        headers=headers,
        json={"query": query, "variables": variables or {}},
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("errors"):
        raise RuntimeError(f"GraphQL errors: {payload['errors']}")
    return payload["data"]


def fetch_commit_contributions_by_repo(token: str, username: str, days: int = 365) -> list[RepoCommitStat]:
    to_date = dt.datetime.now(dt.timezone.utc)
    from_date = to_date - dt.timedelta(days=days)

    query = """
    query($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        contributionsCollection(from: $from, to: $to) {
          commitContributionsByRepository(maxRepositories: 100) {
            repository { nameWithOwner url }
            contributions { totalCount }
          }
        }
      }
    }
    """

    data = _graphql(
        token,
        query,
        {
            "login": username,
            "from": from_date.isoformat(),
            "to": to_date.isoformat(),
        },
    )

    items = (
        data.get("user", {})
        .get("contributionsCollection", {})
        .get("commitContributionsByRepository", [])
    )

    stats: list[RepoCommitStat] = []
    for item in items:
        repo = item.get("repository") or {}
        contrib = item.get("contributions") or {}
        total = int(contrib.get("totalCount") or 0)
        if total <= 0:
            continue
        stats.append(
            RepoCommitStat(
                name_with_owner=str(repo.get("nameWithOwner")),
                url=str(repo.get("url")),
                commit_contributions=total,
            )
        )

    stats.sort(key=lambda s: s.commit_contributions, reverse=True)
    return stats


def fetch_all_repositories(token: str, username: str) -> list[RepoInfo]:
    query = """
    query($login: String!, $cursor: String) {
      user(login: $login) {
        repositories(
          first: 100,
          after: $cursor,
          ownerAffiliations: OWNER,
          privacy: PUBLIC,
          orderBy: {field: PUSHED_AT, direction: DESC}
        ) {
          pageInfo { hasNextPage endCursor }
          nodes {
            nameWithOwner
            url
            stargazerCount
            pushedAt
            primaryLanguage { name }
            defaultBranchRef {
              target {
                ... on Commit {
                  history(first: 0) {
                    totalCount
                  }
                }
              }
            }
          }
        }
      }
    }
    """

    repos: list[RepoInfo] = []
    cursor: str | None = None

    while True:
        data = _graphql(token, query, {"login": username, "cursor": cursor})
        container = data.get("user", {}).get("repositories", {})
        nodes = container.get("nodes", []) or []

        for node in nodes:
            name = str(node.get("nameWithOwner"))
            url = str(node.get("url"))
            stars = int(node.get("stargazerCount") or 0)
            pushed_at = node.get("pushedAt")
            lang = (node.get("primaryLanguage") or {}).get("name")
            
            # Get total commits from default branch
            total_commits = 0
            default_branch = node.get("defaultBranchRef")
            if default_branch:
                target = default_branch.get("target") or {}
                history = target.get("history") or {}
                total_commits = int(history.get("totalCount") or 0)
            
            print(f"  → {name}: {total_commits} commits")
            
            repos.append(
                RepoInfo(
                    name_with_owner=name,
                    url=url,
                    stars=stars,
                    primary_language=str(lang) if lang else None,
                    pushed_at=str(pushed_at) if pushed_at else None,
                    total_commits=total_commits,
                )
            )

        page = container.get("pageInfo", {})
        if not page.get("hasNextPage"):
            break
        cursor = page.get("endCursor")

    return repos


def render_repo_card_svg(repo: RepoInfo, out_path: Path, index: int) -> None:
    """Generate a beautiful SVG card for a single repository"""
    width = 440
    height = 140
    
    repo_name = repo.name_with_owner.split('/')[-1]
    lang = repo.primary_language or "Other"
    
    # Language colors
    lang_colors = {
        "Python": "#3776AB", "JavaScript": "#F7DF1E", "TypeScript": "#3178C6",
        "Java": "#007396", "C#": "#239120", "C++": "#00599C", "Go": "#00ADD8",
        "Rust": "#000000", "Ruby": "#CC342D", "PHP": "#777BB4", "Swift": "#FA7343",
        "Kotlin": "#7F52FF", "Dart": "#0175C2", "HTML": "#E34F26", "CSS": "#1572B6"
    }
    color = lang_colors.get(lang, "#8A2BE2")
    
    # Format date
    try:
        pushed = dt.datetime.fromisoformat(repo.pushed_at.replace("Z", "+00:00")).strftime("%d/%m/%Y") if repo.pushed_at else "—"
    except:
        pushed = "—"
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <linearGradient id="grad{index}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <rect width="{width}" height="{height}" rx="10" fill="url(#grad{index})"/>
  <rect x="8" y="8" width="{width-16}" height="{height-16}" rx="8" fill="#1a1b27" opacity="0.95"/>
  
  <g transform="translate(20, 25)">
    <text x="0" y="0" fill="#c9d1d9" font-family="ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Arial" font-size="18" font-weight="700">
      📦 {_escape_xml(repo_name)}
    </text>
    
    <g transform="translate(0, 30)">
      <rect x="0" y="0" width="100" height="24" rx="12" fill="{color}" opacity="0.2"/>
      <circle cx="12" cy="12" r="5" fill="{color}"/>
      <text x="22" y="16" fill="{color}" font-family="ui-sans-serif,system-ui" font-size="13" font-weight="600">{_escape_xml(lang)}</text>
    </g>
    
    <g transform="translate(0, 65)">
      <text x="0" y="0" fill="#8b949e" font-family="ui-sans-serif,system-ui" font-size="13">
        ⭐ <tspan fill="#c9d1d9" font-weight="600">{repo.stars}</tspan>
        <tspan dx="20">📅 {_escape_xml(pushed)}</tspan>
      </text>
    </g>
  </g>
</svg>'''
    
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(svg, encoding="utf-8")


def _escape_xml(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def render_combined_repos_svg(
    username: str,
    repos: list[RepoInfo],
    out_path: Path,
) -> None:
    """Generate a beautiful combined SVG showing all repos with commits, stars, and dates"""
    width = 900
    padding = 24
    row_h = 55
    title_h = 55
    
    # Filter out the profile repo itself and use total_commits from RepoInfo
    filtered = []
    
    for r in repos:
        if r.name_with_owner.split('/')[-1].lower() != username.lower():
            filtered.append((r, r.total_commits))
    
    # Sort by commits (descending)
    filtered.sort(key=lambda x: x[1], reverse=True)
    
    if not filtered:
        height = 200
        bg = "#0d1117"
        card = "#161b22"
        text = "#c9d1d9"
        muted = "#8b949e"
        
        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
            f'<rect x="0" y="0" width="{width}" height="{height}" rx="14" fill="{bg}"/>',
            f'<rect x="12" y="12" width="{width-24}" height="{height-24}" rx="12" fill="{card}"/>',
            f'<text x="{padding}" y="80" fill="{text}" font-family="ui-sans-serif,system-ui" font-size="18" font-weight="700">Nenhum repositório encontrado</text>',
            "</svg>"
        ]
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("\n".join(parts), encoding="utf-8")
        return
    
    height = padding * 2 + title_h + row_h * len(filtered) + 20
    max_commits = max((c for _, c in filtered), default=1) or 1
    
    bg = "#0d1117"
    card = "#161b22"
    text = "#c9d1d9"
    muted = "#8b949e"
    bar = "#8A2BE2"
    bar_secondary = "#a855f7"
    bar_bg = "#21262d"
    
    def scale_bar(v: int, max_width: int = 280) -> int:
        if max_commits == 0:
            return 0
        return int((v / max_commits) * max_width)
    
    def fmt_date(iso: str | None) -> str:
        if not iso:
            return "—"
        try:
            return dt.datetime.fromisoformat(iso.replace("Z", "+00:00")).strftime("%d/%m/%y")
        except:
            return iso[:10] if iso else "—"
    
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "<defs>",
        '<linearGradient id="barGradient" x1="0%" y1="0%" x2="100%" y2="0%">',
        f'  <stop offset="0%" style="stop-color:{bar};stop-opacity:1" />',
        f'  <stop offset="100%" style="stop-color:{bar_secondary};stop-opacity:1" />',
        '</linearGradient>',
        "</defs>",
        "<style>",
        ".title{font:700 20px ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Arial;}",
        ".sub{font:500 13px ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Arial;}",
        ".repo-name{font:700 16px ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Arial;}",
        ".stat{font:600 13px ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Arial;}",
        "</style>",
        f'<rect x="0" y="0" width="{width}" height="{height}" rx="14" fill="{bg}"/>',
        f'<rect x="12" y="12" width="{width-24}" height="{height-24}" rx="12" fill="{card}"/>',
    ]
    
    # Title
    title = "Repositórios — Atividade e Stats"
    subtitle = f"@{username} • {len(filtered)} repos com total de {sum(c for _, c in filtered)} commits"
    parts.append(f'<text x="{padding}" y="{padding + 20}" class="title" fill="{text}">{_escape_xml(title)}</text>')
    parts.append(f'<text x="{padding}" y="{padding + 42}" class="sub" fill="{muted}">{_escape_xml(subtitle)}</text>')
    
    start_y = padding + title_h + 15
    
    for i, (repo, commits) in enumerate(filtered):
        y = start_y + i * row_h
        repo_name = repo.name_with_owner.split('/')[-1]
        display_name = repo_name if len(repo_name) <= 30 else repo_name[:27] + "..."
        
        pushed = fmt_date(repo.pushed_at)
        
        # Repo name (left) - MAIOR e mais DESTACADO
        parts.append(f'<text x="{padding}" y="{y + 10}" class="repo-name" fill="{text}">📦 {_escape_xml(display_name)}</text>')
        
        # Commits bar (center)
        bar_x = padding + 260
        bar_y = y - 2
        bar_width = scale_bar(commits, 280)
        parts.append(f'<rect x="{bar_x}" y="{bar_y}" width="280" height="14" rx="7" fill="{bar_bg}"/>')
        if bar_width > 0:
            parts.append(f'<rect x="{bar_x}" y="{bar_y}" width="{bar_width}" height="14" rx="7" fill="url(#barGradient)"/>')
        
        # Stats (right side - below bar)
        stats_y = y + 28
        parts.append(f'<text x="{bar_x}" y="{stats_y}" class="stat" fill="{muted}">💬 {commits} commits</text>')
        parts.append(f'<text x="{bar_x + 100}" y="{stats_y}" class="stat" fill="{muted}">⭐ {repo.stars}</text>')
        parts.append(f'<text x="{bar_x + 170}" y="{stats_y}" class="stat" fill="{muted}">📅 {pushed}</text>')
    
    parts.append("</svg>")
    
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(parts), encoding="utf-8")
    print(f"  → Generated combined SVG with {len(filtered)} repositories")
    print(f"  → File size: {out_path.stat().st_size} bytes")


def render_commits_svg(
    username: str,
    period_label: str,
    stats: list[RepoCommitStat],
    out_path: Path,
    max_rows: int = 15,
) -> None:
    width = 900
    padding = 24
    row_h = 28
    title_h = 42
    bar_h = 10

    rows = stats[:max_rows]
    
    # If no stats, render a placeholder card
    if not rows:
        height = 180
        bg = "#0b1020"
        card = "#111827"
        text = "#e5e7eb"
        muted = "#9ca3af"
        
        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
            f'<rect x="0" y="0" width="{width}" height="{height}" rx="14" fill="{bg}"/>',
            f'<rect x="12" y="12" width="{width-24}" height="{height-24}" rx="12" fill="{card}"/>',
            f'<text x="{padding}" y="60" fill="{text}" font-family="ui-sans-serif,system-ui" font-size="18" font-weight="700">Commits por repositório — {_escape_xml(period_label)}</text>',
            f'<text x="{padding}" y="90" fill="{muted}" font-family="ui-sans-serif,system-ui" font-size="14">Nenhum commit encontrado no período selecionado.</text>',
            f'<text x="{padding}" y="120" fill="{muted}" font-family="ui-sans-serif,system-ui" font-size="13">Isso pode acontecer se este for seu primeiro run ou se não houver atividade recente.</text>',
            "</svg>"
        ]
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("\n".join(parts), encoding="utf-8")
        return
    
    max_value = max((r.commit_contributions for r in rows), default=1)

    height = padding * 2 + title_h + row_h * len(rows) + 10

    bg = "#0d1117"
    card = "#161b22"
    text = "#c9d1d9"
    muted = "#8b949e"
    bar = "#8A2BE2"
    bar_secondary = "#a855f7"
    bar_bg = "#21262d"

    def scale(v: int) -> int:
        bar_w_max = 420
        return int(math.floor((v / max_value) * bar_w_max))

    parts: list[str] = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">')
    
    # Add gradient definitions
    parts.append("<defs>")
    parts.append(f'<linearGradient id="barGradient" x1="0%" y1="0%" x2="100%" y2="0%">')
    parts.append(f'  <stop offset="0%" style="stop-color:{bar};stop-opacity:1" />')
    parts.append(f'  <stop offset="100%" style="stop-color:{bar_secondary};stop-opacity:1" />')
    parts.append('</linearGradient>')
    parts.append("</defs>")
    
    parts.append("<style>")
    parts.append(
        ".title{font:700 18px ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Arial;}"
        ".sub{font:500 12px ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Arial;}"
        ".label{font:600 12px ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Arial;}"
        ".count{font:700 13px ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Arial;}"
    )
    parts.append("</style>")

    parts.append(f'<rect x="0" y="0" width="{width}" height="{height}" rx="14" fill="{bg}"/>')
    parts.append(f'<rect x="12" y="12" width="{width-24}" height="{height-24}" rx="12" fill="{card}"/>')

    title = f"Commits por repositório — {period_label}"
    subtitle = f"@{username} • Top {len(rows)} (por commits)"
    parts.append(f'<text x="{padding}" y="{padding + 18}" class="title" fill="{text}">{_escape_xml(title)}</text>')
    parts.append(f'<text x="{padding}" y="{padding + 38}" class="sub" fill="{muted}">{_escape_xml(subtitle)}</text>')

    start_y = padding + title_h + 16
    for i, r in enumerate(rows):
        y = start_y + i * row_h
        repo_label = r.name_with_owner
        if len(repo_label) > 36:
            repo_label = "…" + repo_label[-35:]

        parts.append(f'<text x="{padding}" y="{y}" class="label" fill="{text}">{_escape_xml(repo_label)}</text>')

        bar_x = padding + 320
        bar_y = y - 10
        parts.append(f'<rect x="{bar_x}" y="{bar_y}" width="420" height="{bar_h}" rx="5" fill="{bar_bg}"/>')
        parts.append(f'<rect x="{bar_x}" y="{bar_y}" width="{scale(r.commit_contributions)}" height="{bar_h}" rx="5" fill="url(#barGradient)"/>')

        parts.append(
            f'<text x="{bar_x + 430}" y="{y}" class="count" fill="{muted}">{r.commit_contributions}</text>'
        )

    parts.append("</svg>")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(parts), encoding="utf-8")
    print(f"  → Generated SVG with {len(rows)} repositories")
    print(f"  → File size: {out_path.stat().st_size} bytes")


def render_repos_markdown(username: str, repos: list[RepoInfo], out_path: Path) -> None:
    lines: list[str] = []
    lines.append(f"# Repositórios ({username})")
    lines.append("")
    lines.append(f"Atualizado automaticamente por GitHub Actions em {dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}.\n")
    lines.append("| Repositório | Linguagem | Stars | Último push |")
    lines.append("|---|---:|---:|---:|")

    def fmt_date(iso: str | None) -> str:
        if not iso:
            return "—"
        try:
            return dt.datetime.fromisoformat(iso.replace("Z", "+00:00")).strftime("%Y-%m-%d")
        except Exception:
            return iso

    for r in repos:
        lang = r.primary_language or "—"
        pushed = fmt_date(r.pushed_at)
        lines.append(f"| [{r.name_with_owner}]({r.url}) | {lang} | {r.stars} | {pushed} |")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_readme_repo_section(username: str, repos: list[RepoInfo]) -> None:
    readme_candidates = [ROOT / "README.md", ROOT / "Readme.md"]
    readme_path = next((p for p in readme_candidates if p.exists()), None)
    if not readme_path:
        raise RuntimeError("README not found (expected README.md or Readme.md)")

    start_marker = "<!-- REPOS-LIST:START -->"
    end_marker = "<!-- REPOS-LIST:END -->"
    content = readme_path.read_text(encoding="utf-8")

    print(f"📖 Reading {readme_path.name}...")
    print(f"   File size: {len(content)} chars")
    print(f"   Looking for: {start_marker}")
    print(f"   Found START at position: {content.find(start_marker)}")
    print(f"   Found END at position: {content.find(end_marker)}")
    
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    if start_idx == -1 or end_idx == -1 or end_idx <= start_idx:
        print("\n❌ Markers not found or invalid!")
        print(f"   START marker found: {start_idx != -1}")
        print(f"   END marker found: {end_idx != -1}")
        if start_idx != -1 and end_idx != -1:
            print(f"   Distance between markers: {end_idx - start_idx} chars")
        print("\nSearching for similar patterns...")
        if "REPOS-LIST" in content:
            print("   ✓ Found 'REPOS-LIST' in file")
            # Show lines with REPOS-LIST
            for i, line in enumerate(content.split('\n'), 1):
                if "REPOS-LIST" in line:
                    print(f"   Line {i}: {repr(line)}")
        raise RuntimeError("Repo markers not found in README. Add REPOS-LIST markers first.")

    def fmt_date(iso: str | None) -> str:
        if not iso:
            return "—"
        try:
            return dt.datetime.fromisoformat(iso.replace("Z", "+00:00")).strftime("%Y-%m-%d")
        except Exception:
            return iso

    # Render combined repos (no need for separate cards since we have the overview SVG)
    lines: list[str] = []
    lines.append(start_marker)
    lines.append("")
    lines.append(f"<p align='center'><em>📅 Atualizado em {dt.datetime.now(dt.timezone.utc).strftime('%d/%m/%Y às %H:%M UTC')}</em></p>")
    lines.append("")
    lines.append(end_marker)

    before = content[: start_idx]
    after = content[end_idx + len(end_marker) :]
    updated = before + "\n" + "\n".join(lines) + "\n" + after.lstrip("\n")
    readme_path.write_text(updated, encoding="utf-8")


def main() -> None:
    print("🚀 Starting profile asset generation...")
    
    token = _require_env("GITHUB_TOKEN")
    username = os.getenv("GITHUB_USERNAME") or os.getenv("GITHUB_REPOSITORY_OWNER")
    if not username:
        raise RuntimeError("Missing GITHUB_USERNAME or GITHUB_REPOSITORY_OWNER")
    
    print(f"✓ Username: {username}")

    days = int(os.getenv("PERIOD_DAYS", "365"))
    period_label = os.getenv("PERIOD_LABEL") or "últimos 12 meses"
    print(f"✓ Period: {days} days ({period_label})")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print("\n📂 Fetching all repositories with commit history...")
    repos = fetch_all_repositories(token, username=username)
    print(f"✓ Found {len(repos)} public repositories")
    
    total_commits = sum(r.total_commits for r in repos)
    print(f"✓ Total commits across all repos: {total_commits}")
    
    print("\n🎨 Generating combined repos SVG...")
    render_combined_repos_svg(
        username=username,
        repos=repos,
        out_path=OUT_DIR / "repos-overview.svg",
    )
    print(f"✓ Created: {OUT_DIR / 'repos-overview.svg'}")
    

    print("\n�📝 Generating repositories.md...")
    render_repos_markdown(username=username, repos=repos, out_path=OUT_DIR / "repositories.md")
    print(f"✓ Created: {OUT_DIR / 'repositories.md'}")
    
    print("\n📄 Updating README.md with repo list...")
    update_readme_repo_section(username=username, repos=repos)
    print("✓ README updated successfully")
    
    print("\n✅ All assets generated successfully!")


if __name__ == "__main__":
    main()
