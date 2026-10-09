# The web application

People bring their own LLM model and talk with their beings; friends and administrators also see the
being's inner life. Settings: `config.json` (see `config.example.json` and `domains/core/config.py`).

    EMOSTACK_WEB_CONFIG=config.json python3 apps/web-emostack/app.py --port 8093
    * * * * *  cd /path/to/emostack && EMOSTACK_WEB_CONFIG=... python3 apps/web-emostack/tick.py

## The public room (`publicSheep`)

With `publicSheep` set, one being lives in `<dataFolder>/public/emostack.db` on the model given there
(the house model; nothing is billed to visitors) and is open to anyone at `/` and `/public` without
signing in: one visitor speaks at a time, the others wait in a queue and watch; a visit is
`turnsPerVisit` messages and ends after `idleSeconds` of silence; a visitor has `visitsPerDay`. The
being sleeps between `night[0]` and `night[1]` (`timezone`), when an administrator puts it to rest
(`POST /public/admin/sleep`, `/wake`, `/clear`), and whenever its model does not answer; asleep, it
takes one letter a night per visitor and answers them when it wakes. Reports from visitors:
`GET /public/admin/reports`. The cron tick includes the public store.

Behind a reverse proxy that signs people in, `/public/` must be open to everyone and `/public/admin/`
must stay behind the sign-in. With nginx and `auth_request`, before the catch-all `location /`:

    location /public/admin/ {
        # as location / (auth_request on, identity headers set)
        proxy_set_header X-Auth-Email $auth_email;
        proxy_set_header X-Auth-Name $auth_name;
        proxy_pass http://127.0.0.1:7860;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    location /public/ {
        auth_request off;
        limit_req zone=model_ip burst=30 nodelay;
        limit_conn model_conn 20;
        client_max_body_size 16k;
        proxy_set_header X-Auth-Email "";
        proxy_set_header X-Auth-Name "";
        proxy_pass http://127.0.0.1:7860;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_buffering off;
    }
    location = /public {
        auth_request /__auth;
        error_page 401 = @anon_home;
        # then as location = /
    }
