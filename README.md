# LLama 3.2 3B AI Server implementation

## Server Stack

- ⚡ [**FastAPI**](https://fastapi.tiangolo.com) for the Python backend API..
  - 💾 [Supabase](https://www.supabase.com) (Supabase)
- 🐋 [Docker Compose](https://www.docker.com) for development and production.
- 🔒 Secure password hashing by default.
- 🔑 JWT (JSON Web Token) authentication.
- 📫 Email based password recovery.
- ✅ Tests with [Pytest](https://pytest.org).
- 📞 [Traefik](https://traefik.io) as a reverse proxy / load balancer.
- 🚢 Deployment instructions using Docker Compose, including how to set up a frontend Traefik proxy to handle automatic HTTPS certificates.
- 🏭 CI (continuous integration) and CD (continuous deployment) based on GitHub Actions.

### API Documentation

#### Service API (provides endpoints to use the model)

- [Questionary](/backend/app/services/questionary.py) See API Endpoint
- [Summarize](/backend/app/services/summarize.py) See API Enpoint

#### LLM implementation / initialisation

- [LLama 3.2 3B](/backend/app/services/llms.py)

## Deployment Config

Docker is used see here important files:

[Dockerfile](/backend/Dockerfile)
[Docker Config](/docker-compose.override.yml)

### Configure

You can then update configs in the `.env` files to customize your configurations.

Before deploying it, make sure you change at least the values for:

- `SECRET_KEY`
- `FIRST_SUPERUSER_PASSWORD`
- `POSTGRES_PASSWORD`

You can (and should) pass these as environment variables from secrets.

Read the [deployment.md](./deployment.md) docs for more details.

## Backend Docs (not updated now: template config viewable)

Backend docs: [backend/README.md](./backend/README.md).

## Deployment

Deployment docs: [deployment.md](./deployment.md).
