#!/usr/bin/env python3
"""Generate a self-hosted star-history SVG using the GitHub API."""

from __future__ import annotations

import argparse
import base64
import concurrent.futures
import datetime as dt
import json
import math
import os
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path
from xml.sax.saxutils import escape


GITHUB_API = "https://api.github.com"


def github_get(path: str, token: str) -> object:
    request = urllib.request.Request(
        f"{GITHUB_API}{path}",
        headers={
            "Accept": "application/vnd.github.star+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "cangjie-skill-star-history",
            "X-GitHub-Api-Version": "2026-03-10",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        message = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API returned HTTP {exc.code}: {message}") from exc


def fetch_repo_data(repo: str, token: str) -> tuple[list[dt.date], str]:
    repo_data = github_get(f"/repos/{repo}", token)
    if not isinstance(repo_data, dict) or not isinstance(repo_data.get("stargazers_count"), int):
        raise RuntimeError("Unexpected response from GitHub's repository API")

    page_count = max(math.ceil(repo_data["stargazers_count"] / 100), 1)

    def fetch_page(page: int) -> object:
        return github_get(f"/repos/{repo}/stargazers?per_page=100&page={page}", token)

    dates: list[dt.date] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(8, page_count)) as executor:
        pages = executor.map(fetch_page, range(1, page_count + 1))

    for items in pages:
        if not isinstance(items, list):
            raise RuntimeError("Unexpected response from GitHub's stargazers API")
        for item in items:
            dates.append(dt.datetime.fromisoformat(item["starred_at"].replace("Z", "+00:00")).date())
    owner = repo_data.get("owner")
    avatar_url = owner.get("avatar_url", "") if isinstance(owner, dict) else ""
    return sorted(dates), avatar_url


def fetch_image_data_uri(url: str) -> str:
    if not url:
        return ""
    separator = "&" if "?" in url else "?"
    request = urllib.request.Request(
        f"{url}{separator}s=64",
        headers={"User-Agent": "cangjie-skill-star-history"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            media_type = response.headers.get_content_type()
            encoded = base64.b64encode(response.read()).decode("ascii")
            return f"data:{media_type};base64,{encoded}"
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
        return ""


def nice_tick_step(value: int, tick_count: int = 5) -> int:
    target = max(value / max(tick_count - 1, 1), 1)
    magnitude = 10 ** math.floor(math.log10(target))
    candidates = [magnitude * factor for factor in (1, 2, 5, 10)]
    return max(1, int(min(candidates, key=lambda candidate: abs(candidate - target))))


def format_star_tick(value: int) -> str:
    if value >= 1000:
        return f"{value / 1000:g}K"
    return str(value)


def render_svg(
    repo: str,
    dates: list[dt.date],
    avatar_data_uri: str,
    font_base64: str,
    logo_base64: str,
) -> str:
    if not dates:
        raise RuntimeError("No star history was returned for this repository")

    width, height = 800, 533.333
    left, right, top, bottom = 70, 30, 60, 50
    plot_width = width - left - right
    plot_height = height - top - bottom

    start = dates[0]
    end = max(dates[-1], dt.datetime.now(dt.timezone.utc).date())
    day_span = max((end - start).days, 1)
    daily = Counter(dates)
    series: list[tuple[dt.date, int]] = []
    total = 0
    for offset in range(day_span + 1):
        day = start + dt.timedelta(days=offset)
        total += daily[day]
        series.append((day, total))

    y_max = max(total, 1)

    def x(day: dt.date) -> float:
        return ((day - start).days / day_span) * plot_width

    def y(value: int) -> float:
        return plot_height - (value / y_max) * plot_height

    line_path = " ".join(
        f"{'M' if index == 0 else 'L'}{x(day):.3f} {y(value):.3f}"
        for index, (day, value) in enumerate(series)
    )

    y_ticks: list[str] = []
    tick_step = nice_tick_step(total)
    for value in range(tick_step, total + 1, tick_step):
        ypos = y(value)
        y_ticks.append(
            '<g class="tick">'
            f'<path d="M0 {ypos:.3f}h-1" />'
            f'<text x="-7" y="{ypos:.3f}" dy=".32em">{format_star_tick(value)}</text>'
            '</g>'
        )

    x_ticks: list[str] = []
    for fraction in (0.20, 0.43, 0.67, 0.90):
        day = start + dt.timedelta(days=round(day_span * fraction))
        xpos = x(day)
        x_ticks.append(
            f'<text x="{xpos:.3f}" y="{plot_height + 22:.3f}" text-anchor="middle">'
            f'{day.strftime("%b %d")}</text>'
        )

    safe_repo = escape(repo)
    legend_width = max(150, len(repo) * 7.5 + 29)
    avatar_markup = ""
    if avatar_data_uri:
        avatar_markup = f'''<defs><clipPath id="clip-circle-title"><circle cx="327" cy="23" r="11" /></clipPath></defs>
  <image width="22" height="22" x="316" y="12" clip-path="url(#clip-circle-title)" href="{avatar_data_uri}" />'''

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc" style="stroke-width:3;font-family:xkcd;background:#fff">
  <title id="title">Star history for {safe_repo}</title>
  <desc id="desc">{total} GitHub stars from {start.isoformat()} through {end.isoformat()}</desc>
  <defs>
    <style>@font-face {{ font-family: "xkcd"; src: url(data:application/font-woff;charset=utf-8;base64,{font_base64}) format("woff"); }}</style>
    <filter id="xkcdify" width="100%" height="100%" x="-5" y="-5" filterUnits="userSpaceOnUse">
      <feTurbulence baseFrequency=".05" result="noise" type="fractalNoise" />
      <feDisplacementMap in="SourceGraphic" in2="noise" scale="5" xChannelSelector="R" yChannelSelector="G" />
    </filter>
  </defs>
  <rect width="{width}" height="{height}" fill="#fff" />
  <g pointer-events="all" transform="translate({left} {top})">
    <text style="font-size:16px;fill:#666" text-anchor="middle" transform="translate({plot_width - 50:.3f} {plot_height + 40:.3f})">star-history.com</text>
    <image width="20" height="20" href="data:image/png;base64,{logo_base64}" transform="translate({plot_width - 135:.3f} {plot_height + 25:.3f})" />

    <g fill="none" class="xaxis" font-size="10" text-anchor="middle">
      <path stroke="#000" d="M.5.5h{plot_width}" class="domain" filter="url(#xkcdify)" transform="translate(0 {plot_height:.3f})" />
      <g style="font-family:xkcd;font-size:16px;fill:#000">{''.join(x_ticks)}</g>
    </g>
    <g fill="none" stroke="#000" class="yaxis" font-size="10" text-anchor="end">
      <path d="M-1 {plot_height + .5:.3f}H.5V.5H-1" class="domain" filter="url(#xkcdify)" />
      <g style="font-family:xkcd;font-size:16px;fill:#000;stroke:none">{''.join(y_ticks)}</g>
    </g>

    <path fill="none" stroke="#dd4528" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" d="{line_path}" filter="url(#xkcdify)" />

    <g>
      <rect width="{legend_width:.1f}" height="32" x="8" y="5" fill="#fff" fill-opacity=".85" stroke="#000" stroke-width="2" filter="url(#xkcdify)" rx="5" ry="5" />
      <rect width="8" height="8" x="15" y="17" filter="url(#xkcdify)" rx="2" ry="2" fill="#dd4528" />
      <text x="29" y="25" style="font-size:15px;fill:#000">{safe_repo}</text>
    </g>
  </g>
  <text x="50%" y="30" style="font-size:20px;font-weight:700;fill:#000" text-anchor="middle">Star History</text>
  {avatar_markup}
  <text x="50%" y="{height - 10:.3f}" style="font-size:17px;fill:#000" text-anchor="middle">Date</text>
  <text x="{-height / 2 + 50:.3f}" y="12" dy=".75em" style="font-size:17px;fill:#000" text-anchor="end" transform="rotate(-90)">GitHub Stars</text>
</svg>
'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", "kangarooking/cangjie-skill"))
    parser.add_argument("--output", type=Path, default=Path("assets/star-history.svg"))
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("Set GITHUB_TOKEN or GH_TOKEN before running this script")

    dates, avatar_url = fetch_repo_data(args.repo, token)
    avatar_data_uri = fetch_image_data_uri(avatar_url)
    assets_dir = Path(__file__).resolve().parents[1] / "assets"
    font_base64 = (assets_dir / "xkcd.woff.b64").read_text(encoding="ascii").strip()
    logo_base64 = (assets_dir / "star-history-logo.png.b64").read_text(encoding="ascii").strip()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        render_svg(args.repo, dates, avatar_data_uri, font_base64, logo_base64),
        encoding="utf-8",
    )
    print(f"Wrote {args.output} with {len(dates)} stars")


if __name__ == "__main__":
    main()
