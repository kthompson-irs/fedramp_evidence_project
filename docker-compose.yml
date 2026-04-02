services:
  evidence-api:
    build: .
    container_name: fedramp-evidence-api
    env_file:
      - .env
    ports:
      - "8000:8000"
    restart: unless-stopped

  evidence-worker:
    build: .
    container_name: fedramp-evidence-worker
    env_file:
      - .env
    command: ["python", "-m", "app.services.scheduler"]
    restart: unless-stopped
