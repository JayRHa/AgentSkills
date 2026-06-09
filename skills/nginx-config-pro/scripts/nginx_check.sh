#!/usr/bin/env bash
# nginx_check.sh — lint an nginx config for the most common production mistakes.
#
# This is a heuristic, stdlib-only (bash + grep) pre-flight check. It does NOT
# replace `nginx -t`; run both.
#
# Usage:
#   ./nginx_check.sh /etc/nginx/sites-available/example.conf
#   ./nginx_check.sh /etc/nginx/nginx.conf
#
# Exit codes: 0 = no issues, 1 = warnings found, 2 = usage/error.

set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "usage: $0 <nginx-config-file>" >&2
    exit 2
fi

FILE="$1"
if [[ ! -f "$FILE" ]]; then
    echo "error: file not found: $FILE" >&2
    exit 2
fi

WARN=0
warn() { printf 'WARN  %s\n' "$1"; WARN=1; }
ok()   { printf 'OK    %s\n' "$1"; }
info() { printf 'INFO  %s\n' "$1"; }

# strip comments for content checks
CONTENT="$(grep -vE '^[[:space:]]*#' "$FILE" || true)"
has() { grep -qE "$1" <<<"$CONTENT"; }

echo "Checking: $FILE"
echo "----------------------------------------"

# 1. server_tokens off
if has 'server_tokens[[:space:]]+off'; then ok "server_tokens off (version hidden)"
else warn "server_tokens not set to off — nginx version is leaked in responses"; fi

# 2. weak TLS protocols
if has 'ssl_protocols'; then
    if grep -E 'ssl_protocols' <<<"$CONTENT" | grep -qE 'TLSv1(\.0|\.1)?[[:space:]]'; then
        warn "ssl_protocols enables TLSv1.0/1.1 — disable; use 'TLSv1.2 TLSv1.3'"
    else ok "ssl_protocols looks modern"; fi
else info "no ssl_protocols directive (ok if this isn't a TLS server block)"; fi

# 3. add_header without always
if has 'add_header'; then
    if grep -E 'add_header' <<<"$CONTENT" | grep -vq 'always'; then
        warn "some add_header directives lack 'always' — headers drop on 4xx/5xx"
    else ok "all add_header directives use 'always'"; fi
fi

# 4. HSTS preload safety
if grep -E 'Strict-Transport-Security' <<<"$CONTENT" | grep -q 'preload'; then
    warn "HSTS 'preload' present — ensure you submitted to hstspreload.org and HTTPS is permanent"
fi

# 5. keepalive consistency
if has 'keepalive[[:space:]]+[0-9]'; then
    if has 'proxy_http_version[[:space:]]+1\.1' && grep -E 'proxy_set_header[[:space:]]+Connection' <<<"$CONTENT" | grep -qE '\"\"|'\'''\'''; then
        ok "upstream keepalive paired with proxy_http_version 1.1 + Connection cleared"
    else
        warn "upstream keepalive set but missing 'proxy_http_version 1.1' and/or 'proxy_set_header Connection \"\"' — risks 502s"
    fi
fi

# 6. proxy forwarding headers
if has 'proxy_pass'; then
    for h in 'X-Forwarded-For' 'X-Forwarded-Proto' 'Host'; do
        if grep -qE "proxy_set_header[[:space:]]+$h" <<<"$CONTENT"; then ok "forwards $h"
        else warn "proxy_pass present but $h not forwarded — app may see wrong client/scheme/host"; fi
    done
    if grep -E 'proxy_set_header[[:space:]]+Host' <<<"$CONTENT" | grep -q '\$http_host'; then
        warn "Host set to \$http_host — prefer \$host (graceful fallback to server_name)"
    fi
fi

# 7. client_max_body_size present if uploads expected
if has 'proxy_pass' && ! has 'client_max_body_size'; then
    info "no client_max_body_size — default 1m may reject uploads (413)"
fi

# 8. rate-limit zones referenced but not (visibly) defined here
if has 'limit_req[[:space:]]+zone='; then
    if has 'limit_req_zone'; then ok "limit_req used and a zone is defined"
    else info "limit_req used; ensure limit_req_zone is defined in http{} (may be in another file)"; fi
fi

# 9. caching authenticated responses without bypass
if has 'proxy_cache[[:space:]]'; then
    if has 'proxy_no_cache' || has 'proxy_cache_bypass'; then
        ok "proxy_cache has bypass/no_cache rules"
    else
        warn "proxy_cache enabled without proxy_cache_bypass/proxy_no_cache — may cache per-user data"
    fi
fi

# 10. default_server present for unknown-host handling
if has 'listen[[:space:]]+443' && ! has 'default_server'; then
    info "no default_server — requests for unknown hostnames hit the first server block"
fi

echo "----------------------------------------"
if [[ "$WARN" -eq 0 ]]; then
    echo "No warnings. Still run: nginx -t"
    exit 0
else
    echo "Warnings found. Review above, then run: nginx -t"
    exit 1
fi
