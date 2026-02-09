# api-client-kit

‼️ **Work in progress** — active development.

A small, opinionated toolkit for building robust Python API clients on top of **httpx** (sync + async).

## What it is
`api-client-kit` provides composable primitives you can reuse across client libraries:
- Sync + async client base (httpx)
- Auth plugins (API key, bearer, OAuth2 client-credentials)
- Retries + backoff (policy-based)
- Rate-limit handling (Retry-After, optional limiter)
- Pagination helpers (cursor, Link header)
- Structured errors with safe redaction
- Observability hooks (logging/metrics/tracing adapters)

## Status
- Current: placeholder bootstrap + API design
- Target: **v0.1.0** — first usable release with core client + errors + auth + retries + pagination

## Roadmap (v0.1)
- [ ] Core SyncClient/AsyncClient with shared pipeline
- [ ] Structured errors + safe redaction
- [ ] Auth: API key, bearer, OAuth2 client-credentials
- [ ] Retry policy + backoff
- [ ] Retry-After handling
- [ ] Pagination: cursor + Link header
- [ ] Hooks + logging hook
- [ ] Full tests + CI + PyPI release

## License
MIT
