# PhishGuard threat model

## Scope and security objective

PhishGuard is a local triage tool. Its primary security objective is to help an authorized analyst review suspicious content without causing a network interaction or executing an attachment. The application should preserve the analyst's control over the next action and make its reasoning inspectable.

## Assets

The main assets are the analyst's submitted message text, the integrity of the analysis result, the analyst's browser session, and the host running the application. Message text may contain personal data, internal addresses, or secrets, so the default design avoids persistence and external transmission.

## Trust boundaries

1. **Browser to Flask API:** the browser can send arbitrary input. The server must validate type, size, and content format.
2. **Flask API to analyzer:** the analyzer receives untrusted text and must not treat text as executable code or as a command.
3. **Analyzer to the network:** there is intentionally no network boundary crossing. URL strings remain data.
4. **Container to host:** the container is a deployment convenience, not a complete isolation guarantee. Operators must still apply least privilege and platform hardening.

## Threats and mitigations

| Threat | Example | Mitigation in this project | Residual risk |
|---|---|---|---|
| Server-side request forgery | The analyzer follows an attacker URL | No URL fetching or DNS resolution exists | A future enrichment feature could reintroduce this risk. Isolate it in a dedicated worker. |
| Cross-site scripting | A crafted finding is inserted into the results panel | Client-side `escapeHtml`, restrictive CSP, and no unsafe HTML rendering | Review any future template or JavaScript changes. |
| Denial of service | Very large request body | Flask request limit and explicit analyzer input cap | Rate limiting is still needed for public deployments. |
| Data leakage | Private email is logged or stored | No database and no application logging of submitted text | Reverse proxies and hosting platforms may log requests. Configure them deliberately. |
| Misleading verdict | A benign message receives a low score | Explainable findings, confidence label, and explicit human-review language | Heuristics cannot detect every phish; evaluate on a labeled dataset before operational use. |
| Malicious attachment execution | Analyst opens an attachment from a message | This tool never opens attachments and recommends sandboxing | The analyst's surrounding workflow must enforce safe handling. |
| Clickjacking | The app is embedded in a hostile page | `X-Frame-Options: DENY` and CSP | Browser and proxy configuration should be checked in deployment. |
| Sensitive browser capabilities | A compromised page requests sensors | `Permissions-Policy` disables camera, microphone, and location | This is not a substitute for browser isolation. |

## Abuse cases not supported

PhishGuard does not send phishing emails, generate credential-harvesting pages, brute-force accounts, scan hosts, or validate stolen credentials. It is a static triage aid and should remain separated from offensive automation.

## Deployment checklist

For a public deployment, place the app behind TLS and a reverse proxy, require authentication, add rate limiting, disable debug mode, avoid request-body logging, run as a non-root user, pin and regularly review dependencies, and define a retention policy. If URL reputation or detonation is added, put that capability in a separate network-restricted service with strict egress controls and an explicit user consent model.
