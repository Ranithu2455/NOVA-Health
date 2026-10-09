# Security and Authentication

This document describes the authentication and security implementation in the existing NOVA.Health.API.Server repository. The descriptions are derived from the actual code in the repository (Program.cs, AuthController.cs, User model, DTOs and ApplicationDbContext). Where a capability is planned but not implemented, it is explicitly labeled.

## Overview
- Authentication method: JWT Bearer tokens for API endpoints.
- Password storage: PBKDF2-based hashing (Rfc2898DeriveBytes) as implemented in `AuthController`.
- Authorization: `[Authorize]` attributes on protected controllers/actions; controllers identify the authenticated user by `ClaimTypes.NameIdentifier`.
- Transport security: `Program.cs` configures HTTPS redirection (the application enforces HTTPS redirection). In production TLS termination should be configured on the hosting platform.

---

## Registration (actual implementation)
- Endpoint: `POST /api/Auth/register`
- Flow:
  1. Client submits `RegisterRequest` with `Email` and `Password`.
  2. Controller validates input and checks for existing user by email.
  3. `AuthController.HashPassword` uses PBKDF2 (`Rfc2898DeriveBytes.Pbkdf2`) with SHA-256 and a per-user salt and returns a string containing iterations, salt and hash.
  4. The new `User` row is inserted into PostgreSQL via EF Core (`ApplicationDbContext`).
  5. Controller returns 200 OK with minimal user info.
- Security:
  - Passwords are never stored in plaintext.
  - Email uniqueness is enforced at database level.

---

## Login (actual implementation)
- Endpoint: `POST /api/Auth/login`
- Flow:
  1. Client submits `LoginRequest` with `Email` and `Password`.
  2. Controller locates the `User` by email.
  3. `AuthController.VerifyPassword` parses the stored hash (format `iterations.salt.hash`), derives the key using the same iterations and salt, and uses `CryptographicOperations.FixedTimeEquals` to compare.
  4. On success, the controller generates a JWT containing claims:
	 - `ClaimTypes.NameIdentifier` (user id)
	 - `ClaimTypes.Email` (user email)
  5. JWT is signed using HMAC-SHA256 and the `Jwt:Key` configuration value; `Jwt:Issuer` and `Jwt:Audience` are used where configured.
  6. Token lifetime used in the current implementation is 1 hour (created in `AuthController`).
  7. Controller returns `AuthResponse` containing `AccessToken`, `ExpiresAt`, and `UserId`.

---

## JWT Authentication (actual implementation)
- Configuration:
  - Program.cs reads configuration keys `Jwt:Key`, `Jwt:Issuer`, and `Jwt:Audience`.
  - The JWT Bearer authentication is configured using `AddJwtBearer` and `TokenValidationParameters` (issuer/audience/validate lifetime/validate signing key).
  - The signing key is expected to be provided via configuration (user-secrets, environment variables, or appsettings).
- Token usage:
  - Clients include the token in request headers:
	`Authorization: Bearer <token>`
  - The JwtBearer middleware validates the token and sets `HttpContext.User`.
  - Controllers use `User.FindFirstValue(ClaimTypes.NameIdentifier)` to determine the current user id.
- Token expiry: 1 hour (current code sets this when generating the token in AuthController).

---

## Authorization and Ownership
- Pattern used in controllers (actual code):
  - The application enforces resource ownership by relying on the `ClaimTypes.NameIdentifier` claim from the validated JWT and filtering queries by the `UserId` FK.
  - Example: GET /api/Profile obtains the user id from the claim and queries `Profiles` where `UserId == parsedUserId`.
- Do NOT accept `UserId` from client request as the source of truth for ownership checks.

---

## Password security (actual implementation)
- Hash algorithm: PBKDF2 (Rfc2898DeriveBytes) with SHA-256, salt length 16 bytes, output length 32 bytes, iterations = 100,000 (as implemented in `AuthController`).
- Storage format: `iterations.Base64(salt).Base64(hash)` (joined by `.`)
- Verification: derive key using the same parameters and compare with `CryptographicOperations.FixedTimeEquals`.
- Recommendation: enforce strong passwords on the client and server; consider rate limiting on login endpoints.

---

## HTTPS
- `Program.cs` configures `app.UseHttpsRedirection()` — the app redirects HTTP to HTTPS.
- Production TLS must be configured by the hosting environment (e.g., reverse proxy or cloud load balancer). Always use TLS 1.2+.

---

## Sensitive Health Data
- The application stores health-related data (symptoms, medications, sleep, mood, meals, water intake, reports). Protect these as personal health information (PHI):
  - Keep least privilege: only return data for authenticated user.
  - Do not log sensitive content.
  - Control access to production database and backups.
  - Encrypt sensitive artifacts at rest where required (e.g., file storage for reports).

---

## OAuth / External Identity Providers — Planned
- The project currently stores `OAuthProvider` and `OAuthProviderId` fields on the `User` model, but there is no currently implemented OAuth/OpenID Connect external login flow in the repository.
- Planned integration approach:
  - Add external authentication handlers (e.g., Google) and callbacks.
  - On successful external authentication, map or provision a local User row and issue a JWT.
  - Store `OAuthProvider` and `OAuthProviderId` to link accounts.
- Security: Do not store provider secrets in source code; use user-secrets or a secret manager.

---

## Token revocation and refresh tokens (status)
- Current implementation: short-lived access tokens (1 hour) are issued. No refresh token mechanism or token revocation list is implemented in the repository (Planned / Not Implemented).

---

## Summary of implemented authentication features
- Implemented:
  - PBKDF2 password hashing and verification in `AuthController`.
  - JWT generation on login (1 hour lifetime) and validated by JwtBearer middleware in Program.cs.
  - `[Authorize]` on protected endpoints; controllers use claims to enforce ownership.
- Planned / Not Implemented:
  - OAuth / OpenID Connect external login flow.
  - Refresh tokens and token revocation.


*Document created by inspecting `Program.cs`, `AuthController.cs`, `Models/User.cs`, `DTOs/Auth/*`, and `ApplicationDbContext`.*
