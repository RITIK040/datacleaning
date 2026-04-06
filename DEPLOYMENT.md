# Quant Data Pro - Containerization & Deployment Guide

## Overview
Your Streamlit application is now fully containerized with an optimized multi-stage Dockerfile, GitHub Actions CI/CD pipelines, and deployment configurations.

---

## 1. Local Development & Testing

### Build the Docker Image
```bash
docker build -t quant-data-pro:latest .
```

### Run with Docker Compose (Recommended)
```bash
docker compose up
```
Access the app at: `http://localhost:8501`

### Run Single Container
```bash
docker run -d --name quant-data-pro -p 8501:8501 quant-data-pro:latest
```

### View Logs
```bash
docker compose logs -f app
# or
docker logs -f quant-data-pro
```

### Stop Container
```bash
docker compose down
# or
docker stop quant-data-pro
```

---

## 2. Dockerfile Optimization Details

### Multi-Stage Build
- **Builder Stage**: Compiles wheels for all Python dependencies (reduces final image size)
- **Final Stage**: Only includes runtime dependencies and compiled wheels

### Size Benefits
- Removes build tools (gcc, make, etc.) from final image
- Eliminates source code and intermediate artifacts
- Final image size: ~500-700MB (vs 1.5GB+ single-stage)

### Security
- Non-root user (`streamlit:1000`) runs the container
- Minimal dependencies reduce attack surface
- Health checks monitor container status

### Environment Variables
```
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_LOGGER_LEVEL=info
```

---

## 3. GitHub Actions CI/CD Setup

### Required Secrets (GitHub Settings → Secrets)

#### For Docker Hub Push
- `DOCKER_USERNAME`: Your Docker Hub username
- `DOCKER_PASSWORD`: Your Docker Hub access token (not password)

#### For GitHub Container Registry (Optional)
- `GITHUB_TOKEN`: Auto-provided by GitHub

### Workflows Included

#### A. `docker-build.yml` - Build & Test
- Triggers: Push to main/develop, PRs to main, tag pushes
- Actions:
  - Builds image
  - Pushes to GitHub Container Registry (ghcr.io)
  - Tests image on PR (no push)
  - Uses build cache for faster builds

**Access images:**
```bash
docker pull ghcr.io/<your-username>/quant_data_tool:latest
```

#### B. `docker-hub-push.yml` - Push to Docker Hub
- Triggers: Push to main, manual workflow dispatch
- Actions:
  - Builds image
  - Pushes to Docker Hub
  - Auto-tags with branch, SHA, latest

**Access images:**
```bash
docker pull <your-username>/quant-data-pro:latest
```

#### C. `quality-checks.yml` - Linting & Tests
- Triggers: Push to main/develop, PRs
- Actions:
  - Flake8 linting
  - Black code formatting check
  - isort import sorting check
  - Pytest test runner (if tests exist)

---

## 4. Deployment Options

### Option A: Docker Hub + Docker Swarm
```bash
# Deploy to Docker Swarm
docker service create \
  --name quant-data-pro \
  --publish 8501:8501 \
  --replicas 1 \
  <your-username>/quant-data-pro:latest
```

### Option B: Kubernetes
```bash
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: quant-data-pro
spec:
  replicas: 2
  selector:
    matchLabels:
      app: quant-data-pro
  template:
    metadata:
      labels:
        app: quant-data-pro
    spec:
      containers:
      - name: app
        image: <your-username>/quant-data-pro:latest
        ports:
        - containerPort: 8501
        env:
        - name: STREAMLIT_SERVER_HEADLESS
          value: "true"
        livenessProbe:
          httpGet:
            path: /_stcore/health
            port: 8501
          initialDelaySeconds: 40
          periodSeconds: 30
---
apiVersion: v1
kind: Service
metadata:
  name: quant-data-pro
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8501
  selector:
    app: quant-data-pro
EOF
```

### Option C: Cloud Run (GCP)
```bash
# Push to Artifact Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/quant-data-pro

# Deploy
gcloud run deploy quant-data-pro \
  --image gcr.io/PROJECT_ID/quant-data-pro \
  --platform managed \
  --region us-central1 \
  --port 8501 \
  --memory 1Gi
```

### Option D: AWS ECS
```bash
# Create ECR repository
aws ecr create-repository --repository-name quant-data-pro

# Push image
aws ecr get-login-password | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker tag quant-data-pro:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/quant-data-pro:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/quant-data-pro:latest

# Deploy with ECS CLI or CloudFormation
```

---

## 5. Production Checklist

- [ ] Set GitHub Secrets (DOCKER_USERNAME, DOCKER_PASSWORD)
- [ ] Update image name in docker-hub-push.yml if needed
- [ ] Create tagged release (v1.0.0) to trigger GitHub Actions
- [ ] Verify images are pushed to registry
- [ ] Test pulling image from registry in clean environment
- [ ] Configure resource limits for production:
  ```bash
  docker run -m 2g --cpus=1.5 -d quant-data-pro:latest
  ```
- [ ] Set up monitoring/logging (Docker logs, CloudWatch, etc.)
- [ ] Configure auto-restart policy:
  ```bash
  docker run --restart=always -d quant-data-pro:latest
  ```
- [ ] Test healthcheck in production environment

---

## 6. Git Workflow Setup

### Initialize Git (if not done)
```bash
git init
git add .
git commit -m "Initial commit: containerized Quant Data Pro application"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

### Create Feature Branch
```bash
git checkout -b feature/new-feature
# Make changes
git add .
git commit -m "Add new feature"
git push origin feature/new-feature
# Create PR on GitHub
```

### Tag Release for Deployment
```bash
git tag v1.0.0
git push origin v1.0.0
# This triggers docker-build.yml with semantic versioning
```

---

## 7. Troubleshooting

### Container won't start
```bash
docker logs quant-data-pro
# Check for missing dependencies or port conflicts
docker ps -a
```

### Port 8501 already in use
```bash
# Find and kill existing process
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Or use different port
docker run -p 8502:8501 quant-data-pro:latest
```

### GitHub Actions failing
- Check Actions tab in GitHub for detailed logs
- Verify secrets are set correctly
- Ensure Dockerfile builds locally first

### Image size too large
```bash
docker inspect quant-data-pro:latest | grep -i size
# Expected: 500-700MB after multi-stage build
```

---

## 8. Optimization Tips

### Reduce Build Time
- Dockerfile layers are cached; put frequently-changing code last
- Use `.dockerignore` to exclude unnecessary files
- Consider using `docker buildx` for parallel builds

### Reduce Image Size
- Current: Multi-stage build already optimized
- Next: Use distroless base image (python:3.11-distroless) for ~200MB
- Use Alpine Linux (python:3.11-alpine) for minimal size

### Faster Pulls
- Use smaller tags: `latest` < `main` < `sha-abc123`
- Store in private registry close to deployment region

---

## 9. Files Created

```
.
├── Dockerfile                          # Multi-stage optimized build
├── docker-compose.yml                  # Local dev environment
├── .dockerignore                       # Build context optimization
├── .github/
│   └── workflows/
│       ├── docker-build.yml            # Build to GitHub Container Registry
│       ├── docker-hub-push.yml         # Push to Docker Hub
│       └── quality-checks.yml          # Linting & tests
└── (your app files)
```

---

## 10. Next Steps

1. Set GitHub Secrets for automated deployments
2. Choose a deployment platform (Kubernetes, ECS, Cloud Run, etc.)
3. Monitor container logs and set up alerting
4. Regularly update base image (`python:3.11-slim`) for security patches
5. Consider multi-region deployment for high availability

---

## Quick Command Reference

```bash
# Build
docker build -t quant-data-pro .

# Run locally
docker compose up -d
docker run -p 8501:8501 quant-data-pro:latest

# Push to registry
docker tag quant-data-pro:latest myrepo/quant-data-pro:v1.0.0
docker push myrepo/quant-data-pro:v1.0.0

# Monitor
docker logs -f quant-data-pro
docker stats quant-data-pro

# Cleanup
docker compose down
docker system prune -a
```
