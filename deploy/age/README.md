# PostgreSQL + Apache AGE (local Docker)

`string_therapy` needs **PostgreSQL + Apache AGE**, not plain managed Postgres.

Primary setup here is **local Docker Compose**. Railway notes are at the bottom for optional cloud deploy.

## Local (recommended)

### 1. Configure credentials

```bash
cd deploy/age
cp .env.example .env
# edit .env — set a real POSTGRES_PASSWORD
```

`.env` is gitignored. Do not commit passwords.

### 2. Start the database

```bash
docker compose up -d --build
docker compose ps
```

This builds from `Dockerfile` (`apache/age` + `shared_preload_libraries=age`), publishes **5432**, and stores data in the Docker volume `string_therapy_pgdata`.

### 3. Point the app at localhost

In the project root `.env`:

```text
ROUTER_DATABASE_URL=postgresql://postgres:<password>@127.0.0.1:5432/string_therapy
```

Use the same password as `POSTGRES_PASSWORD` in `deploy/age/.env`. URL-encode special characters in the password if needed.

### 4. Seed the router graph

From the project root (pixi env with `string-therapy` installed):

```bash
set -a && source .env && set +a
string-therapy-ensure-schema
string-therapy-seed --graph routes/router_graph.json
```

Or use `nbs/03_deploy_routes.ipynb`.

That creates the AGE `router` graph and related ACL/schema from `routes/router_graph.json`.

### 5. Smoke check

```bash
docker compose exec string-therapy-db \
  psql -U postgres -d string_therapy \
  -c "CREATE EXTENSION IF NOT EXISTS age; LOAD 'age'; SELECT * FROM ag_catalog.ag_graph;"
```

You should see a `router` graph after seeding.

### Useful commands

| Command | Purpose |
|---------|---------|
| `docker compose up -d` | Start / recreate |
| `docker compose logs -f` | Follow logs |
| `docker compose down` | Stop (keeps volume) |
| `docker compose down -v` | Stop **and delete data** |

### Remote access (other servers)

Compose publishes `0.0.0.0:5432`, Postgres listens on `*`, and `pg_hba.conf` allows password auth from any host (`scram-sha-256`). So another machine can connect with:

```text
postgresql://postgres:<password>@<this-host-public-ip>:5432/string_therapy
```

Example from another host:

```bash
psql "postgresql://postgres:<password>@<this-host-public-ip>:5432/string_therapy" -c 'SELECT 1'
```

On the **client** app, set:

```text
ROUTER_DATABASE_URL=postgresql://postgres:<password>@<this-host-public-ip>:5432/string_therapy
```

**Checklist if connection fails**

1. Use this host’s **public IP** (or DNS), not `127.0.0.1`.
2. Open **TCP 5432** in the cloud firewall / security group (Hetzner, AWS, etc.) for the client IPs.
3. Confirm the container is up: `docker compose ps`.
4. URL-encode special characters in the password.

**Hardening (recommended)**

Do not leave Postgres open to the whole internet longer than you need. Prefer one of:

- Cloud firewall: allow `5432` only from known client CIDRs.
- SSH tunnel from the other server:  
  `ssh -L 5432:127.0.0.1:5432 user@<this-host>` then connect to `127.0.0.1:5432` locally.
- Restrict `pg_hba` inside the container to those CIDRs, e.g. replace the open rule with:

```text
host all all 203.0.113.10/32 scram-sha-256
```

Then reload: `docker compose exec string-therapy-db psql -U postgres -c "SELECT pg_reload_conf();"`

### Variables (`deploy/age/.env`)

| Name | Default | Notes |
|------|---------|--------|
| `POSTGRES_USER` | `postgres` | DB superuser |
| `POSTGRES_PASSWORD` | (required) | Local secret |
| `POSTGRES_DB` | `string_therapy` | Database name |
| `POSTGRES_PORT` | `5432` | Host port |

---

## Optional: Railway

Use only if you want AGE in the cloud again. Prefer the local compose stack for day-to-day work.

### Create the service

**Option A — Docker image**

1. Railway → **New** → **Docker Image**
2. Image: `apache/age`
3. Start command: `postgres -c shared_preload_libraries=age`

**Option B — this Dockerfile**

1. Connect the repo
2. Root Directory: `deploy/age`
3. Deploy (`Dockerfile` + optional `railway.toml`)

### Volume (required)

| Setting | Value |
|---------|--------|
| Mount path | `/var/lib/postgresql` |

### Railway variables

| Name | Value |
|------|--------|
| `POSTGRES_USER` | `postgres` |
| `POSTGRES_PASSWORD` | strong secret |
| `POSTGRES_DB` | `string_therapy` |

### Networking

Same Railway project (private):

```text
ROUTER_DATABASE_URL=postgresql://postgres:${{age.POSTGRES_PASSWORD}}@${{age.RAILWAY_PRIVATE_DOMAIN}}:5432/string_therapy
```

Laptop via TCP Proxy:

```text
ROUTER_DATABASE_URL=postgresql://postgres:<password>@<tcp-proxy-host>:<proxy-port>/string_therapy
```

Then run the same seed commands as in the local section.

### What not to do on Railway

- Do not use Railway **Database → PostgreSQL** (no AGE).
- Do not skip the volume (data wipe on redeploy).
- Do not leave TCP Proxy open longer than needed.
