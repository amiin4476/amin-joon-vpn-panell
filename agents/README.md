# AMIN JOON Node Agent

The AMIN JOON Node Agent runs on each VPN server and allows the central management panel to securely monitor and communicate with that server.

## Features

- Secure HTTPS communication through Caddy
- Domain name support
- Public IPv4 address support
- Public IPv6 address support
- Bearer token authentication
- CPU, memory, and disk monitoring
- Request rate limiting
- Automatic TLS certificate management through ACME

## Requirements

- Ubuntu 22.04 or newer
- Docker Engine
- Docker Compose plugin
- A public IPv4 or IPv6 address, or a domain pointing to the server
- Public inbound TCP ports 80 and 443
- A working internet connection for ACME certificate issuance

## Installation

### 1. Download the project

```bash
git clone https://github.com/amiin4476/amin-joon-vpn-panell.git
cd amin-joon-vpn-panell/agents
```

### 2. Create environment configuration

Copy the example configuration:

```bash
cp .env.example .env
```

Edit the environment file:

```bash
nano .env
```

Configure the following values:

```env
AGENT_TOKEN=YOUR_UNIQUE_RANDOM_SECRET_AT_LEAST_32_CHARACTERS
NODE_NAME=Germany-Node-01
AGENT_DOMAIN=agent.example.com
```

Set `AGENT_DOMAIN` to one of the following:

- Your public domain name, such as `agent.example.com`
- Your public IPv4 address, such as `203.0.113.10`
- Your public IPv6 address, using brackets, such as `[2001:db8::10]`

For a domain, configure its DNS records to point to this server.

The `AGENT_TOKEN` must be unique for each node and contain at least 32 characters.

Never publish the real `.env` file or share its token.

### 3. Configure network access

Allow inbound traffic on:

- TCP 80 — ACME certificate validation
- TCP 443 — HTTPS communication
- UDP 443 — Optional HTTP/3 support

Make sure your firewall and hosting provider allow these ports.

Port 9000 must not be exposed publicly.

### 4. Start the Agent and Caddy

Build and start the containers:

```bash
docker compose up -d --build
```

### 5. Check container status

```bash
docker compose ps
```

Both `node-agent` and `caddy` should be running.

### 6. Check HTTPS health

Run:

```bash
curl https://${AGENT_DOMAIN}/health
```

A successful response should contain:

```json
{
  "status": "ok"
}
```

### 7. Check authenticated connectivity

Run:

```bash
curl -H "Authorization: Bearer ${AGENT_TOKEN}" https://${AGENT_DOMAIN}/api/v1/ping
```

A successful response should contain:

```json
{
  "status": "connected",
  "node": "Germany-Node-01"
}
```

The exact response also includes a timestamp.

## TLS Certificates

Caddy automatically requests and renews TLS certificates through ACME.

The Caddy configuration uses the `shortlived` ACME certificate profile to support public IP address certificates where the certificate authority permits them.

Important requirements:

- The server must be reachable from the public internet.
- TCP ports 80 and 443 must be accessible.
- The configured domain or IP must identify the actual server.
- Certificate issuance depends on the ACME provider's current eligibility and validation requirements.

IP address certificates have a short validity period and are automatically renewed by Caddy.

Do not disable TLS certificate verification in the central management panel.

## Security

- The Agent is not directly exposed to the public internet.
- Caddy provides the public HTTPS endpoint.
- Protected API endpoints require Bearer token authentication.
- The Agent container runs as a non-root user.
- The Agent container uses a read-only filesystem.
- Linux capabilities are dropped.
- Requests are rate-limited.
- Caddy certificate data is stored in persistent Docker volumes.

## Troubleshooting

Check container status:

```bash
docker compose ps
```

View Agent logs:

```bash
docker compose logs --tail=100 node-agent
```

View Caddy logs:

```bash
docker compose logs --tail=100 caddy
```

If certificate issuance fails, verify DNS/IP configuration, public reachability, firewall rules, and ACME validation requirements.

## Important

Do not expose port 9000 directly to the public internet.

The central management panel must connect to the Agent using its public HTTPS domain or IP address and the configured Agent token.
