#!/usr/bin/env python3
"""
Push Markdown digest content to 企业微信 (WeCom) via Webhook.

Usage:
    # Push a Markdown file
    python3 wechat_webhook_push.py --file <path-to-md> --webhook <webhook-url>

    # Push with HTML full-version link appended
    python3 wechat_webhook_push.py --file <path-to-md> --webhook <webhook-url> --html-url <public-url>

    # Push with custom title
    python3 wechat_webhook_push.py --file <path-to-md> --webhook <webhook-url> --title "Custom Title"

    # Push raw text content from stdin
    echo "Hello" | python3 wechat_webhook_push.py --webhook <webhook-url> --title "Test"

    # Dry run (print payload without sending)
    python3 wechat_webhook_push.py --file <path-to-md> --webhook <webhook-url> --dry-run

Notes:
    - 企业微信 Webhook Markdown 消息有 4096 字节限制
    - 脚本会自动截断过长内容并添加"查看完整版"链接
    - 如果提供了 --html-url，消息末尾会附上可点击的公网链接
    - 支持标准 Markdown 语法（标题、加粗、链接、引用、列表等）
"""

import argparse
import json
import sys
import os
import urllib.request
import urllib.error
import re
from datetime import datetime


# 企业微信 Markdown 消息的字节限制
WECHAT_MD_BYTE_LIMIT = 4096
# 留一些余量给截断提示
SAFE_BYTE_LIMIT = 3800


def read_markdown_file(filepath: str) -> str:
    """Read a Markdown file and return its content."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def truncate_to_byte_limit(text: str, limit: int = SAFE_BYTE_LIMIT) -> tuple[str, bool]:
    """
    Truncate text to fit within byte limit (UTF-8).
    Returns (truncated_text, was_truncated).
    """
    encoded = text.encode("utf-8")
    if len(encoded) <= limit:
        return text, False

    # Truncate at byte level, then decode safely
    truncated = encoded[:limit].decode("utf-8", errors="ignore")

    # Try to cut at the last complete line
    last_newline = truncated.rfind("\n")
    if last_newline > limit * 0.5:  # Only if we keep at least half the content
        truncated = truncated[:last_newline]

    return truncated, True


def simplify_markdown_for_wechat(content: str) -> str:
    """
    Simplify Markdown content for better rendering in 企业微信.
    WeCom supports a subset of Markdown: headers, bold, links, quotes, lists.
    """
    lines = content.split("\n")
    simplified = []

    for line in lines:
        # Remove image syntax (WeCom doesn't support images in markdown msg)
        line = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"[\1]", line)

        # Remove horizontal rules (--- or ***)
        if re.match(r"^\s*[-*_]{3,}\s*$", line):
            continue

        # Keep everything else as-is (WeCom handles basic MD well)
        simplified.append(line)

    return "\n".join(simplified)


def extract_title_from_md(content: str) -> str:
    """Extract the first H1 or H2 heading as title."""
    for line in content.split("\n"):
        match = re.match(r"^#{1,2}\s+(.+)", line)
        if match:
            return match.group(1).strip()
    return f"OpenClaw 日报 {datetime.now().strftime('%Y-%m-%d')}"


def build_payload(content: str, title: str = None, html_url: str = None) -> dict:
    """Build the 企业微信 Webhook payload."""
    # Simplify for WeCom rendering
    simplified = simplify_markdown_for_wechat(content)

    # Reserve space for the footer (link + truncation notice)
    footer = ""
    if html_url:
        footer = f"\n\n---\n> 📖 [点击查看完整版 HTML 日报]({html_url})"

    footer_bytes = len(footer.encode("utf-8"))
    truncate_limit = SAFE_BYTE_LIMIT - footer_bytes

    # Truncate if needed
    truncated, was_truncated = truncate_to_byte_limit(simplified, truncate_limit)

    if was_truncated:
        truncated += "\n\n> ⚠️ 内容过长已截断"

    # Append footer
    truncated += footer

    return {
        "msgtype": "markdown",
        "markdown": {
            "content": truncated
        }
    }


def send_webhook(webhook_url: str, payload: dict) -> dict:
    """Send payload to 企业微信 Webhook and return response."""
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        return {"errcode": e.code, "errmsg": f"HTTP {e.code}: {body}"}
    except urllib.error.URLError as e:
        return {"errcode": -1, "errmsg": f"Connection error: {e.reason}"}
    except Exception as e:
        return {"errcode": -1, "errmsg": str(e)}


def main():
    parser = argparse.ArgumentParser(
        description="Push Markdown digest to 企业微信 via Webhook"
    )
    parser.add_argument(
        "--file", "-f",
        help="Path to Markdown file to push"
    )
    parser.add_argument(
        "--webhook", "-w",
        required=True,
        help="企业微信 Webhook URL"
    )
    parser.add_argument(
        "--title", "-t",
        help="Custom title (auto-extracted from MD if not provided)"
    )
    parser.add_argument(
        "--html-url",
        help="Public URL to the full HTML report (appended to message)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print payload without sending"
    )

    args = parser.parse_args()

    # Read content
    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        content = read_markdown_file(args.file)
    elif not sys.stdin.isatty():
        content = sys.stdin.read()
    else:
        print("Error: Provide --file or pipe content via stdin", file=sys.stderr)
        sys.exit(1)

    if not content.strip():
        print("Error: Empty content", file=sys.stderr)
        sys.exit(1)

    # Determine title
    title = args.title or extract_title_from_md(content)

    # Build payload
    payload = build_payload(content, title, html_url=args.html_url)

    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        content_bytes = len(payload["markdown"]["content"].encode("utf-8"))
        print(f"\n--- Content size: {content_bytes} bytes (limit: {WECHAT_MD_BYTE_LIMIT}) ---")
        sys.exit(0)

    # Send
    print(f"Pushing to 企业微信: {title}")
    result = send_webhook(args.webhook, payload)

    if result.get("errcode") == 0:
        print(f"✓ Push successful")
        sys.exit(0)
    else:
        print(f"✗ Push failed: {result.get('errmsg', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
