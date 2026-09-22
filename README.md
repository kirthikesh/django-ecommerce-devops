# django-ecommerce-devops

A full-featured e-commerce site built with Django, containerized with Docker,
deployable to Kubernetes, and shipped through a GitHub Actions CI/CD pipeline.

## Features

- **Catalog** — categories, products, search and filtering (by name, category, price range), sorting
- **Cart** — session-based cart (add/update/remove, works for guests)
- **Checkout** — mock/test-mode payment gateway (no real charges, no API keys needed); a card number ending in `0000` simulates a decline
- **Accounts** — custom user model, registration, login/logout, profile with shipping details
- **Orders** — order history and order detail pages for logged-in users
- **Reviews** — star ratings + comments per product, one review per user per product
- **Admin panel** — Django admin for managing products, categories, orders and reviews

## Project layout

```
core/            Django project settings, urls, wsgi/asgi
apps/
  accounts/      custom user model, auth views
  products/      catalog, search/filter, admin
  cart/          session-based cart
  orders/        checkout, mock payments, order history
  reviews/       product reviews
templates/       Django templates
static/          CSS
k8s/             Kubernetes manifests
.github/workflows/ci-cd.yml   CI/CD pipeline
Dockerfile
docker-compose.yml
```

## Local development (no Docker)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Without `POSTGRES_DB` set, the app falls back to SQLite automatically, so
this works with zero external services.

## Run with Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

This starts Postgres and the Django app (via Gunicorn) on http://localhost:8000.
Migrations run automatically on container start.

## Deploy to Kubernetes (kind / minikube)

1. Create a local cluster, e.g. `kind create cluster`
2. Build and load the image:
   ```bash
   docker build -t django-ecommerce-devops:local .
   kind load docker-image django-ecommerce-devops:local
   ```
3. Copy the secret template and fill in real values:
   ```bash
   cp k8s/secret.example.yaml k8s/secret.yaml
   # edit k8s/secret.yaml — never commit it (it's gitignored)
   ```
4. Point `k8s/django.yaml`'s image at your local tag (or your pushed GHCR image), then apply everything:
   ```bash
   kubectl apply -f k8s/namespace.yaml
   kubectl apply -f k8s/configmap.yaml
   kubectl apply -f k8s/secret.yaml
   kubectl apply -f k8s/postgres.yaml
   kubectl apply -f k8s/django.yaml
   kubectl apply -f k8s/ingress.yaml
   ```
5. Check rollout: `kubectl -n ecommerce get pods`

An NGINX ingress controller is assumed (`ingressClassName: nginx`); install
one first if your cluster doesn't have it (e.g. `kind`'s ingress-nginx docs).

## CI/CD pipeline

`.github/workflows/ci-cd.yml` runs on every push/PR to `main`:

1. **lint** — flake8
2. **test** — Django test suite against a real Postgres service container
3. **build-and-push** — builds the Docker image and pushes it to
   `ghcr.io/<your-github-username>/django-ecommerce-devops` (only on pushes to `main`)
4. **deploy** — manual (`workflow_dispatch`) job that applies the `k8s/` manifests
   and rolls out the new image. It needs a `KUBE_CONFIG` repository secret
   (base64-encoded kubeconfig) pointing at a cluster the runner can reach — a
   purely local `kind`/`minikube` cluster isn't reachable from GitHub-hosted
   runners, so for local development just run `kubectl apply -f k8s/` yourself
   after pulling the built image.

Before pushing, update the image reference in `k8s/django.yaml`
(`ghcr.io/OWNER/django-ecommerce-devops`) to match your actual GitHub username/org.

## Payments

Checkout uses a small mock gateway (`apps/orders/payments.py`) that mimics
test-mode providers like Stripe: any card number succeeds except one ending
in `0000`, which simulates a decline. No external payment API or credentials
are required. Swap it for a real integration behind the same `charge()`
interface when going to production.

## Tests

```bash
python manage.py test
```
