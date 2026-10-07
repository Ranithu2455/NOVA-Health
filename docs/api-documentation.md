# API Documentation

This document lists the API endpoints implemented in the NOVA.Health.API.Server project. Only endpoints that actually exist in the repository source code are documented here. Planned endpoints are listed under "Planned API Endpoints".

All endpoints use JSON request and response bodies and follow REST conventions.

## Global notes
- Base path: `/api`
- Authentication: JWT Bearer for protected endpoints. Include header `Authorization: Bearer <token>`.
- All controllers use attribute routing and the controller name as the route prefix (e.g., `AuthController` → `/api/Auth`).
- Validation: DTOs use DataAnnotations; controllers return 400 BadRequest when ModelState is invalid.

---

## 1. Authentication

### POST /api/Auth/register
- Purpose: Register a new user account.
- Authentication: Anonymous
- Request body: `RegisterRequest` DTO (`DTOs/Auth/RegisterRequest.cs`)
  - Properties: `Email` (required, email), `Password` (required, min length 8)
- Response:
  - 200 OK: returns a simple object with message, userId and email (existing implementation returns minimal info).
  - 409 Conflict: if email already exists
  - 400 BadRequest: invalid payload
- Notes: Passwords are hashed using PBKDF2 (see security documentation). No plaintext password stored.

### POST /api/Auth/login
- Purpose: Authenticate user and return a JWT access token.
- Authentication: Anonymous
- Request body: `LoginRequest` DTO (`DTOs/Auth/LoginRequest.cs`)
  - Properties: `Email` (required), `Password` (required)
- Response:
  - 200 OK: `AuthResponse` DTO (`DTOs/Auth/AuthResponse.cs`)
	- `AccessToken` (JWT), `ExpiresAt` (DateTimeOffset), `UserId` (GUID)
  - 401 Unauthorized: invalid credentials
  - 400 BadRequest: invalid payload
- Notes: JWT generated with claims containing `ClaimTypes.NameIdentifier` (UserId) and `ClaimTypes.Email`; token expiration is set to 1 hour in the current implementation.

### GET /api/Auth/me
- Purpose: Return basic information about the currently authenticated user.
- Authentication: Required (Bearer JWT)
- Request: No body
- Response:
  - 200 OK: object containing `UserId` and `Email` of the authenticated user.
  - 401 Unauthorized: missing or invalid JWT

---

## 2. Profile

### GET /api/Profile
- Purpose: Retrieve profile for the authenticated user.
- Authentication: Required (Bearer JWT)
- Request: No body
- Response:
  - 200 OK: profile object (fields from `Profile` model via `ProfileResponse` DTO)
	- Fields: `ProfileId`, `UserId`, `FirstName`, `LastName`, `DateOfBirth`, `Gender`, `Height`, `Weight`, `BloodGroup`, `CreatedAt`, `UpdatedAt`
  - 401 Unauthorized: invalid JWT or user id claim missing
  - 404 NotFound: profile does not exist for the user
- Notes: Controller enforces ownership by reading `ClaimTypes.NameIdentifier` from JWT and querying `Profiles` by `UserId`.

### PUT /api/Profile
- Purpose: Update profile for the authenticated user.
- Authentication: Required (Bearer JWT)
- Request body: `UpdateProfileRequest` DTO (`DTOs/Profile/UpdateProfileRequest.cs`)
  - Fields: `FirstName` (required), `LastName`, `DateOfBirth`, `Gender`, `Height`, `Weight`, `BloodGroup`
- Response:
  - 200 OK: updated profile object
  - 400 BadRequest: invalid model
  - 401 Unauthorized: invalid JWT
  - 404 NotFound: profile not found for user
- Notes: The controller updates only allowed fields and sets `UpdatedAt`. Ownership is enforced via JWT.

---

## Planned API Endpoints (Not Yet Implemented)
The repository contains DTOs for many resource types (Medication, Symptom, Sleep, Mood, Water, Meal, Report, EmergencyContact) but the corresponding controllers are not present in the codebase. These endpoints are planned but not implemented in the current repository snapshot.

Planned controllers/endpoints (expected design):
- Medication
  - GET /api/medications
  - GET /api/medications/{id}
  - POST /api/medications
  - PUT /api/medications/{id}
  - DELETE /api/medications/{id}
- Symptom
  - GET /api/symptoms
  - GET /api/symptoms/{id}
  - POST /api/symptoms
  - PUT /api/symptoms/{id}
  - DELETE /api/symptoms/{id}
- Sleep
  - GET /api/sleep
  - GET /api/sleep/{id}
  - POST /api/sleep
  - PUT /api/sleep/{id}
  - DELETE /api/sleep/{id}
- Mood
  - GET /api/moods
  - POST /api/moods
  - PUT /api/moods/{id}
  - DELETE /api/moods/{id}
- Water
  - GET /api/water
  - POST /api/water
  - PUT /api/water/{id}
  - DELETE /api/water/{id}
- Meal
  - GET /api/meals
  - POST /api/meals
  - PUT /api/meals/{id}
  - DELETE /api/meals/{id}
- Report
  - GET /api/reports
  - GET /api/reports/{id}
  - POST /api/reports
  - DELETE /api/reports/{id}
- EmergencyContact
  - GET /api/emergency-contacts
  - POST /api/emergency-contacts
  - PUT /api/emergency-contacts/{id}
  - DELETE /api/emergency-contacts/{id}

> Note: The DTOs exist under `DTOs/` for these resources but controllers are not implemented in the repository at the time of this documentation.

---

## API Style and Conventions
- RESTful resources under `/api/*`.
- JSON input/output.
- Use of DTOs for requests and responses; EF entities are not returned directly.
- Status codes:
  - 200 OK for successful GET/PUT
  - 201 Created for successful POST (where implemented)
  - 400 BadRequest for validation errors
  - 401 Unauthorized for missing/invalid tokens
  - 404 NotFound for missing resources
  - 409 Conflict for duplicate resources (e.g., existing email)
  - 500 InternalServerError for unexpected errors
- Swagger (OpenAPI) is configured in Program.cs and provides interactive API documentation in Development.

---

*Document generated by inspecting Controllers and DTOs in the repository. Only implemented endpoints are documented as "Implemented" above; planned endpoints are clearly labeled.*
