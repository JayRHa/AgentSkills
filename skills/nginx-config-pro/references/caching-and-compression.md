# Caching & Compression Reference

## proxy_cache setup

Define the cache store once at `http {}` scope:
```nginx
proxy_cache_path /var/cache/nginx/site levels=1:2 keys_zone=site_cache:10m
                 max_size=1g inactive=60m use_temp_path=off;
```
- `levels=1:2` — directory hashing to avoid huge flat dirs.
- `keys_zone=NAME:SIZE` — shared memory for keys/metadata (~8k keys per 1m).
- `max_size` — disk cap; LRU eviction beyond it.
- `inactive` — purge entries not accessed within this window.
- `use_temp_path=off` — write directly into the cache dir (avoids cross-device copy).

Apply in a `location`:
```nginx
proxy_cache site_cache;
proxy_cache_valid 200 301 302 10m;
proxy_cache_valid 404 1m;
proxy_cache_key "$scheme$request_method$host$request_uri";
proxy_cache_use_stale error timeout updating http_500 http_502 http_503 http_504;
proxy_cache_background_update on;
proxy_cache_lock on;            # collapse concurrent misses into one upstream call
add_header X-Cache-Status $upstream_cache_status always;
```

### Never cache personalized/authenticated responses
```nginx
proxy_cache_bypass $http_authorization $cookie_session;  # skip lookup, still cache
proxy_no_cache     $http_authorization $cookie_session;  # do not store
```
If either variable is non-empty/non-zero, the rule fires. This prevents serving
one user's cached page to another.

### Cache key tips
- Default key omits Vary; if upstream varies on `Accept-Encoding`, nginx handles
  gzip correctly, but for `Accept-Language` or auth you must add to the key.
- To cache per-language: `proxy_cache_key "$scheme$host$request_uri$http_accept_language";`
- Honor upstream `Cache-Control: private/no-store` — nginx does by default unless
  you override with `proxy_ignore_headers` (avoid unless you know why).

### Confirming behavior
`curl -sI https://host/api/public/x | grep -i x-cache-status`
Expect `MISS` first, `HIT` after. `BYPASS` means a bypass var matched; `EXPIRED`
means it was refreshed.

### Purging
Open-source nginx has no built-in purge. Options: short `proxy_cache_valid`,
`proxy_cache_bypass $arg_nocache` for ad-hoc refresh, or delete files under the
cache path and reload. `proxy_cache_purge` requires nginx Plus or a third-party
module.

## gzip

```nginx
gzip on;
gzip_vary on;                 # adds Vary: Accept-Encoding
gzip_comp_level 5;            # 4-6 is the sweet spot; higher = diminishing CPU
gzip_min_length 256;         # don't compress tiny payloads
gzip_proxied any;            # compress even for proxied requests
gzip_types text/plain text/css application/json application/javascript
           text/xml application/xml application/xml+rss text/javascript
           image/svg+xml application/wasm;
```
- `text/html` is always compressed and need not be listed.
- Do NOT gzip already-compressed formats (jpg, png, mp4, woff2, gz) — wasted CPU.
- Compressing dynamic responses + caching: nginx caches the uncompressed body
  and compresses per request unless you cache the compressed variant. For static
  assets prefer pre-compressed files via `gzip_static on;`.

## brotli (if ngx_brotli is compiled in)

```nginx
brotli on;
brotli_comp_level 5;
brotli_static on;            # serve pre-built .br files when present
brotli_types text/plain text/css application/json application/javascript
             image/svg+xml application/wasm;
```
Brotli beats gzip ~15-25% on text. Ship both; clients negotiate via
`Accept-Encoding`. Check it is loaded: `nginx -V 2>&1 | tr ' ' '\n' | grep brotli`.

## Static asset strategy

```nginx
location ~* \.(?:css|js|woff2|svg|png|jpg|jpeg|gif|ico|webp)$ {
    root /var/www/site;
    expires 1y;
    add_header Cache-Control "public, immutable" always;
    access_log off;
    try_files $uri =404;
}
```
- Use content-hashed filenames (e.g. `app.3f9a2.js`) so `immutable` is safe.
- `immutable` tells browsers never to revalidate within the freshness window.
- Non-hashed HTML should use a short or `no-cache` policy so deploys are visible.
