# Security Policy

## Reporting a Vulnerability
Please email security@insightai.example (placeholder) with details.
Do not open public GitHub issues for security vulnerabilities.

## Supported Versions
Only the latest `main` branch and the most recent tagged release receive
security patches.

## Practices
- JWT-based authentication with short-lived access tokens + refresh tokens.
- Passwords hashed with bcrypt/argon2.
- All traffic served over HTTPS/TLS in production.
- Parameterized queries / ORM usage only — no raw SQL string interpolation.
- Dependency scanning via Dependabot and CodeQL (see .github/workflows).
- Secrets managed via environment variables / AWS Secrets Manager, never
  committed to source control.
