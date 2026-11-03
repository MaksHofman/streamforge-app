# streamforge-app

Minimal HTTP service used as the demo workload for the **StreamForge** DevOps / Platform Engineering portfolio project.

The service is intentionally tiny. Its purpose is to be a real, testable, containerizable workload for practicing Docker, Kubernetes, Helm, GitOps and CI — not an application-development exercise.

This repository contains **application code and tests only**. Kubernetes manifests, Helm charts, Argo CD configuration and infrastructure CI live in the companion repository, `streamforge-infra`.

## Status

| Item | State |
|---|---|
| HTTP service (`/` and `/health`) | Implemented |
| Unit tests | Implemented |
| GitHub Actions CI (tests only) | Implemented |
| Dockerfile | Planned (Stage 2) |
| Image published to GHCR | Planned (Stage 2) |

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
│       └── ci.yml         # code tests only
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

## Continuous integration

The workflow in `.github/workflows/ci.yml` runs on pushes to `main` and on pull requests. It:

1. checks out the repository,
2. sets up Python,
3. installs dependencies from `requirements.txt`,
4. runs the unit tests.

It uses read-only repository permissions (`contents: read`).

The workflow deliberately does **not** build a Docker image, scan an image, publish to GHCR or update image tags. Image publishing is a separate, manual process (see below).

## Container image and GHCR (planned — Stage 2)

> This section describes the intended approach. The Dockerfile and published image do not exist yet; this README will be updated when they do.

- **Registry:** GitHub Container Registry (GHCR)
- **Intended package name:** `ghcr.io/<github-owner>/streamforge-app`
- **Versioning:** explicit version tags such as `0.1.0`; `latest` is not used for deployments.
- **Publishing:** manual, from a developer machine, using a GitHub personal access token with the `write:packages` permission. Never commit tokens or credentials to this repository.
- **Consumption:** the `streamforge-infra` repository references the image repository and tag in its Helm values.

Exact build and push commands, package visibility and credential handling will be documented here once the image is built and pushed.

## Related repositories

- `streamforge-infra` — Kubernetes configuration, Helm chart, Argo CD, infrastructure CI, observability, security and documentation.

## Scope

This service is a small demo workload. The larger e-commerce event-processing platform mentioned in the project concept is a possible future extension and is **not** implemented here.
