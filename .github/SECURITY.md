# Security Policy

## Reporting Security Issues

If you discover a security vulnerability in Daily Tracker, please report it by emailing the maintainer directly. **Do not open a public issue** for security vulnerabilities.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Security Best Practices

### For Users

1. **Protect Your `.env` File**
   - Never commit `.env` to version control
   - Use different secrets for development and production
   - Store production secrets in secure vaults (AWS Secrets Manager, HashiCorp Vault, etc.)

2. **Generate Secure Secrets**
   ```bash
   # Generate secure 256-bit secrets
   openssl rand -hex 32  # For JWT_SECRET
   openssl rand -hex 32  # For ENCRYPTION_KEY
   ```

3. **API Key Security**
   - Rotate API keys regularly
   - Use environment-specific keys (dev, staging, prod)
   - Never share keys in logs, screenshots, or documentation

4. **Database Encryption**
   - The `ENCRYPTION_KEY` encrypts sensitive database fields
   - **Never change this key** after data is encrypted (will corrupt data!)
   - If you must rotate it, decrypt all data first, change key, then re-encrypt

5. **JWT Token Security**
   - JWT tokens expire after 90 days (configurable)
   - Rotate `JWT_SECRET` periodically to force re-authentication
   - Use HTTPS in production to prevent token interception

### For Developers

1. **Dependency Management**
   - Keep dependencies up to date: `uv pip list --outdated`
   - Review security advisories: `safety check`
   - Use `bandit` for Python security scanning: `bandit -r src/`

2. **Input Validation**
   - All API inputs are validated with Pydantic schemas
   - SQL injection prevention via SQLAlchemy ORM
   - Command injection prevention in CLI

3. **Authentication**
   - Passwords hashed with bcrypt (cost factor: 12)
   - JWT tokens with HS256 algorithm
   - API endpoints protected with dependency injection

4. **Code Review**
   - Security-sensitive changes require review
   - CI/CD includes security scanning (Trivy, Bandit, Safety)
   - All PRs must pass security checks

## Security Features

### Built-in Security

- ✅ **Password Hashing**: bcrypt with salt
- ✅ **Database Encryption**: AES encryption for sensitive fields
- ✅ **JWT Authentication**: Secure token-based auth
- ✅ **SQL Injection Protection**: SQLAlchemy ORM
- ✅ **Input Validation**: Pydantic schemas
- ✅ **Secrets Management**: Environment variables
- ✅ **Rate Limiting**: Configurable in deployment
- ✅ **HTTPS Support**: Reverse proxy ready

### CI/CD Security Scanning

- **Bandit**: Python security linter
- **Safety**: Dependency vulnerability scanner
- **Trivy**: Docker image security scanner
- **Ruff**: Code quality and security patterns

## Responsible Disclosure

We follow responsible disclosure practices:

1. Report vulnerabilities privately
2. Allow 90 days for patch development
3. Coordinate public disclosure timing
4. Credit reporters (unless anonymity requested)

## Security Updates

Security updates are released as:
- **Critical**: Immediate patch release
- **High**: Release within 7 days
- **Medium**: Release within 30 days
- **Low**: Included in next regular release

Subscribe to [GitHub Security Advisories](https://github.com/EanHD/tracker/security/advisories) for notifications.

## Questions?

For security questions (not vulnerabilities), open a [GitHub Discussion](https://github.com/EanHD/tracker/discussions).

---

**Last Updated**: October 21, 2025
