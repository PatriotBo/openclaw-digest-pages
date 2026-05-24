#!/usr/bin/env python3
import json

with open('url_map.json', 'r') as f:
    data = json.load(f)

entries = sorted(data['entries'], key=lambda x: x['date'], reverse=True)

rows = ''
for e in entries:
    rows += f'        <tr>\n            <td>{e["date"]}</td>\n            <td><a href="{e["filename"]}">{e["filename"]}</a></td>\n        </tr>\n'

html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="robots" content="noindex, nofollow">
    <title>OpenClaw Digest Pages - Index</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; max-width: 800px; margin: 2rem auto; padding: 0 1rem; background: #1a1a2e; color: #e8e8f0; }}
        h1 {{ color: #818cf8; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
        th, td {{ padding: 0.6rem 1rem; text-align: left; border-bottom: 1px solid #2a2a3a; }}
        th {{ color: #818cf8; }}
        a {{ color: #6366f1; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h1>OpenClaw Digest Pages</h1>
    <p>AI Daily Digest archive. {len(entries)} reports available.</p>
    <table>
        <thead>
            <tr><th>Date</th><th>File</th></tr>
        </thead>
        <tbody>
{rows}        </tbody>
    </table>
</body>
</html>'''

with open('index.html', 'w') as f:
    f.write(html)
print(f'OK - regenerated index.html with {len(entries)} entries')
