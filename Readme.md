# streamforge-app

Minimal HTTP service used as the demo workload for the **StreamForge** DevOps / Platform Engineering portfolio project.

The service is intentionally tiny. Its purpose is to be a real, testable, containerizable workload for practicing Docker, Kubernetes, Helm, GitOps and CI — not an application-development exercise.

This repository contains **application code, tests and the Dockerfile**. Kubernetes manifests, Helm charts, Argo CD configuration and infrastructure CI live in the companion repository, `streamforge-infra`. The CI/CD pipeline logic is shared and lives in `pipeline-templates`.

## Status

| Item | State |
|---|---|
| HTTP service (`/` and `/health`) | Implemented |
| Unit tests | Implemented |
| Dockerfile (non-root, `python:3.12-slim`) | Implemented |
| CI: tests, image build, Trivy scan (via shared reusable workflow) | Implemented |
| Image published to GHCR on version tags (`v*`) | Implemented |
| Deployment to Kubernetes | Handled in `streamforge-infra` |

## Endpoints

| Method | Path | Response |
|---|---|---|
| GET | `/` | Simple HTML page |
| GET | `/health` | `200` with JSON `{"status": "ok"}` |
| GET | any other path | `404` with JSON error |

## Configuration

Configuration is read from environment variables:

| Variable | Default | Description |
|---|---|---|
| `HOST` | `0.0.0.0` | Address to bind to |
| `PORT` | `8080` | Port to listen on |
| `APP_VERSION` | `0.1.0` | Version string shown on the home page |

## Repository structure

```text
streamforge-app/
├── app/
│   ├── __init__.py
│   └── server.py          # HTTP server (standard library only)
├── tests/
│   ├── __init__.py
│   └── test_server.py     # unit tests
├── .github/
│   └── workflows/
│       └── ci.yml         # calls the shared pipeline in pipeline-templates
├── Dockerfile
├── .dockerignore
├── requirements.txt       # no dependencies at this stage
├── .gitignore
└── README.md
```

## Run locally

Requirements: Python 3.10 or newer. No packages need to be installed.

```bash
python -m app.server
```

The server listens on `http://localhost:8080`. Check it from another terminal:

```bash
curl http://localhost:8080/
curl http://localhost:8080/health
```

To use a different port:

```bash
PORT=9000 python -m app.server
```

Stop the server with `Ctrl+C`.

## Run tests

From the repository root:

```bash
python -m unittest discover -s tests -t . -v
```

The tests start the server on a random free port in a background thread, so they do not conflict with a server you already have running.

## Run in Docker

```bash
docker build -t streamforge-app:local .
docker run --rm -p 8080:8080 streamforge-app:local
```

The container runs as a non-root user (UID 10001) and listens on port 8080. Check `http://localhost:8080/health`.

## Continuous integration and image publishing

`.github/workflows/ci.yml` calls a reusable workflow from the `pipeline-templates` repository (`python-app-pipeline.yml`), so the same pipeline can be shared between projects. It runs on pushes to `main`, on pull requests and on version tags (`v*`).

Pipeline stages:

1. **Test** — runs the unit tests.
2. **Build** — builds the Docker image on the runner. The image is not pushed at this point.
3. **Trivy scan (gate)** — fails the pipeline if CRITICAL vulnerabilities are found (unfixed ones are ignored).
4. **Trivy report** — a SARIF report is always produced and uploaded as a workflow artifact (kept for 30 days).
5. **Push** — only on a version tag (`v*`) and only after the scan passes, the image is pushed to GHCR.

Because the image is scanned before it is pushed, an image that fails the gate never reaches the registry. Pushes to `main` and pull requests run the test, build and scan stages but do not publish an image.

The GitHub Actions artifact is only the Trivy report. The container image itself lives in GHCR; Kubernetes pulls it from there.

## Releasing a new image version

Create and push a Git tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```

The pipeline publishes the image to GHCR with two tags:

- `0.1.0` — the version, taken from the Git tag;
- a short commit SHA — identifies the exact commit the image was built from.

Image: `ghcr.io/makshofman/streamforge-app`

Version tags are immutable by convention — a published tag is never moved. `latest` is not used for deployments.

## Registry and credentials

- **Registry:** GitHub Container Registry (GHCR).
- **Authentication in CI:** the built-in `GITHUB_TOKEN` with `packages: write`. No tokens or secrets are stored in this repository.
- **Visibility:** the package should be public so a local kind cluster can pull the image without an image pull secret. If it is private, the cluster needs a pull secret.
- **Consumption:** the `streamforge-infra` repository references the image repository and tag in its Helm values.

## Related repositories

- `streamforge-infra` — Kubernetes configuration, Helm chart, Argo CD, infrastructure CI, observability, security and documentation.
- `pipeline-templates` — reusable GitHub Actions workflows shared between projects.

## Scope

This service is a small demo workload. The larger e-commerce event-processing platform mentioned in the project concept is a possible future extension and is **not** implemented here.