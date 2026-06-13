# Worked Example: Proxy a Node app on :3000 to https://app.example.com

## Input / requirements
- App: Express/Next.js listening on `127.0.0.1:3000`, HTTP, supports websockets.
- Domain: `app.example.com`, TLS via Let's Encrypt (certs already issued).
- Needs: HTTP→HTTPS redirect, HTTP/2, gzip, rate limiting (10 r/s), security
  headers, websocket upgrade, 25 MB upload limit.
- No response caching (responses are personalized).

## Step 1 — http{} context (in /etc/nginx/conf.d/00-shared.conf)

```nginx
upstream node_app {
    server 127.0.0.1:3000 max_fails=3 fail_timeout=15s;
    keepalive 32;
}

limit_req_zone  $binary_remote_addr zone=app_req:10m rate=10r/s;
limit_conn_zone $binary_remote_addr zone=app_conn:10m;

map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}
```

## Step 2 — site config (/etc/nginx/sites-available/app.example.com.conf)

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name app.example.com;
    location /.well-known/acme-challenge/ { root /var/www/certbot; }
    location / { return 301 https://$host$request_uri; }
}

server {
    listen 443 ssl;
    listen [::]:443 ssl;
    http2 on;
    server_name app.example.com;

    server_tokens off;
    client_max_body_size 25m;

    ssl_certificate     /etc/letsencrypt/live/app.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.example.com/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/app.example.com/chain.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_tickets off;
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 1.1.1.1 8.8.8.8 valid=300s;

    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    gzip on;
    gzip_vary on;
    gzip_comp_level 5;
    gzip_min_length 256;
    gzip_types text/plain text/css application/json application/javascript image/svg+xml;

    limit_req  zone=app_req burst=20 nodelay;
    limit_conn app_conn 20;
    limit_req_status 429;

    location / {
        proxy_http_version 1.1;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade           $http_upgrade;
        proxy_set_header Connection        $connection_upgrade;
        proxy_connect_timeout 5s;
        proxy_read_timeout    60s;
        proxy_pass http://node_app;
    }
}
```

> Note: the websocket `Connection $connection_upgrade` map and upstream
> `keepalive` both want to control the `Connection` header. The map wins per
> request; keepalive reuse still works for non-upgrade requests because
> `$connection_upgrade` resolves to `close` only when `Upgrade` is empty — for
> normal requests it yields `close`, disabling pooled keepalive on this location.
> If keepalive reuse matters more than websockets on a path, split websockets
> into their own `location /ws/` block and set `Connection ""` elsewhere.

## Step 3 — validate and reload

```bash
./scripts/nginx_check.sh /etc/nginx/sites-available/app.example.com.conf
sudo ln -s /etc/nginx/sites-available/app.example.com.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo nginx -s reload
```

## Step 4 — verify (expected output)

```bash
$ curl -sI https://app.example.com | head
HTTP/2 200
strict-transport-security: max-age=63072000; includeSubDomains
x-content-type-options: nosniff
x-frame-options: SAMEORIGIN
content-encoding: gzip

$ curl -sI http://app.example.com
HTTP/1.1 301 Moved Permanently
location: https://app.example.com/

# rate limit: hammer the endpoint, expect some 429s
$ for i in $(seq 1 40); do curl -s -o /dev/null -w "%{http_code} " https://app.example.com/; done
200 200 200 ... 429 429
```

Websocket check (using websocat or wscat):
```bash
$ wscat -c wss://app.example.com/socket
Connected (press CTRL+C to quit)
```
