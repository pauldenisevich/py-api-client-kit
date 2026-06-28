# Security Policy

Security is a core concern for `api-client-kit`.

This package is intended to help developers build API clients that handle credentials, tokens, headers, request payloads, response payloads, and error context safely.

## Supported Versions

The project is currently in early development.

No stable public release is available yet.

| Version  | Supported             |
| -------- | --------------------- |
| `0.1.x`  | Planned               |
| `<0.1.0` | No production support |

## Reporting a Vulnerability

Please do not report security vulnerabilities through public issues.

Once the repository is public, use GitHub Security Advisories if available.

Until a public security process is finalized, contact the maintainer privately.

Do not include secrets, credentials, tokens, private keys, or sensitive customer data in public reports, issues, pull requests, examples, screenshots, or logs.

## Sensitive Information

Never commit or disclose:

* API keys
* bearer tokens
* refresh tokens
* passwords
* cookies
* private SSH keys
* GitHub tokens
* PyPI tokens
* `.env` files
* customer data
* sensitive request or response payloads

## Redaction Policy

`api-client-kit` treats redaction as a first-class concern.

Errors, logs, hooks, diagnostics, and examples should avoid leaking:

* `Authorization` headers
* cookies
* API keys
* tokens
* passwords
* secrets in query parameters
* sensitive body fields

Redaction behavior will be implemented and tested as part of the package runtime.

## Test Policy

Tests must not call real external APIs.

Tests must not require real secrets.

HTTP behavior should be tested with local test doubles such as `httpx.MockTransport`.

## Disclosure Timeline

This project is not yet in a stable public release phase.

A more formal disclosure process will be added before the first stable public release.
