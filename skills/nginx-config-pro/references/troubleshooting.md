# nginx Troubleshooting Reference

## First commands every time
```bash
nginx -t                      # syntax + does referenced files exist
nginx -T | less               # dump the FULLY resolved config (all includes)
tail -f /var/log/nginx/error.log
systemctl status nginx        # or: nginx -s reload after a passing -t
```

## 502 Bad Gateway — nginx reached but upstream failed
Causes, in order of likelihood:
1. **Upstream not running / wrong port.** `curl -v http://127.0.0.1:<PORT>/` from
   the nginx host. If that fails, the app is the problem, not nginx.
2. **SELinux blocking the connection** (RHEL/Fedora): error log shows
   `Permission denied` connecting upstream. Fix:
   `setsebool -P httpd_can_network_connect 1`.
3. **Socket perms** when proxying to a unix socket: nginx user must have rwx on it.
4. **Upstream sent invalid headers** (`upstream sent too big header`): raise
   `proxy_buffer_size 16k; proxy_buffers 4 16k;`.
5. **keepalive misconfig**: missing `proxy_http_version 1.1` + `Connection ""`
   while `upstream { keepalive }` is set causes reset connections.

## 504 Gateway Timeout — upstream too slow
- Confirm in error log: `upstream timed out (110: Connection timed out)`.
- Raise the relevant timeout only as a stopgap:
  `proxy_read_timeout 120s;` (response), `proxy_connect_timeout 10s;` (connect).
- The real fix is in the application; large reports/exports should stream or move
  to a background job.

## 413 Request Entity Too Large
`client_max_body_size 50m;` at server (or location) scope. Default is 1m.

## 400 Bad Request / wrong vhost served
- Requests for an unknown host fall to the `default_server`. Define an explicit
  default that returns 444 to drop them.
- `$host` empty? A client without a Host header on HTTP/1.0. `$host` falls back
  to `server_name`, which is why you should use `$host` not `$http_host`.

## Duplicate or missing headers
- Missing security headers on a 404/500 page → you forgot `always`.
- Headers vanish inside a location → the `add_header` inheritance trap (any
  `add_header` in the location discards parent ones). Re-add the full bundle.
- Duplicate `Strict-Transport-Security` → it is set in BOTH a server block and
  an included snippet. Define it once.

## Caching not working
- Add `add_header X-Cache-Status $upstream_cache_status always;` and inspect.
- `BYPASS` → a `proxy_cache_bypass` var matched (cookie/auth present).
- Always `MISS` → upstream sends `Set-Cookie` or `Cache-Control: no-store`;
  nginx refuses to store those. Check upstream response with `curl -sI`.
- Cache dir not writable by the nginx worker user.

## Rate limiting not triggering / too aggressive
- Behind a CDN every request shares the edge IP → configure `real_ip` first.
- `limit_req` logs `limiting requests` at error level when active; grep the log.
- `burst` too low causes legit users to get 429; `nodelay` serves burst instantly.

## TLS issues
- `SSL_ERROR` / chain incomplete → use `fullchain.pem`, not `cert.pem`.
- OCSP stapling not working → set `ssl_trusted_certificate` + a working `resolver`.
- Mixed-content warnings → app generates http:// URLs; ensure
  `proxy_set_header X-Forwarded-Proto $scheme;` and configure the app to honor it.

## Performance / connection limits
- `worker_connections are not enough` in log → raise `worker_connections` AND
  `worker_rlimit_nofile` (the OS fd limit) together.
- `worker_processes auto;` matches CPU cores.
- Use `nginx -V` to confirm which modules (http_v2, brotli, stream) are compiled in.
