# Security Policy

## Reporting a Vulnerability
Raise a GitHub issue with the `security` label or Jira ticket in the `SECURITY` project. Please include a detailed description of the vulnerability, steps to reproduce, and any relevant screenshots or logs.

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
