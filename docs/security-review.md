# Security Configuration Review

This file reviews the current security posture of the NOVA.Health.API.Server repository and identifies implemented features, partial areas and recommended improvements.

> This review is based on the repository state (Program.cs, AuthController.cs, ApplicationDbContext.cs, Models and DTOs) and does not change any source code.

## Summary table

- HTTPS redirection: Implemented (Program.cs: app.UseHttpsRedirection())
- JWT authentication: Implemented (JwtBearer in Program.cs)
- Password hashing: Implemented (PBKDF2 via Rfc2898DeriveBytes in AuthController)
- Unique user email constraint: Implemented (Index attribute on User.Email + migration snapshot)
- Authorization pattern (ownership checks): Implemented for Profile and Auth endpoints (controllers use ClaimTypes.NameIdentifier)
- Swagger with Bearer security: Implemented in Program.cs (security definition added)
- CORS: Permissive policy configured (AllowAnyOrigin) — Partially Implemented/needs tightening for production


## Findings and recommendations

### Implemented

1. JWT Bearer Authentication
   - Present in Program.cs, tokens validated using TokenValidationParameters.
   - Benefits: stateless authentication, compatible with mobile clients.

2. PBKDF2 Password Hashing
   - Implemented with Rfc2898DeriveBytes and fixed-time comparison. This is secure when iterations are sufficiently large.

3. HTTPS Redirection
   - app.UseHttpsRedirection() is enabled. Hosting must provide TLS certificate in production.

4. Database constraints
   - Unique index on User.Email, FK constraints and indexes on UserId across child tables are present in migrations.

5. DTO usage
   - Controllers use DTOs to avoid exposing EF entities directly (Profile, Auth DTOs are present).


### Partially implemented / Requires attention

1. CORS policy
   - Current policy allows any origin, header and method (configured in Program.cs). For production narrow allowed origins to the Flutter app domains or use environment-specific configuration.
   - Action: Replace AllowAnyOrigin with specific origins in production.

2. Token lifetime and refresh
   - Access tokens issued for 1 hour (in code). No refresh token or revocation mechanism exists.
   - Action: Implement refresh tokens and revocation if longer sessions are required.

3. Logging and sensitive data
   - Ensure logging configuration redacts sensitive fields and tokens. No explicit redaction middleware present.
   - Action: Add structured logging with filtering for PIIs.

4. Password policy
   - Registration DTO enforces a minimum length (8) but there is no enforced complexity policy in code beyond DataAnnotations.
   - Action: Consider server-side password strength checks and rate-limiting for registration and login.

5. File uploads and report storage
   - Reports store FileUrl (string). Ensure uploaded files are stored securely with restricted access and filenames do not expose local file system paths.


### Recommended security improvements

1. Use user-secrets / environment variables / Key Vault for secrets (Jwt:Key, DB passwords). Avoid appsettings.json for secrets in source control.
2. Harden CORS in production.
3. Add rate-limiting on auth endpoints to mitigate brute-force attacks.
4. Implement refresh token lifecycle and revocation.
5. Add global exception handling that hides stack traces in Production and returns consistent error payloads.
6. Enforce strict Content Security Policy (CSP) and security headers via middleware (e.g., HSTS, X-Content-Type-Options).
7. Periodic security dependency scans and updates.


## Classification
- Implemented: HTTPS redirection, JWT authentication, PBKDF2 password hashing, unique email constraint, basic ownership checks for Profile
- Partially Implemented: CORS (present but permissive), Logging (default without PII redaction)
- Recommended: Refresh token implementation, rate limiting, stronger CORS, secret management with Key Vault


## Actionable checklist (short)
- [ ] Move secrets to user-secrets or Key Vault
- [ ] Restrict CORS to known origins in production
- [ ] Add rate limiting for /api/Auth/login
- [ ] Implement refresh tokens and revocation
- [ ] Add structured logging with PII redaction
- [ ] Verify file upload/storage access controls


*This security review reflects the repository state and is advisory. Implement changes in a separate commit after review.*
