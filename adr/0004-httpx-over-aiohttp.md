# ADR 0004: Standardize on httpx, drop aiohttp

- **Status:** Accepted
- **Date / version:** 2026-06-19 (uvicore 0.4.x)

> Backfilled from commit `d3e3c43`.

## Context

The shared async HTTP client service used **aiohttp (3.11)**, while **httpx** was already present for
testing. Carrying two async HTTP libraries is redundant; aiohttp also had teardown friction in the
test lifecycle, and httpx aligns naturally with the Starlette/FastAPI ecosystem (and our tests use
`httpx.AsyncClient` directly).

## Decision

Standardize on **httpx (0.28.1)** as the single async HTTP stack and **remove aiohttp**. Update the
`http_client` package provider/service and the mailgun mail backend to httpx. Tests use
`httpx.AsyncClient` directly rather than Starlette's `TestClient`.

## Consequences

- **+** One async HTTP stack to learn, pin, and secure; ~700 fewer transitive lockfile lines.
- A defensive condition was later added to the httpx teardown (`31e82c7`, 2026-06-20) to avoid
  shutdown errors.
- Note: Starlette's `TestClient` nudges toward an httpx2 package, but that only matters if we adopt
  it — we don't.
