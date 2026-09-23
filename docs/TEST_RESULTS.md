# Verification results

PhishGuard was verified locally with Python 3.12, Flask, Gunicorn, and pytest.

## Automated tests

Command:

```bash
pytest -q
```

Result:

```text
.......                                                                  [100%]
7 passed in 0.23s
```

The tests cover URL extraction, high-risk detection, low-risk text, invalid content type, empty input, maximum input length, JSON response structure, and security headers.

## HTTP smoke test

The homepage returned HTTP 200 and loaded the external JavaScript asset at `/static/app.js`. The API accepted JSON at `POST /api/analyze` and returned a high-risk result for the safe demonstration input:

```text
URGENT: Your Microsoft 365 password expires today. Verify immediately at http://192.0.2.10/login?password=reset
```

Observed result:

```text
Risk score: 86/100
Verdict: High risk
Confidence: High
```

The `192.0.2.0/24` address range is reserved for documentation examples, so the sample does not target a real website.

## Browser evidence

The screenshot in `docs/screenshots/phishguard-analysis.webp` was captured from the running application after loading the sample and selecting **Analyze safely**. It shows the populated message, the 86/100 risk score, findings, and analyst recommendations.
