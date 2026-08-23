# Audit and Production Harden AI Knowledge Assistant

**Goal**: Thoroughly audit the existing AI Knowledge Assistant repository and complete all incomplete, placeholder, weak, inconsistent, or production-unready parts, without rewriting the project. Preserve architecture, improve incrementally, and ensure production readiness.

## User Review Required

> [!IMPORTANT]
> Review the scope and ordering of tasks. Confirm any preferences for incremental rollout vs. all-at-once changes. Let me know if any items should be deferred.

## Open Questions

> [!QUESTION]
> None at this stage; the plan covers all identified areas. I will raise specific questions if ambiguities arise during implementation.

## Proposed Changes

---
### 1. Repository Audit
- Scan entire codebase for TODO/FIXME, placeholder logic, dead code, broken imports, mismatches, missing validation, security weaknesses, missing tests, etc.
- Generate a comprehensive checklist of issues.

---
### 2. Authentication & Security
- Replace hard‑coded secrets with environment variables (`JWT_SECRET`, `GEMINI_API_KEY`, etc.).
- Add startup validation for required secrets.
- Ensure password hashing via `bcrypt` (or similar) and no logging of raw passwords.
- Validate refresh tokens, implement token revocation checks.
- Add FastAPI dependencies to protect all sensitive endpoints.
- Enforce per‑user resource isolation in all services.

---
### 3. CORS Configuration
- Remove wildcard `*` origins.
- Introduce `CORS_ALLOWED_ORIGINS` env var, default to `http://localhost:5173` for dev.
- Update `.env.example` and `.env` placeholders.

---
### 4. Environment Variables & Secrets
- Audit all external service usages (Gemini, AWS S3, etc.).
- Ensure `.env.example` contains placeholders for all required keys.
- Add entries to `.gitignore` to exclude `.env` and other secret files.

---
### 5. User/Document Isolation
- Extend Chroma metadata schema to include `owner_id`, `document_id`, `source`, `chunk_index`.
- Modify retrieval functions to filter by current user ID.
- Add ownership checks to document listing, deletion, and chat retrieval endpoints.
- Write tests for cross‑user isolation.

---
### 6. Document Ingestion Pipeline
- Add file‑type, size, and filename validation.
- Secure filename handling (prevent path traversal).
- Gracefully handle corrupted/encrypted/empty PDFs.
- Store processing status (`pending`, `ready`, `failed`).
- Move heavy PDF processing and embedding to FastAPI background tasks.
- Ensure idempotent indexing and cleanup on failures.

---
### 7. RAG Pipeline Improvements
- Make chunk size, overlap, and `TOP_K_RETRIEVAL` configurable via env.
- Preserve metadata during chunking and embedding.
- Add relevance filtering before passing chunks to Gemini.
- Update system prompt to enforce source‑only answers, citation style, and avoid hallucination.
- Switch to a supported Gemini model (e.g., `gemini-1.5-pro`) configurable via env.

---
### 8. Source Citations
- Enhance metadata to carry page numbers from PyMuPDF.
- Return structured citation objects in API responses.
- Update frontend UI to display citations clearly (document name, page, excerpt).

---
### 9. Document Management
- Ensure CRUD endpoints enforce ownership.
- On deletion: remove DB record, delete stored PDF, purge related Chroma vectors.
- Implement proper error handling and cleanup for partial failures.

---
### 10. Chat / Conversation Management
- Verify conversations are linked to user IDs.
- Enforce ownership on chat retrieval.
- Persist messages with timestamps and associated document IDs.
- Improve frontend chat UX: loading spinners, error messages, long‑response handling.

---
### 11. Frontend Quality
- Verify auth flow (login, register, token refresh, logout).
- Replace hard‑coded API URLs with env‐based config (`VITE_API_URL`).
- Add loading/empty/error states for document list and chat.
- Ensure responsive design and no console errors.
- Preserve existing design; add micro‑animations for polished UX.

---
### 12. Database & Migrations
- Review SQLAlchemy models for proper relationships and indexes.
- Replace any `Base.metadata.create_all()` usage with Alembic migrations.
- Add migration scripts for any schema changes (e.g., `owner_id` foreign keys, document status column).

---
### 13. Storage Abstraction
- Introduce a storage interface with two implementations: local filesystem and S3.
- Use env vars (`STORAGE_BACKEND=local|s3`, `AWS_*`) to select backend.
- Ensure existing local storage continues to work out‑of‑the‑box.

---
### 14. Testing
- Write/expand pytest suites covering:
  * Auth (register, login, refresh, protected routes)
  * Authorization (user isolation for docs, chats)
  * Document pipelines (valid/invalid PDFs, size limits, corrupted files)
  * RAG retrieval and citation correctness
  * API error handling
- Aim for >80% coverage of critical paths.

---
### 15. Observability & Error Handling
- Add structured logging (using `loguru` or Python `logging`) with appropriate levels.
- Mask sensitive data in logs.
- Return consistent JSON error responses with error codes.

---
### 16. Docker & Deployment
- Review Dockerfiles for secret handling (no build‑time env vars for secrets).
- Update `docker-compose.yml` to wait for PostgreSQL readiness (`depends_on` + healthcheck script).
- Ensure volumes for local storage and PostgreSQL data.
- Add health endpoint checks.

---
### 17. Code Quality
- Run `ruff`/`flake8`/`black` (or equivalent) to clean imports, formatting, and lint issues.
- Remove dead code and duplicated logic.
- Ensure type hints are present where appropriate.

---
### 18. README Update
- Revise README to reflect final architecture, env vars, setup steps, Docker usage, testing instructions, and security considerations.

---
### 19. Real API Integrations
- Wire Gemini API with real calls, configurable model name.
- Implement S3 storage integration (using `boto3`).
- Validate presence of required env vars at startup.

---
### 20. Final Verification
- Run full end‑to‑end verification steps listed in the request.
- Iterate until no errors remain.

## Verification Plan

- Execute lint/format checks.
- Run `pytest` and ensure all tests pass.
- Build and start Docker stack (`docker compose up --build`).
- Manually test API endpoints via Postman or curl.
- Perform UI smoke test in browser.
- Verify cross‑user isolation, citations, and token flows.

---
**Implementation will proceed in the order above, grouping related changes to minimize disruption.**
