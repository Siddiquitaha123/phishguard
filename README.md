# PhishGuard

**PhishGuard** is an explainable phishing-triage assistant for security analysts and security-awareness teams. It accepts suspicious email text or URLs and returns a bounded risk score, the exact signals that contributed to the score, and safe next steps.

This project models a real SOC problem: an analyst often needs a fast first-pass decision before escalating a message to a mail-security platform or incident-response workflow. PhishGuard is intentionally **offline-first**. It never visits a URL, downloads a file, or sends submitted content to a third party.

> **Important limitation:** this is a triage aid, not a verdict engine. A low score does not prove that a message is safe, and a high score is not proof of compromise. A human must verify context, sender authentication, headers, and organizational policy.

## Why this is a strong intermediate cybersecurity project

The project demonstrates more than a regex demo. It combines a threat-modelled web application, explainable detection logic, secure parsing, API validation, security headers, automated tests, Docker packaging, CI, and analyst-oriented documentation. The design is small enough to understand completely while still reflecting a real security workflow.

## Capabilities

- Extracts URLs without making network requests.
- Detects IP-address hosts, HTTP links, URL shorteners, suspicious top-level domains, excessive subdomains, brand/login wording, and sensitive redirect parameters.
- Detects urgency, credential/payment requests, and risky attachment references in message text.
- Produces evidence for every score contribution.
- Enforces input limits and rejects malformed API requests.
- Uses a restrictive Content Security Policy and other browser security headers.
- Includes unit tests, API tests, sample messages, Docker packaging, and GitHub Actions CI.

## Quick start

```bash
git clone https://github.com/YOUR_USERNAME/phishguard.git
cd phishguard
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
flask --app app.main run --debug
```

Open <http://127.0.0.1:5000>. Paste a message from `samples/demo_messages.txt`, then click **Analyze safely**.

For a production-like local run:

```bash
gunicorn --bind 127.0.0.1:5000 app.main:app
```

With Docker:

```bash
docker build -t phishguard .
docker run --rm -p 5000:5000 phishguard
```

## API example

```bash
curl -s http://127.0.0.1:5000/api/analyze \
  -H 'Content-Type: application/json' \
  -d '{"text":"URGENT: verify your password at http://192.0.2.10/login?password=x"}' | python3 -m json.tool
```

The API returns `score`, `verdict`, `confidence`, extracted `urls`, structured `findings`, and `recommendations`. Each finding has a stable code, severity, explanation, and points. This makes the output reviewable and suitable for later integration with a case-management system.

## How the scoring works

The analyzer is a transparent additive heuristic. Each signal contributes a small number of points, and the total is capped at 100.

| Score | Label | Meaning |
|---:|---|---|
| 0–29 | Low risk | Few known signals; continue normal verification. |
| 30–59 | Needs review | Some signals are present; escalate or verify out of band. |
| 60–100 | High risk | Multiple strong signals; do not click, open, or disclose information. |

The score is not a probability. For example, an IP-address URL and an urgent password request are independent pieces of evidence that should be reviewed together. In a future production system, this layer could be combined with sender-authentication results, URL reputation, sandbox verdicts, and analyst feedback.

## Architecture

```text
Browser
  │ POST /api/analyze {text}
  ▼
Flask validation layer
  │ type, empty input, size limit
  ▼
Offline analyzer
  ├─ URL extraction and parsing
  ├─ URL signals
  ├─ message-language signals
  └─ explainable score + recommendations
  ▼
JSON response or rendered result panel
```

The analyzer is kept separate from Flask so it can be tested independently or reused by a CLI, a queue worker, or a future mail-ingestion adapter. The application does not persist submitted messages, which reduces accidental handling of sensitive content.

## Project map

| Path | Purpose |
|---|---|
| `app/analyzer.py` | Pure Python detection and scoring engine. |
| `app/main.py` | Flask routes, validation, and security headers. |
| `app/templates/index.html` | Minimal analyst interface. |
| `app/static/style.css` | Accessible dark interface styling. |
| `tests/test_phishguard.py` | Unit, API, validation, and header tests. |
| `samples/demo_messages.txt` | Safe test inputs using reserved IP space. |
| `THREAT_MODEL.md` | Assets, trust boundaries, threats, and mitigations. |
| `LEARNING_GUIDE.md` | Beginner-friendly study plan and interview demonstration guide. |
| `.github/workflows/test.yml` | Continuous integration. |

## Security decisions

PhishGuard does not use `requests`, a browser automation library, or a URL resolver. That is deliberate: automatically visiting an attacker-controlled URL would create server-side request forgery, malware, and privacy risks. The interface escapes findings before placing them into the DOM, while the server sets a restrictive policy as defense in depth. The input limit prevents oversized requests from consuming unbounded memory.

The sample uses RFC 5737 documentation IP addresses rather than live infrastructure. Do not paste passwords, tokens, private email, or confidential incident data into an untrusted deployment.

## How to understand it completely

Start with `tests/test_phishguard.py`. Each test states a behavior the system promises. Then read `analyze()` in `app/analyzer.py` and follow one test into the corresponding finding. Finally, inspect `api_analyze()` in `app/main.py` to see how untrusted input is validated before reaching the analyzer.

To extend the project, add one signal at a time and pair it with a test. Good next steps are parsing `Authentication-Results` headers, adding analyst feedback with a local SQLite database, creating a CLI that reads `.eml` files without opening attachments, and measuring precision/recall on a labeled, privacy-safe dataset.

## Resume-ready description

> Built PhishGuard, an explainable offline-first phishing triage web application in Python and Flask. Implemented transparent URL and social-engineering heuristics, bounded input validation, CSP and browser security headers, structured JSON findings, Docker packaging, and automated CI with unit/API tests.

## Responsible-use boundary

Use this project only for defensive analysis of messages you are authorized to inspect. Do not use it to probe third-party infrastructure, collect credentials, or automatically visit suspicious links. The tool is designed to help a defender decide what to investigate next.

## License

MIT. See `LICENSE`.
