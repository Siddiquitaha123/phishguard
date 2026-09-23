# PhishGuard

**PhishGuard** is an offline-first phishing-triage web application for analyzing suspicious email text and URLs. It produces an explainable risk score, evidence-based findings, and safe next steps for a human analyst.

![PhishGuard analysis result](docs/screenshots/phishguard-analysis.webp)

> **Safety boundary:** PhishGuard treats URLs as data. It does not visit links, resolve DNS, download files, execute attachments, or send submitted content to external services. It is a triage aid, not a replacement for an analyst.

## Features

- Explainable additive risk score from 0 to 100.
- URL checks for HTTP, IP-address hosts, URL shorteners, suspicious TLDs, excessive subdomains, brand/login wording, and sensitive query parameters.
- Message checks for urgency, credential/payment requests, multiple addresses, and risky attachment references.
- JSON API at `POST /api/analyze`.
- Input validation, request-size limits, output escaping, Content Security Policy, and browser security headers.
- Automated unit/API tests, Docker packaging, GitHub Actions CI, threat model, and test evidence.

## Technology stack

Python 3.12, Flask, Gunicorn, HTML5, CSS3, vanilla JavaScript, pytest, Docker, Git, and GitHub Actions. The analyzer uses Python standard-library modules including `re`, `ipaddress`, `dataclasses`, and `urllib.parse`.

## Run locally

```bash
git clone https://github.com/YOUR_USERNAME/phishguard.git
cd phishguard
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
pytest -q
python -m flask --app app.main run
```

Open <http://127.0.0.1:5000> and click **Load example**, then **Analyze safely**.

Expected test result:

```text
7 passed
```

On Windows PowerShell, use:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
pytest -q
python -m flask --app app.main run
```

## Run with Docker

```bash
docker build -t phishguard .
docker run --rm -p 5000:5000 phishguard
```

Open <http://127.0.0.1:5000>.

## API example

```bash
curl -s http://127.0.0.1:5000/api/analyze \
  -H 'Content-Type: application/json' \
  -d '{"text":"URGENT: verify your password at http://192.0.2.10/login?password=x"}'
```

The response contains `score`, `verdict`, `confidence`, `urls`, `findings`, and `recommendations`.

## Project structure

```text
app/analyzer.py                 Explainable phishing-analysis engine
app/main.py                    Flask routes, validation, and security headers
app/templates/index.html       Web interface
app/static/app.js              Browser interaction and API call
app/static/style.css            Interface styling
tests/test_phishguard.py        Unit and API tests
samples/demo_messages.txt      Safe demonstration inputs
THREAT_MODEL.md                Threats, trust boundaries, and mitigations
docs/TEST_RESULTS.md            Verification evidence
docs/screenshots/               Running-app screenshot
Dockerfile                      Container image definition
.github/workflows/test.yml     CI test workflow
```

## Risk labels

| Score | Label | Meaning |
|---:|---|---|
| 0–29 | Low risk | Few known signals; continue normal verification. |
| 30–59 | Needs review | Investigate and verify through a separate channel. |
| 60–100 | High risk | Do not click, open, or disclose information. |

The score is a prioritization heuristic, not a probability or proof of compromise.

## Security design

The application does not persist submitted messages. It validates JSON type and input length before analysis. It uses safe URL parsing instead of network requests. Findings are escaped before being inserted into the browser DOM. The server adds CSP, clickjacking protection, MIME-sniffing protection, referrer control, and a restrictive permissions policy.

## Resume description

> Built PhishGuard, an explainable offline-first phishing-triage application in Python and Flask. Implemented URL and social-engineering heuristics, secure input validation, CSP and HTTP security headers, structured JSON findings, automated tests, Docker packaging, threat modeling, and GitHub Actions CI.

## License

MIT. See [LICENSE](LICENSE).
