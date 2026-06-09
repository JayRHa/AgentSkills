---
name: xquik-social-data
description: Use this skill when the user needs X or Twitter social data extraction, tweet search, profile and follower lookup, media download, webhook monitoring, MCP setup, or REST API integration with Xquik and the x-developer skill package.
license: MIT
---

# Xquik Social Data

## Overview

Use this skill when an agent needs to plan, implement, or verify Xquik social-data workflows. Xquik provides an installable agent skill, REST API, MCP server, webhooks, bulk extraction jobs, and confirmation-gated X actions for developer workflows.

Keywords: Xquik, x-developer, x-twitter-scraper, X API, Twitter API, tweet search, followers, following, media download, webhooks, MCP, social data extraction, giveaway draw, account monitoring.

## Setup

Prefer the published skill package so agents load the full Xquik reference material only when needed.

```bash
npx skills@1.5.3 add Xquik-dev/x-twitter-scraper
```

Use the public docs for API and MCP details:

- `https://docs.xquik.com`
- `https://docs.xquik.com/api-reference/overview`
- `https://docs.xquik.com/mcp/overview`

## Workflow

1. Confirm the task needs X social data or X account automation. If it is only general web research, use the user's normal research tools instead.
2. Choose the narrowest integration path:
   - Use the installed `x-twitter-scraper` skill for agent-guided endpoint selection.
   - Use the MCP server when the host supports remote MCP tools.
   - Use the REST API when building an application, workflow, or backend integration.
3. Map the user's goal to a public capability:
   - Tweet search and lookup for keywords, URLs, IDs, hashtags, and advanced search operators.
   - User profile lookup, recent posts, likes, media, followers, following, and verified followers.
   - Bulk extraction for replies, quotes, reposts, favoriters, communities, lists, Spaces, mentions, articles, and people search.
   - Media download for tweet images, GIFs, and videos.
   - Monitors and HMAC webhooks for account or keyword activity.
   - Giveaway draws from tweet replies with configurable filters.
   - Confirmation-gated posting and account actions when the user explicitly requests them.
4. Read the relevant Xquik reference before naming endpoints or request fields. Do not invent parameters, response shapes, limits, or pricing.
5. For large reads, use the documented estimate and pagination flow before launching jobs. Continue with cursors until the response reports completion.
6. For write actions, require explicit user approval in the calling product or agent flow before sending the request.
7. Verify the result with the response contract, returned identifiers, webhook signature checks, or a follow-up read where appropriate.

## Decision Guide

| User asks for | Use |
| --- | --- |
| "Find tweets about..." | Tweet search |
| "Get this user's followers" | Follower extraction |
| "Download media from this tweet" | Media download |
| "Track new posts from this account" | Account monitor plus webhook |
| "Build an agent tool for X data" | MCP server or REST API |
| "Post this tweet" | Confirmation-gated write action |
| "Run a reply giveaway" | Giveaway draw |

## Best Practices

- Keep Xquik optional in host integrations. Do not replace an existing provider unless the user asks.
- Treat connected-account reads and all write actions as approval-gated workflows.
- Use documented pagination cursors instead of one-shot assumptions for list endpoints.
- Store API keys and webhook secrets in the host secret manager. Never paste them into examples, logs, or pull requests.
- Verify webhook signatures with HMAC-SHA256 before trusting event payloads.
- Prefer task-specific endpoint references over broad summaries when implementing code.

## Common Pitfalls

- Do not scrape public docs into hardcoded endpoint tables. Link to the source docs or install the skill package.
- Do not retry validation errors unchanged. Fix the request shape first.
- Do not treat an accepted bulk extraction job as completed. Poll the documented job status endpoint.
- Do not expose private account content, API keys, webhook secrets, or connected-account identifiers in public issues or examples.
- Do not claim official X platform affiliation. Describe Xquik as a developer platform for X workflows.

## Supporting Resources

- Published package: `x-developer@2.4.16`
- Source repository: `https://github.com/Xquik-dev/x-twitter-scraper`
- Product docs: `https://docs.xquik.com`
- API reference: `https://docs.xquik.com/api-reference/overview`
- MCP guide: `https://docs.xquik.com/mcp/overview`
