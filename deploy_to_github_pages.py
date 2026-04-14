#!/usr/bin/env python3
"""
Deploy OpenClaw digest HTML to GitHub Pages with randomized URLs.

Usage:
    # Deploy a specific HTML file
    python3 deploy_to_github_pages.py --file <path-to-html> --repo-dir <local-repo-dir>

    # Deploy and return the public URL
    python3 deploy_to_github_pages.py --file <path-to-html> --repo-dir <local-repo-dir> --base-url https://patriotbo.github.io/openclaw-digest-pages

    # Dry run
    python3 deploy_to_github_pages.py --file <path-to-html> --repo-dir <local-repo-dir> --dry-run

The script:
1. Generates a random slug for the HTML filename (e.g., openclaw-digest-2026-03-18-a3f8b2c1.html)
2. Injects <meta name="robots" content="noindex, nofollow"> into the HTML
3. Updates the URL mapping file (url_map.json) for reference
4. Regenerates the index.html (protected, not publicly linked)
5. Git add, commit, push to trigger GitHub Pages deployment
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import uuid
from datetime import datetime


URL_MAP_FILE = "url_map.json"


def generate_random_slug(date_str: str) -> str:
    """Generate a random slug like openclaw-digest-2026-03-18-a3f8b2c1."""
    random_part = uuid.uuid4().hex[:8]
    return f"openclaw-digest-{date_str}-{random_part}"


def extract_date_from_filename(filepath: str) -> str:
    """Extract date from filename like openclaw-digest-2026-03-18.html."""
    basename = os.path.basename(filepath)
    match = re.search(r"(\d{4}-\d{2}-\d{2})", basename)
    if match:
        return match.group(1)
    return datetime.now().strftime("%Y-%m-%d")


def inject_noindex(html_content: str) -> str:
    """Inject noindex meta tag into HTML <head>."""
    noindex_tag = '<meta name="robots" content="noindex, nofollow">'

    # Check if already present
    if "noindex" in html_content:
        return html_content

    # Inject after <head> or <head ...>
    head_pattern = re.compile(r"(<head[^>]*>)", re.IGNORECASE)
    match = head_pattern.search(html_content)
    if match:
        insert_pos = match.end()
        return html_content[:insert_pos] + "\n    " + noindex_tag + html_content[insert_pos:]

    # Fallback: inject at the very beginning
    return noindex_tag + "\n" + html_content


def load_url_map(repo_dir: str) -> dict:
    """Load the URL mapping file."""
    map_path = os.path.join(repo_dir, URL_MAP_FILE)
    if os.path.exists(map_path):
        with open(map_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"entries": []}


def save_url_map(repo_dir: str, url_map: dict):
    """Save the URL mapping file."""
    map_path = os.path.join(repo_dir, URL_MAP_FILE)
    with open(map_path, "w", encoding="utf-8") as f:
        json.dump(url_map, f, ensure_ascii=False, indent=2)


def generate_index_html(url_map: dict) -> str:
    """Generate a simple index.html listing all digests (also protected with noindex)."""
    entries = sorted(url_map.get("entries", []), key=lambda e: e.get("date", ""), reverse=True)

    rows = ""
    for entry in entries:
        date = entry.get("date", "unknown")
        slug = entry.get("slug", "")
        filename = f"{slug}.html"
        rows += f"""
        <tr>
            <td>{date}</td>
            <td><a href="{filename}">{filename}</a></td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="robots" content="noindex, nofollow">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenClaw Daily Digest Archive</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0f;
            color: #e0e0e0;
            min-height: 100vh;
            padding: 2rem;
        }}
        h1 {{
            font-size: 1.8rem;
            margin-bottom: 1.5rem;
            background: linear-gradient(135deg, #ff6b6b, #ffa36b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        table {{
            width: 100%;
            max-width: 600px;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 0.75rem 1rem;
            text-align: left;
            border-bottom: 1px solid #222;
        }}
        th {{ color: #888; font-weight: 500; }}
        a {{
            color: #6bb5ff;
            text-decoration: none;
        }}
        a:hover {{ text-decoration: underline; }}
        .footer {{
            margin-top: 2rem;
            color: #555;
            font-size: 0.85rem;
        }}
    </style>
</head>
<body>
    <h1>🦀 OpenClaw Daily Digest Archive</h1>
    <table>
        <thead>
            <tr><th>日期</th><th>报告</th></tr>
        </thead>
        <tbody>{rows}
        </tbody>
    </table>
    <p class="footer">This page is not indexed by search engines.</p>
</body>
</html>"""


def git_push(repo_dir: str, message: str) -> bool:
    """Stage all changes, commit, and push."""
    try:
        cmds = [
            ["git", "add", "-A"],
            ["git", "commit", "-m", message],
            ["git", "push", "-u", "origin", "main"],
        ]
        for cmd in cmds:
            result = subprocess.run(
                cmd, cwd=repo_dir, capture_output=True, text=True, timeout=60
            )
            if result.returncode != 0:
                # Allow "nothing to commit"
                if "nothing to commit" in result.stdout or "nothing to commit" in result.stderr:
                    print("Nothing new to commit.")
                    return True
                print(f"Git error: {' '.join(cmd)}", file=sys.stderr)
                print(f"  stdout: {result.stdout}", file=sys.stderr)
                print(f"  stderr: {result.stderr}", file=sys.stderr)
                return False
        return True
    except subprocess.TimeoutExpired:
        print("Git operation timed out", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Git error: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Deploy digest HTML to GitHub Pages")
    parser.add_argument("--file", "-f", required=True, help="Path to HTML file to deploy")
    parser.add_argument("--repo-dir", "-r", required=True, help="Path to local git repo directory")
    parser.add_argument("--base-url", "-b", default="", help="Base URL for GitHub Pages (e.g., https://user.github.io/repo)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without doing it")

    args = parser.parse_args()

    # Validate input
    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    if not os.path.isdir(args.repo_dir):
        print(f"Error: Repo directory not found: {args.repo_dir}", file=sys.stderr)
        sys.exit(1)

    # Read HTML
    with open(args.file, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Extract date and generate slug
    date_str = extract_date_from_filename(args.file)
    slug = generate_random_slug(date_str)
    dest_filename = f"{slug}.html"
    dest_path = os.path.join(args.repo_dir, dest_filename)

    # Inject noindex
    html_content = inject_noindex(html_content)

    # Build public URL
    public_url = ""
    if args.base_url:
        public_url = f"{args.base_url.rstrip('/')}/{dest_filename}"

    if args.dry_run:
        print(f"Would deploy: {args.file}")
        print(f"  → {dest_path}")
        print(f"  Slug: {slug}")
        if public_url:
            print(f"  URL: {public_url}")
        print(f"  noindex injected: Yes")
        sys.exit(0)

    # Write HTML file
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✓ Deployed: {dest_filename}")

    # Update URL map
    url_map = load_url_map(args.repo_dir)

    # Remove existing entry for the same date (re-deploy)
    url_map["entries"] = [e for e in url_map["entries"] if e.get("date") != date_str]

    url_map["entries"].append({
        "date": date_str,
        "slug": slug,
        "filename": dest_filename,
        "public_url": public_url,
        "deployed_at": datetime.now().isoformat()
    })
    save_url_map(args.repo_dir, url_map)
    print(f"✓ URL map updated")

    # Regenerate index.html
    index_html = generate_index_html(url_map)
    index_path = os.path.join(args.repo_dir, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_html)
    print(f"✓ Index page regenerated")

    # Git push
    commit_msg = f"Add digest {date_str}"
    print(f"Pushing to GitHub...")
    if git_push(args.repo_dir, commit_msg):
        print(f"✓ Push successful")
        if public_url:
            print(f"🔗 Public URL: {public_url}")
        # Output just the URL for script piping
        print(f"URL:{public_url}")
    else:
        print(f"✗ Push failed", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
