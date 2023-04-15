# JIRA
create proxy enabled for nginx using location block below
```
   location /jira-webhook {
	proxy_pass http://127.0.0.1:8080;
        include uwsgi_params;
	proxy_cache_bypass 1;
	proxy_http_version 1.0;
	proxy_next_upstream off;
    }
```
run the wsgi as daemon using below command
`uwsgi --ini webhook.ini `
