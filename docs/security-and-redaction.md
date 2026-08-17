# Security and Redaction

This document defines the security and redaction principles for `api-client-kit`.

`api-client-kit` is intended to help developers build API clients that may handle credentials, tokens, headers, request payloads, response payloads, and error context. Security and redaction are therefore core design concerns, not optional add-ons.

The project is currently under active early development. Reusable header,
diagnostic-URL, structured-payload, and bounded body-snippet redaction
primitives and the initial package error taxonomy are available; automatic safe
diagnostic integration remains future work.

Current public usage:

```python
from api_client_kit.redaction import (
    redact_headers,
    redact_payload,
    redact_url,
    safe_body_snippet,
)
```

## Security Goals

The package should help users build API clients that are:

* safe around credentials
* safe around logs and errors
* testable without real secrets
* explicit about sensitive data
* predictable in failure modes
* conservative about what gets exposed in diagnostics

The package must avoid leaking credentials through:

* exception messages
* exception `repr`
* logs
* hook payloads
* debug output
* request context
* response context
* test fixtures
* documentation examples

## Sensitive Data

Treat the following as sensitive by default:

* `Authorization` headers
* bearer tokens
* API keys
* refresh tokens
* access tokens
* cookies
* session IDs
* passwords
* client secrets
* private keys
* PyPI tokens
* GitHub tokens
* query parameters containing secrets
* payload fields containing secrets
* customer data
* sensitive request bodies
* sensitive response bodies

When uncertain, prefer redaction.

## Header Redaction

`redact_headers` returns a new `httpx.Headers` collection with sensitive values
replaced by `<redacted>`. It recognizes the eight approved names listed below
with exact, case-insensitive matching, preserves safe and repeated headers, and
does not mutate its input. Clients, errors, logs, and hooks do not
automatically invoke it yet.

Headers that should be redacted include:

```text
Authorization
Proxy-Authorization
Cookie
Set-Cookie
X-API-Key
API-Key
X-Auth-Token
X-Access-Token
```

Example:

```text
Authorization: <redacted>
X-API-Key: <redacted>
```

Header matching should be case-insensitive.

## Query Parameter Redaction

URLs may contain credentials or tokens in query parameters.

`redact_url` returns a safe diagnostic string. It recognizes the thirteen
approved names below with exact, case-insensitive matching on decoded query
names, replaces valued sensitive parameters with `<redacted>`, preserves
repeated parameters and safe query text where practical, redacts URL userinfo,
and strips fragments. It does not mutate its input. It is a standalone helper;
clients, errors, logs, and hooks do not automatically invoke it yet.

Query parameters that should be redacted include:

```text
token
access_token
refresh_token
api_key
apikey
key
secret
client_secret
password
session
session_id
auth
authorization
```

Example:

```text
https://api.example.com/items?api_key=<redacted>&page=2
```

Non-sensitive query parameters may remain visible when useful for debugging.

## Payload Redaction

`redact_payload` sanitizes common structured Python payloads as a standalone
helper. It recursively rebuilds `Mapping`, `list`, and `tuple` values: mappings
always become plain `dict` objects, while lists and tuples retain their types.
Supported caller-owned containers are never mutated. All other values,
including opaque custom objects and unsupported containers such as `set` and
`frozenset`, are left unchanged and are not inspected.

It recognizes the fourteen approved sensitive string keys below with exact,
case-insensitive matching. A matching key replaces its entire associated value
with `<redacted>` without first traversing that value. Non-string mapping keys
are preserved exactly and their values continue to recurse. Payload keys are
structured data and are not URL- or form-decoded.

Sensitive payload keys include:

```text
token
access_token
refresh_token
api_key
apikey
key
secret
client_secret
password
auth
authorization
cookie
session
session_id
```

Example input:

```json
{
  "username": "alice",
  "password": "real-password",
  "metadata": {
    "api_key": "real-key"
  }
}
```

Safe output:

```json
{
  "username": "alice",
  "password": "<redacted>",
  "metadata": {
    "api_key": "<redacted>"
  }
}
```

Safe-key structured values preserve enough shape to make debugging useful
without exposing approved secret values. This is not a generic deep-copy API:
opaque leaves may be returned by identity. It performs no arbitrary value/text
scanning, and it does not inspect object attributes, dataclasses, Pydantic
models, sets, generic iterables, or generators. Cyclic or pathologically deep
supported structures are outside this helper's contract.

Clients, errors, logs, and hooks do not automatically invoke `redact_payload`
yet.

## Body Snippets

`safe_body_snippet` returns a standalone safe diagnostic string for `str` or
`bytes` bodies. It is not raw body content or a re-sendable payload. Empty
bodies return `<empty>`. Safe plain text keeps its formatting where practical;
the final text or JSON rendering is at most 1024 characters and longer output
ends with `…<truncated>`.

Callers may pass known request-side secret values through `secret_values`.
Nonempty values are replaced exactly, case-sensitively, everywhere they occur;
there is no generic token detection or arbitrary-text secret heuristic. This
also prevents known credentials from leaking across the truncation boundary.
Automatic collection of sensitive request values is not implemented yet.

Bytes decode only with strict UTF-8 and then use the text behavior. Bytes that
cannot decode as UTF-8 return only `<binary body: N bytes>`, exposing the byte
count rather than raw content.

Text at or below a 65,536-character/byte structured parsing ceiling is parsed
best-effort as JSON. Valid JSON is passed through `redact_payload`, serialized
as compact deterministic JSON, then scrubbed for caller-supplied secret values.
Malformed JSON falls back to plain text without key-based heuristics. Larger
bodies skip structured parsing and use the bounded text path.

Clients, errors, logs, and hooks do not automatically invoke
`safe_body_snippet` yet. Structured package errors, automatic diagnostic
context, RequestContext secret-value discovery, logging hooks, and
observability hooks remain future work.

## Structured Errors

`ApiClientError` is the current root package exception. It can store optional
diagnostic context that has already been prepared by its caller. `str(error)`
renders only the safe message and `repr(error)` renders only the class and
message, so context is never automatically dumped into either representation.
The base error does not sanitize arbitrary caller-supplied context; automatic
safe context construction remains future work.

`NetworkError` and `TimeoutError` are current package error types. They inherit
the message-only `str()` and class-plus-message `repr()` behavior, so optional
context is not automatically rendered. They do not store raw underlying
transport exceptions as fields; native `raise ... from ...` chaining is the
intended cause mechanism. HTTPX-to-package mapping is not implemented yet, and
clients do not yet integrate package errors.

`HttpStatusError` and its specialized HTTP status subclasses are also current
package error types. An HTTP status error stores package `ResponseData`, with
explicit raw HTTPX access available only through `error.response.raw`; there is
no raw underlying-response alias directly on the exception. Attaching a response
does not sanitize it, but response contents and inherited context are not
automatically rendered by `str()` or `repr()`. Safe diagnostic-context
construction, automatic status mapping, and client integration remain future
work; response body diagnostics do not yet use the redaction primitives.

Decode error types remain future work.

Future structured errors should include useful context without exposing secrets.

Planned error context may include:

* HTTP method
* sanitized URL
* sanitized request headers
* response status code
* sanitized response headers
* safe response body snippet
* retry attempt count
* request ID or correlation ID if available
* safe metadata

Structured errors should not include:

* raw authorization headers
* raw cookies
* raw API keys
* raw tokens
* unbounded request bodies
* unbounded response bodies
* private keys
* credentials from environment variables

## Logs

Logs should follow the same redaction rules as errors.

A logging hook should never log raw credentials.

Safe logs may include:

* method
* sanitized URL
* status code
* elapsed time
* retry attempt
* sanitized error type
* safe request ID
* safe metadata

Unsafe logs include:

* raw `Authorization` headers
* raw cookies
* raw tokens
* raw API keys
* raw sensitive payload fields
* full unbounded response bodies

## Hooks

Observability hooks should receive sanitized or explicitly safe context.

Hook payloads should not become a path for secret leakage.

If a hook receives raw context for advanced use cases, that behavior must be explicit, documented, and opt-in.

Default hooks should be safe.

## Tests

Security and redaction behavior must be tested.

Tests should verify that secrets do not appear in:

* sanitized headers
* sanitized URLs
* sanitized payloads
* exception strings
* exception `repr`
* logs
* hook payloads
* safe body snippets

Tests must use fake secrets only.

Good fake values:

```text
test-api-key
test-token
secret-value
password-value
```

Never use real credentials in tests.

## Documentation Examples

Documentation examples must not contain real secrets.

Use obvious placeholders:

```text
<api-key>
<token>
<redacted>
test-api-key
test-token
```

Do not include real service credentials, real tokens, private keys, screenshots containing secrets, or customer data.

## Environment Files

Do not commit real environment files.

The repository may include:

```text
.env.example
```

The repository must not include:

```text
.env
.env.local
.env.production
.env.* containing real secrets
```

`.env.example` should contain only safe placeholders.

## Local Development

Local development should not require real API credentials for tests.

If future examples require credentials, they must be opt-in and clearly documented as external/manual examples.

Automated tests must not depend on real external services or real API keys.

## CI

CI must not require real secrets for normal linting, formatting, tests, coverage, or package build checks.

CI should run safely for pull requests.

Release publishing may require trusted publishing or release-specific credentials, but those should be configured through GitHub/PyPI security mechanisms and must not be committed.

## Dependency Policy

Runtime dependencies should be minimal.

Do not add security-sensitive dependencies casually.

When adding dependencies that affect transport, auth, cryptography, logging, tracing, or serialization, review:

* maintenance status
* license
* dependency tree
* public API implications
* security implications
* testability

## Reporting Vulnerabilities

Do not report security vulnerabilities through public issues.

Use the process documented in:

```text
SECURITY.md
```

Do not include real secrets, tokens, credentials, private keys, or customer data in public reports.

## Implementation Expectations

When implementing security or redaction functionality:

* keep redaction helpers deterministic
* test sensitive key matching
* test case-insensitive header matching
* test nested payload redaction
* test URL query redaction
* test exception string safety
* test log safety
* avoid global mutable redaction state unless explicitly justified
* make defaults safe
* document opt-in unsafe behavior clearly, if any exists

## Non-Goals

`api-client-kit` is not a credential vault.

It should not store, rotate, encrypt, or manage secrets.

It should help avoid accidental exposure of secrets while building API clients.

Credential storage and secret management belong to dedicated secret-management systems.

## Summary

Security and redaction are core package responsibilities.

The default behavior should be conservative:

```text
safe by default
explicit when advanced behavior is needed
no real secrets in tests
no real secrets in docs
no raw credentials in errors, logs, or hooks
```

When in doubt, redact.
