# ShopSphere — E-commerce Microservices Platform

A deployable learning project for a DevOps assignment. It includes a React storefront/admin UI and five independent Flask services backed by PostgreSQL:

- **User Service**: registration, login, JWT authentication, user profile
- **Product Service**: product catalog, search, categories, stock
- **Order Service**: cart checkout, order history, order status; coordinates payment and notification
- **Payment Service**: simulated card/UPI payment (no real money is charged)
- **Notification Service**: persisted in-app order/payment notifications

> This is an educational starter, not a production payment system. Payment is simulated. Do not use real card details. The demo uses a shared PostgreSQL server with a separate database per service.

## Quick start (Docker)

Requirements: Docker Desktop / Docker Engine and Docker Compose v2.

```bash
cp .env.example .env
docker compose up --build
```

Open **http://localhost:8080**. The web container serves the React app and proxies `/api/*` to the correct backend service.

Stop:
```bash
docker compose down
```
Remove local demo data too:
```bash
docker compose down -v
```

## Demo accounts and payment simulation

Register a new account from the UI. The first registered user is a normal customer. To use admin endpoints, set `ADMIN_EMAIL` in `.env` before starting and register with that email; the UI includes a basic admin product form for that account.

The payment form accepts any non-empty demo payment reference. Use `DECLINE` as the payment reference to simulate a declined payment. No actual payment is processed.

## API endpoints

| Service | Path | Main endpoints |
|---|---|---|
| User | `/api/users` | `POST /register`, `POST /login`, `GET /me` |
| Product | `/api/products` | `GET /`, `GET /<id>`, `POST /`, `PUT /<id>`, `DELETE /<id>` |
| Order | `/api/orders` | `POST /`, `GET /`, `GET /<id>` |
| Payment | `/api/payments` | `POST /`, `GET /` |
| Notification | `/api/notifications` | `GET /` |

All backend services expose `/health`.

## Local development without Docker

Each service has its own `requirements.txt` and expects its `DATABASE_URL` plus shared `JWT_SECRET`. The easiest supported workflow is Docker Compose because it provisions five PostgreSQL databases and the reverse proxy.

## DevOps assignment workflow

1. **Source control**: push this repository to GitHub; use feature branches and pull requests.
2. **Quality checks**: add tests/linting to the workflow; never commit `.env`.
3. **Containerization**: each backend folder has its own Dockerfile; `frontend/Dockerfile` builds the React app and serves it with Nginx.
4. **Registry**: create one Amazon ECR repository per image (or use a single repo with distinct tags).
5. **CI/CD**: `.github/workflows/ci-cd.yml` builds and pushes images to ECR on pushes to `main`. Configure the listed GitHub Actions secrets/variables first.
6. **AWS infrastructure**: `infra/terraform` contains a starter ECS cluster, ECR repositories, and networking. Extend it with ECS task definitions/services, ALB listener/path routing, RDS PostgreSQL, Secrets Manager, and CloudWatch before production deployment.
7. **Monitoring**: configure CloudWatch log groups/alarms and ECS health checks.
8. **Security**: use GitHub OIDC to assume an AWS role, least-privilege IAM, private subnets for services/database, HTTPS, Secrets Manager, image scanning, and non-root containers.

## Important AWS note

The Compose stack is fully runnable locally. The Terraform and CI/CD files are assignment scaffolding, not a one-click production AWS deployment. You must supply your AWS account/region, GitHub OIDC role, VPC/network choices, domain/TLS certificate if needed, and RDS/ALB/ECS service configuration. Never publish credentials or real payment data.
