# AMIN JOON Node Agent

The AMIN JOON Node Agent runs on each VPN server and allows the central
management panel to monitor and communicate with that server.

## Requirements

- Ubuntu 22.04 or newer
- Docker Engine
- Docker Compose plugin

## Installation

### 1. Download the project

Clone the repository:

```bash
git clone https://github.com/amiin4476/amin-joon-vpn-panell.git
cd amin-joon-vpn-panell/agents
2. Create environment configuration
Copy the example file:
cp .env.example .env


Edit the environment file:
nano .env


Set a unique secret token for this node:
AGENT_TOKEN=YOUR_UNIQUE_RANDOM_SECRET
NODE_NAME=Germany-Node-01


The token must contain at least 32 characters.

Never publish the real .env file or share the token.
3. Start the Agent
Build and start the container:
docker compose up -d --build


4. Check container status
docker compose ps


5. Check local health
curl http://127.0.0.1:9000/health


A successful response should contain:
{
  "status": "ok"
}


Security
- The Agent listens only on localhost.
- The Agent requires Bearer token authentication for protected endpoints.
- The container runs as a non-root user.
- The container uses a read-only filesystem.
- Linux capabilities are dropped.
- Requests are rate-limited.
Important
The current Agent uses HTTP on localhost.

Do not expose port 9000 directly to the public internet.

HTTPS and secure communication with the central panel must be configured
before connecting production nodes.

**Commit message:**
`Add node agent installation guide`
