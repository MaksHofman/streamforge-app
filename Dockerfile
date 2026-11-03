FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

# Run as a non-root user with a numeric UID (works with runAsNonRoot in Kubernetes)
RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin appuser

WORKDIR /srv

COPY app/ ./app/

USER 10001

EXPOSE 8080

CMD ["python", "-m", "app.server"]