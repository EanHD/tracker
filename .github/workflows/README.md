# GitHub Actions Workflows

This directory contains CI/CD workflows for Daily Tracker.

## Workflows

### ci-cd.yml

Main CI/CD pipeline that runs on every push, pull request, and tag.

**Triggers:**
- Push to `main` or `develop`
- Pull requests to `main` or `develop`
- Tags matching `v*` (e.g., v1.0.0)
- Manual trigger via GitHub UI

**Jobs:**

1. **Lint & Type Check** (`lint`)
   - Runs `ruff` for linting and formatting
   - Runs `mypy` for type checking
   - Fast fail to catch issues early

2. **Test Suite** (`test`)
   - Runs pytest with coverage
   - Uploads coverage to Codecov
   - Matrix testing (Python 3.12)
   - Creates coverage artifacts

3. **Security Scan** (`security`)
   - Runs `bandit` for security issues
   - Runs `safety` for dependency vulnerabilities
   - Results uploaded to GitHub Security tab

4. **Build Docker Image** (`build-docker`)
   - Builds Docker image with BuildKit
   - Pushes to Docker Hub
   - Scans with Trivy for vulnerabilities
   - Uses layer caching for speed

5. **Deploy to Production** (`deploy-production`)
   - Only runs on version tags (e.g., v1.0.0)
   - SSHs to production server
   - Pulls latest image
   - Runs docker-compose up
   - Health check verification
   - Slack notification

6. **Create Release** (`release`)
   - Auto-generates changelog from commits
   - Creates GitHub Release
   - Attaches Docker image info
   - Links to documentation

## Required Secrets

Configure these in GitHub Settings → Secrets and variables → Actions:

### Docker Hub
- `DOCKER_USERNAME` - Docker Hub username
- `DOCKER_PASSWORD` - Docker Hub password or access token

### Production Deployment
- `PROD_HOST` - Production server IP or hostname
- `PROD_USERNAME` - SSH username (e.g., `tracker`)
- `PROD_SSH_KEY` - Private SSH key for authentication

### Notifications (Optional)
- `SLACK_WEBHOOK` - Slack webhook URL for notifications
- `CODECOV_TOKEN` - Codecov token (optional, public repos)

## Setup Instructions

### 1. Docker Hub

Create a Docker Hub account and access token:

```bash
# Login to Docker Hub
docker login

# Create access token at https://hub.docker.com/settings/security
# Add to GitHub Secrets as DOCKER_USERNAME and DOCKER_PASSWORD
```

### 2. Production Server SSH

Generate SSH key and add to server:

```bash
# Generate SSH key (no passphrase)
ssh-keygen -t ed25519 -C "github-actions" -f github_actions_key

# Copy public key to server
ssh-copy-id -i github_actions_key.pub tracker@your-server.com

# Add private key to GitHub Secrets as PROD_SSH_KEY
cat github_actions_key | gh secret set PROD_SSH_KEY

# Add host and username
gh secret set PROD_HOST --body "your-server.com"
gh secret set PROD_USERNAME --body "tracker"
```

### 3. Slack Notifications (Optional)

Create Slack incoming webhook:

1. Go to https://api.slack.com/apps
2. Create new app
3. Enable Incoming Webhooks
4. Create webhook URL
5. Add to GitHub Secrets:

```bash
gh secret set SLACK_WEBHOOK --body "https://hooks.slack.com/services/..."
```

## Usage

### Automatic Runs

Workflows run automatically on:

- **Every push to `main`** - Full CI/CD pipeline
- **Every PR** - Lint, test, security (no deploy)
- **Version tags** - Full pipeline + deploy + release

### Manual Runs

Trigger manually via GitHub UI:

1. Go to Actions tab
2. Select "CI/CD Pipeline"
3. Click "Run workflow"
4. Choose branch
5. Click "Run workflow"

### Version Tagging

To create a release:

```bash
# Tag version
git tag -a v1.0.0 -m "Release v1.0.0"

# Push tag
git push origin v1.0.0

# This triggers:
# - Build Docker image: daily-tracker:1.0.0
# - Deploy to production
# - Create GitHub Release
```

## Workflow Status Badges

Add to README.md:

```markdown
![CI/CD](https://github.com/EanHD/tracker/workflows/CI/CD%20Pipeline/badge.svg)
[![codecov](https://codecov.io/gh/EanHD/tracker/branch/main/graph/badge.svg)](https://codecov.io/gh/EanHD/tracker)
```

## Best Practices

1. **Test locally before pushing**
   ```bash
   # Run tests
   pytest
   
   # Check linting
   ruff check src/
   
   # Build Docker image
   docker build -t tracker:test .
   ```

2. **Use branch protection**
   - Require CI to pass before merging
   - Require reviews for PRs
   - Settings → Branches → Add rule

3. **Keep secrets secure**
   - Never commit secrets to repo
   - Use GitHub Secrets for sensitive data
   - Rotate secrets regularly

4. **Monitor workflow runs**
   - Check Actions tab for failures
   - Enable email notifications
   - Set up Slack alerts

5. **Version tagging strategy**
   - Semantic Versioning (v1.0.0)
   - `v*.*.*` for production releases
   - `v*.*.*-beta.*` for beta releases
   - `v*.*.*-alpha.*` for alpha releases

## Troubleshooting

### Workflow fails at Docker build

**Symptom:** Docker build step fails

**Solutions:**
- Check Dockerfile syntax: `docker build -t test .`
- Verify secrets are set: `DOCKER_USERNAME`, `DOCKER_PASSWORD`
- Check Docker Hub rate limits

### Deployment fails

**Symptom:** SSH connection or deployment fails

**Solutions:**
- Verify SSH key is correct and has no passphrase
- Check server is accessible: `ssh tracker@your-server.com`
- Ensure docker-compose.yml exists on server
- Check production server logs: `ssh tracker@server 'cd /opt/tracker && docker-compose logs'`

### Tests fail in CI but pass locally

**Symptom:** Tests pass locally but fail in GitHub Actions

**Solutions:**
- Check Python version matches (3.12)
- Ensure all dependencies in pyproject.toml
- Check for environment-specific issues
- Run tests with same conditions: `pytest --maxfail=1 -v`

### Coverage upload fails

**Symptom:** Codecov upload step fails

**Solutions:**
- Codecov token may be required for private repos
- Check coverage.xml is generated
- Verify Codecov is enabled for repo

## Advanced Configuration

### Matrix Testing

Test multiple Python versions:

```yaml
strategy:
  matrix:
    python-version: ['3.11', '3.12', '3.13']
```

### Conditional Jobs

Run jobs only on specific conditions:

```yaml
if: github.event_name == 'push' && github.ref == 'refs/heads/main'
```

### Environment Secrets

Use environment-specific secrets:

```yaml
environment:
  name: production
  url: https://tracker.yourdomain.com
```

### Caching Dependencies

Speed up builds with caching:

```yaml
- name: Cache uv
  uses: actions/cache@v3
  with:
    path: ~/.cache/uv
    key: ${{ runner.os }}-uv-${{ hashFiles('pyproject.toml') }}
```

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [SSH Action](https://github.com/appleboy/ssh-action)
- [Codecov Action](https://github.com/codecov/codecov-action)

---

**Need Help?** Check the main documentation or open an issue on GitHub.
