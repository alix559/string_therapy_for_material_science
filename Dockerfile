# Thin Railway proxy → origin UI/controller on the Hetzner host.
# The FastHTML app + string_therapy controller run on the server, not here.
#
# Railway Variables:
#   UPSTREAM=http://static.29.136.62.46.clients.your-server.de:4546
#   PORT     (injected by Railway)

FROM caddy:2.9-alpine

COPY Caddyfile /etc/caddy/Caddyfile

ENV UPSTREAM=http://static.29.136.62.46.clients.your-server.de:4546 \
    PORT=8080

EXPOSE 8080
