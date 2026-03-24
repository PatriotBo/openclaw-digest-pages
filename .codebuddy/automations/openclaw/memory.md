# OpenClaw Daily Digest — Automation Memory

## ⚠️ 制度变更记录

### 2026-03-19: 敏感信息审查制度生效

**规则文件**: `.workbuddy/rules/sensitive-info-review.mdc`

从即日起，每次调用 `deploy_to_github_pages.py` 部署 HTML 到 GitHub Pages **之前**，必须：
1. 对 HTML 和 MD 文件执行敏感信息自动扫描（API Key、Webhook URL、个人信息、内网地址、本地路径等）
2. 生成审查报告并展示给用户
3. **等待用户明确确认** 后才能执行部署（P0 必须脱敏，P1 需用户判断）

此规则为 `always` 类型，每次任务执行时自动加载。

---

## 2026-03-23 (Mon) — Run #5

**Status**: ✅ Success  
**Entries found**: 9 (4 YouTube, 5 Other/Web)  
**Platforms searched**: YouTube (TranscriptAPI direct), X/Twitter (xAI API SSL error → Brave Search fallback, no results), 小红书 (Brave Search fallback, rate limited), Web (Brave Search — excellent results)  
**Note**: web_search tool unavailable; xAI API returned SSL error (exit code 35); Brave Search rate limited after 3 requests (CAPTCHA/429). TranscriptAPI YouTube search worked perfectly. Brave web search provided rich results before rate limiting.

**Reports generated**:
- MD: `openclaw-digest-2026-03-23.md`
- HTML: `openclaw-digest-2026-03-23.html`

**Sensitive info review**: ✅ Passed (P0: clean, P1: clean, P2: 3 GitHub usernames — public info)  
**Deployed**: `openclaw-digest-2026-03-23-c7b718d9.html`  
**Public URL**: https://patriotbo.github.io/openclaw-digest-pages/openclaw-digest-2026-03-23-c7b718d9.html  
**WeChat push**: ✅ Summary mode successful  
**Local server**: Running at localhost:9527  
**Dedup DB**: 9 new URLs added (44 total)

---

## 2026-03-21 (Sat) — Run #4

**Status**: ✅ Success  
**Entries found**: 9 (3 YouTube, 3 X/Twitter, 3 Other/Web)  
**Platforms searched**: YouTube (TranscriptAPI direct), X/Twitter (fallback via Brave Search — xAI credits exhausted), 小红书 (fallback via Brave Search), Web (Brave Search)  
**Note**: web_search tool unavailable; xAI API credits exhausted. TranscriptAPI YouTube search worked natively. Brave Search provided excellent results for X, 小红书 fallback, and web sources.

**Reports generated**:
- MD: `openclaw-digest-2026-03-21.md`
- HTML: `openclaw-digest-2026-03-21.html`

**Sensitive info review**: ✅ Passed (P0: clean, P1: clean — 1 false positive excluded, P2: clean)  
**Deployed**: `openclaw-digest-2026-03-21-731c38ec.html`  
**Public URL**: https://patriotbo.github.io/openclaw-digest-pages/openclaw-digest-2026-03-21-731c38ec.html  
**WeChat push**: ✅ Summary mode successful  
**Local server**: Running at localhost:9527  
**Dedup DB**: 9 new URLs added (35 total)

---

## 2026-03-20 (Fri) — Run #3

**Status**: ✅ Success  
**Entries found**: 9 (3 YouTube, 3 X/Twitter, 3 Other/Web)  
**Platforms searched**: YouTube (TranscriptAPI direct), X/Twitter (fallback via DuckDuckGo — xAI credits exhausted), 小红书 (blocked by CAPTCHA), Web (Brave Search)  
**Note**: web_search tool unavailable; xAI API credits exhausted; Google/DuckDuckGo blocked by CAPTCHA. TranscriptAPI YouTube search worked natively. Brave Search provided excellent web results.

**Reports generated**:
- MD: `openclaw-digest-2026-03-20.md`
- HTML: `openclaw-digest-2026-03-20.html`

**Sensitive info review**: ✅ Passed (P0: clean, P1: clean, P2: 1 GitHub username — public info)  
**Deployed**: `openclaw-digest-2026-03-20-08bca0cd.html`  
**Public URL**: https://patriotbo.github.io/openclaw-digest-pages/openclaw-digest-2026-03-20-08bca0cd.html  
**WeChat push**: ✅ Summary mode successful  
**Local server**: Running at localhost:9527  
**Dedup DB**: 9 new URLs added (36 total)

---

## 2026-03-19 (Thu) — Run #2

**Status**: ✅ Success  
**Entries found**: 8 (1 YouTube, 7 Other/Web)  
**Platforms searched**: YouTube (fallback via DuckDuckGo), X/Twitter (blocked by CAPTCHA), 小红书 (blocked by CAPTCHA), Web (DuckDuckGo)  
**Note**: web_search tool was unavailable; Google & Bing blocked by CAPTCHA. DuckDuckGo returned good results. X and 小红书 native search not possible this run.

**Reports generated**:
- MD: `openclaw-digest-2026-03-19.md`
- HTML: `openclaw-digest-2026-03-19.html`

**Deployed**: `openclaw-digest-2026-03-19-2997609f.html`  
**Public URL**: https://patriotbo.github.io/openclaw-digest-pages/openclaw-digest-2026-03-19-2997609f.html  
**WeChat push**: ✅ Summary mode successful  
**Local server**: Running at localhost:9527  
**Dedup DB**: 8 new URLs added (27 total)

---

## 2026-03-18 (Tue) — Run #1 (initial run, no memory file existed)

**Status**: ✅ Success (inferred from url_map.json)  
**Deployed**: `openclaw-digest-2026-03-18-502e26e7.html`  
**Public URL**: https://patriotbo.github.io/openclaw-digest-pages/openclaw-digest-2026-03-18-502e26e7.html  
**Dedup DB**: 19 entries from this run
