---
name: nginx-config-pro
description: Generates and hardens production nginx configurations for reverse proxying with TLS termination, HTTP/2, response caching, rate limiting, gzip/brotli compression, and security headers. Use this skill when the user asks to "set up nginx as a reverse proxy", "add TLS/SSL to nginx", "configure nginx caching or rate limiting", "harden an nginx config", "proxy an app behind nginx", "fix nginx 502/504 errors", or write/review nginx.conf and server blocks.
license: MIT
---

# nginx-config-pro

## Overview

Authoritative guidance for writing secure, performant nginx reverse-proxy configurations. Produces server blocks that terminate TLS, speak HTTP/2, proxy to upstream applications, cache responses, throttle abusive clients, and compress payloads — without the footguns that cause 502s, header leaks, or weak ciphers.

**Keywords:** nginx, reverse proxy, TLS, SSL, HTTPS, HTTP/2, HTTP/3, certbot, Let's Encrypt, upstream, proxy_pass, gzip, brotli, rate limiting, limit_req, proxy_cache, security headers, HSTS, CSP, OCSP stapling, websocket, load balancing, 502 bad gateway, 504 gateway timeout.

This skill targets nginx 1.18+ (most directives work on 1.10+). HTTP/3 notes assume 1.25+.

## When to use

- Standing up nginx in front of an app server (Node, Django/gunicorn, Rails/puma, PHP-FPM, a container).
- Adding or fixing TLS, redirects, or HSTS.
- Diagnosing 502/504, header duplication, or caching misses.
- Reviewing an existing `nginx.conf` for security and performance.

## Workflow

Follow these steps in order. Each builds on the previous.

1. **Gather inputs.** Determine: domain name(s), upstream address (host:port or socket), app protocol (http/https/grpc/websocket), whether TLS certs exist or need Let's Encrypt, expected traffic profile (for rate limits and cache), and static asset paths.
2. **Choose a topology.** Single upstream vs. load-balanced pool; HTTP/1.1 keepalive to upstream vs. fresh connections; whether caching is safe (idempotent GET responses with sane cache headers).
3. **Scaffold the file.** Use `templates/reverse-proxy.conf.tmpl` as the starting point. Place site configs in `/etc/nginx/sites-available/<name>.conf` and symlink into `sites-enabled/` (Debian/Ubuntu), or `/etc/nginx/conf.d/<name>.conf` (RHEL).
4. **Configure TLS.** Apply the cipher suite, protocols, and OCSP stapling from `references/tls-hardening.md`. Always serve a port 80 → 443 redirect. Add HSTS only once you are certain HTTPS is permanent.
5. **Set proxy headers correctly.** Forward `Host`, `X-Forwarded-For`, `X-Forwarded-Proto`, and `X-Real-IP`. Set sane timeouts. For websockets, add the `Upgrade`/`Connection` map. See the "Proxy headers" checklist below.
6. **Add performance layers.** Enable gzip (and brotli if the module is present), HTTP/2, upstream keepalive, and `proxy_cache` where appropriate.
7. **Add protection layers.** Define `limit_req_zone` / `limit_conn_zone` in `http {}` and apply them in `location`/`server`. Add the security-header bundle.
8. **Validate.** Run `scripts/nginx_check.sh <conf>` to lint for the most common mistakes, then `nginx -t` and reload. Verify externally per `references/troubleshooting.md`.

## Proxy headers checklist (the #1 source of bugs)

Put shared proxy settings in a snippet (e.g. `/etc/nginx/snippets/proxy.conf`) and `include` it:

```nginx
proxy_http_version 1.1;
proxy_set_header Host              $host;
proxy_set_header X-Real-IP         $remote_addr;
proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_set_header X-Forwarded-Host  $host;
proxy_set_header Connection        "";          # enables upstream keepalive
proxy_read_timeout    60s;
proxy_connect_timeout 5s;
proxy_send_timeout    60s;
proxy_buffering on;
```

Rules:
- Use `$host` (not `$http_host`) so a missing Host header degrades gracefully to `server_name`.
- `$proxy_add_x_forwarded_for` appends; never hard-set `X-Forwarded-For $remote_addr` behind another proxy.
- Set `Connection ""` only when paired with an `upstream { keepalive N; }` block and `proxy_http_version 1.1`.
- Your app must trust these headers ONLY when nginx is the edge. Behind a load balancer/CDN, validate the real client IP via `set_real_ip_from` + `real_ip_header`.

## Worked decision: should I cache this?

| Condition | Cache? |
|-----------|--------|
| Response is `GET`/`HEAD`, no `Set-Cookie`, no `Authorization` | Yes |
| Upstream sends `Cache-Control: private/no-store` | No (respect it) |
| Per-user/personalized HTML | No, or vary by a cache key that includes the session |
| Static assets (js/css/img with hashed names) | Yes, long `expires`, `immutable` |
| API JSON that changes every request | No |

When caching, always add a `X-Cache-Status $upstream_cache_status` header so you can confirm HIT/MISS/BYPASS. See `references/caching-and-compression.md`.

## Rate limiting quick reference

Define zones in `http {}`, apply in `server`/`location`:

```nginx
# http {} context
limit_req_zone  $binary_remote_addr zone=req_per_ip:10m rate=10r/s;
limit_conn_zone $binary_remote_addr zone=conn_per_ip:10m;

# location {} context
limit_req  zone=req_per_ip burst=20 nodelay;
limit_conn conn_per_ip 20;
limit_req_status 429;
```

- `burst` absorbs short spikes; `nodelay` serves the burst immediately instead of queuing.
- `$binary_remote_addr` is compact (16 bytes/IPv6); a 10m zone holds ~160k unique IPs.
- For login endpoints use a tighter zone (e.g. `rate=5r/m`) to slow credential stuffing.
- Behind a CDN, key on the real client IP (after `real_ip`), not the CDN edge IP.

## Security headers bundle

Apply at `server` scope (see `references/tls-hardening.md` for full rationale and CSP guidance):

```nginx
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
add_header X-Content-Type-Options    "nosniff" always;
add_header X-Frame-Options           "SAMEORIGIN" always;
add_header Referrer-Policy           "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy    "default-src 'self'" always;
server_tokens off;
```

The `always` flag is mandatory — without it headers are dropped on 4xx/5xx responses.

## Best Practices

- **One server block per concern.** Keep a dedicated port-80 redirect block separate from the TLS block.
- **Always `server_tokens off;`** to hide the nginx version.
- **Use snippets/includes** for `proxy.conf`, `ssl.conf`, and `security-headers.conf` so every site stays consistent.
- **Pin `ssl_protocols TLSv1.2 TLSv1.3;`** and a modern cipher list; disable TLS 1.0/1.1.
- **Test before reload:** `nginx -t && nginx -s reload`. Never reload a config that fails the test.
- **Set explicit timeouts.** Defaults (60s read) can hang clients on a slow upstream.
- **Define a default `server_name _;` block** that returns 444 to drop requests for unknown hosts.
- **Log to structured/JSON format** when shipping to a log pipeline (see template).
- **Reload, don't restart**, for config changes — reload is zero-downtime.

## Common Pitfalls

- **Missing `Connection ""` + keepalive mismatch** → upstream connections not reused, or `502` storms. Pair `proxy_http_version 1.1`, `Connection ""`, and `upstream { keepalive }`.
- **`add_header` without `always`** → security headers silently disappear on errors.
- **`add_header` inheritance trap** → defining ANY `add_header` in a `location` discards ALL `add_header` from the parent `server`. Re-include the full bundle or use a snippet in every location that needs it.
- **`proxy_pass` trailing-slash semantics** → `proxy_pass http://up/;` (with slash) strips the matched location prefix; without the slash it passes the full URI. Mixing these breaks routing.
- **HSTS too early / `preload` before submission** → can lock users out of HTTP for `max-age`. Start with a small `max-age`, drop `preload` until you have submitted to hstspreload.org.
- **`502 Bad Gateway`** → upstream down, wrong port, or SELinux blocking the connection (`setsebool -P httpd_can_network_connect 1`). See `references/troubleshooting.md`.
- **`504 Gateway Timeout`** → slow upstream; raise `proxy_read_timeout` and fix the app, don't just mask it.
- **`413 Request Entity Too Large`** → raise `client_max_body_size` (default 1m) for uploads.
- **Caching authenticated responses** → leaks one user's data to another. Add `proxy_cache_bypass`/`proxy_no_cache` for cookies/Authorization.
- **Worker/file-descriptor limits** → high-traffic sites need `worker_connections` and `worker_rlimit_nofile` raised together.

## Bundled files

- `templates/reverse-proxy.conf.tmpl` — complete, fill-in server config with TLS, caching, rate limiting, gzip, websockets, and security headers.
- `references/tls-hardening.md` — cipher suites, protocols, OCSP stapling, HSTS, CSP, Let's Encrypt/certbot, real-IP behind CDN.
- `references/caching-and-compression.md` — proxy_cache zones, cache keys, bypass rules, gzip/brotli tuning, static asset strategy.
- `references/troubleshooting.md` — 502/504/413/444 diagnosis, header debugging, validation commands.
- `scripts/nginx_check.sh` — stdlib (bash/grep) linter for the most common nginx config mistakes.
- `examples/node-app-proxy.md` — worked example: proxying a Node app on :3000 to https://app.example.com.
