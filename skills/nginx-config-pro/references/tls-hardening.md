# TLS & Security Hardening Reference

## Protocols and ciphers

Disable everything below TLS 1.2. TLS 1.3 is mandatory for a modern (Mozilla
"Intermediate"/"Modern") rating.

```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers off;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:\
ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:\
ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305;
```

- TLS 1.3 cipher selection is controlled by the client; `ssl_ciphers` only affects 1.2.
- Prefer ECDSA certs for performance; dual ECDSA+RSA certs serve old clients too.
- `ssl_prefer_server_ciphers off` is current best practice (clients pick best AEAD).

## Session resumption

```nginx
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:10m;   # ~40k sessions per 10m
ssl_session_tickets off;            # tickets without rotation hurt forward secrecy
```

## OCSP stapling

```nginx
ssl_stapling on;
ssl_stapling_verify on;
ssl_trusted_certificate /etc/letsencrypt/live/<DOMAIN>/chain.pem;
resolver 1.1.1.1 8.8.8.8 valid=300s;
resolver_timeout 5s;
```

Stapling lets nginx serve a cached OCSP response so clients skip a round-trip to
the CA. Verify with: `openssl s_client -connect host:443 -status < /dev/null 2>&1 | grep -A2 'OCSP Response'`.

## HSTS (HTTP Strict Transport Security)

```nginx
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains" always;
```

Rollout order — do NOT skip steps:
1. Confirm HTTPS works on the apex AND every subdomain you cover.
2. Start with `max-age=300` (5 min) to limit blast radius.
3. Raise to `max-age=31536000` once stable.
4. Add `includeSubDomains` only when every subdomain is HTTPS.
5. Add `preload` and submit at https://hstspreload.org LAST. Preload is hard to
   reverse — a mistake locks users out of HTTP for the full max-age.

The `always` flag is required so the header is sent on error responses too.

## Security headers — full bundle with rationale

```nginx
add_header X-Content-Type-Options "nosniff" always;         # no MIME sniffing
add_header X-Frame-Options "SAMEORIGIN" always;             # clickjacking (legacy)
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'" always;
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
```

### Content-Security-Policy guidance
- Start strict (`default-src 'self'`) and widen only as needed.
- Prefer `frame-ancestors 'self'` in CSP over `X-Frame-Options` for modern browsers.
- Avoid `'unsafe-inline'`/`'unsafe-eval'`; use nonces or hashes for inline scripts.
- Test with the browser console and report-only mode first:
  `Content-Security-Policy-Report-Only: ...`.

### The add_header inheritance trap
`add_header` directives are NOT additive across contexts. If a `location` block
defines even one `add_header`, ALL inherited `add_header` from the `server`
block are dropped. Solution: put the full bundle in a snippet and `include` it
in every location that adds headers, or define headers only at server scope and
avoid `add_header` inside locations.

## Let's Encrypt / certbot

Webroot method (no nginx downtime):
```bash
certbot certonly --webroot -w /var/www/certbot -d example.com -d www.example.com
```
The port-80 server block must serve `/.well-known/acme-challenge/` from that
webroot (see template). Renewal is automatic via the certbot systemd timer; add
a deploy hook to reload nginx:
```bash
certbot renew --deploy-hook "nginx -s reload"
```

## Real client IP behind a CDN / load balancer

When nginx sits behind Cloudflare/ALB, `$remote_addr` is the proxy's IP. To
recover the real client (needed for rate limiting and logs):
```nginx
set_real_ip_from 173.245.48.0/20;   # each trusted proxy CIDR
set_real_ip_from 10.0.0.0/8;
real_ip_header   X-Forwarded-For;   # or CF-Connecting-IP for Cloudflare
real_ip_recursive on;
```
Only trust forwarded headers from CIDRs you control; otherwise clients can spoof
their IP and bypass rate limits.

## Verification tools
- `nginx -t` — config syntax.
- `openssl s_client -connect host:443 -servername host` — handshake/cert chain.
- SSL Labs (https://www.ssllabs.com/ssltest/) — external A/A+ grade.
- `curl -sI https://host` — confirm headers are present (and on errors with `-I https://host/nonexistent`).
