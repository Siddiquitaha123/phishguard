# PhishGuard learning and demonstration guide

This guide is for learning the project from the ground up. You do not need advanced Python, Flask, JavaScript, Docker, or machine learning knowledge to understand the current version. The project is intentionally small and uses mostly Python standard-library features.

## 1. What the project does

PhishGuard accepts suspicious email text or a URL. It checks the input for recognizable phishing signals. It adds points for those signals, assigns a risk label, and explains the evidence to the analyst.

The complete flow is:

```text
User pastes message
        |
        v
Browser sends JSON to Flask API
        |
        v
Flask validates the input
        |
        v
Python analyzer extracts URLs and checks signals
        |
        v
Python returns score, verdict, findings, and recommendations
        |
        v
Browser displays the result
```

The application does not visit the supplied URL. That is an important security decision because automatically visiting attacker-controlled URLs could create server-side request forgery, malware, and privacy risks.

## 2. How much Python is used?

Python is the main language in this project. Almost all security functionality is written in Python.

| Python area | Where it is used |
|---|---|
| Strings and text processing | Normalizing the message and searching for suspicious words |
| Lists and sets | Storing URLs, findings, terms, and scoring codes |
| Regular expressions | Extracting URLs, email addresses, and risky attachment names |
| Functions | Separating URL extraction, analysis, and recommendations |
| Classes | `Finding` and `Analysis` data structures |
| Type hints | Explaining expected input and return values |
| Exceptions | Safely checking whether a hostname is an IP address |
| URL parsing | Reading schemes, hosts, paths, and query parameters |
| JSON | Receiving API input and returning analysis results |
| HTTP handling | Flask routes and responses |
| Testing | Verifying normal and invalid behavior with pytest |

The project does **not** require advanced Python topics such as metaclasses, decorators that you write yourself, asynchronous programming, multiprocessing, deep inheritance, or complex algorithms.

## 3. Python libraries used

### Python standard library

These libraries come with Python. You do not install them separately:

- `dataclasses`: creates simple structured objects for findings and analysis results.
- `html`: decodes HTML entities such as `&amp;`.
- `ipaddress`: checks whether a hostname is an IP address.
- `re`: searches text with regular expressions.
- `typing`: documents expected types.
- `urllib.parse`: safely separates a URL into its scheme, host, path, and query string.

### External packages

Only three runtime/development packages are used:

- **Flask:** creates the web application and API routes.
- **Gunicorn:** runs the Flask application using a production-style server.
- **pytest:** runs automated tests.

The project does not use NumPy, Pandas, scikit-learn, SQLAlchemy, or other advanced data libraries.

## 4. Learn the files in this order

### Step 1: Read the tests

Open `tests/test_phishguard.py`. Tests are the easiest way to understand expected behavior.

For example:

```python
def test_high_risk_message_is_explainable():
    result = analyze("URGENT: verify your password immediately at http://192.0.2.10/login?password=x")
    assert result.verdict == "High risk"
    assert result.score >= 60
```

This says that a message containing urgency, a password request, an IP address, and an HTTP login URL should produce a high-risk result.

Important Python concepts here are:

- `def`: defines a function.
- `result = ...`: stores a returned value.
- `assert`: checks that an expectation is true.
- `fixture`: creates reusable test setup.

### Step 2: Read `extract_urls()`

This function searches the input for URL-like text. It removes trailing punctuation and converts `www.example.com` into `http://www.example.com` so it can be parsed consistently.

Important concepts:

- A function receives an argument.
- A list stores multiple values.
- A `for` loop processes each match.
- `if` statements apply conditions.
- `.lower()` makes comparison case-insensitive.

### Step 3: Read `analyze()`

This is the main security function. It follows this pattern:

```text
clean input
   |
extract URLs
   |
check URL signals
   |
check message-language signals
   |
add points
   |
choose verdict
   |
create recommendations
```

The nested helper function `add()` creates a `Finding` object and appends it to the findings list. It prevents the scoring logic from repeatedly writing the same object-construction code.

### Step 4: Read `app/main.py`

This file connects the Python analyzer to the web.

The important route is:

```python
@app.post("/api/analyze")
def api_analyze():
```

It means: when the browser sends a `POST` request to `/api/analyze`, run this function.

The route performs these checks:

1. Is the request JSON?
2. Is the JSON an object?
3. Does it contain a string named `text`?
4. Is the text non-empty?
5. Is it below the maximum length?
6. If valid, call `analyze(text)`.
7. Return the result as JSON.

This is where web input becomes Python input.

### Step 5: Read the HTML and JavaScript last

The HTML creates the text area and buttons. The JavaScript sends the text to the Flask API and displays the response. You only need to understand the basic request flow; you do not need advanced frontend knowledge.

## 5. Flask explained simply

Flask is a Python web framework. It lets Python respond to browser requests.

This code creates an application:

```python
from flask import Flask
app = Flask(__name__)
```

This code creates a page route:

```python
@app.get("/")
def index():
    return render_template("index.html")
```

When someone visits `/`, Flask runs `index()` and returns the HTML page.

This code creates an API route:

```python
@app.post("/api/analyze")
def api_analyze():
    payload = request.get_json()
    return jsonify(analyze(payload["text"]).to_dict())
```

When the browser sends JSON to `/api/analyze`, Flask reads the JSON, passes the message to the Python analyzer, and returns a JSON result.

The only Flask concepts you need for an initial interview are:

- Application object
- Routes
- GET requests for pages
- POST requests for submitted data
- JSON requests and responses
- Templates
- Request validation
- Response headers

## 6. What to learn from tutorials

Do not try to learn all of Flask before studying the project. Learn these topics in order:

1. Python functions, lists, dictionaries, sets, loops, and exceptions.
2. Python modules and imports.
3. HTTP basics: URL, method, status code, headers, and JSON.
4. Flask application creation and routes.
5. Flask request handling and JSON responses.
6. HTML forms and DOM elements.
7. JavaScript `fetch()` at a basic level.
8. pytest basics.
9. Docker images and containers at a conceptual level.

A good stopping point is when you can explain the request flow without copying an explanation.

## 7. Local setup and commands

From the project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the tests:

```bash
pytest -q
```

Start the development server:

```bash
flask --app app.main run --debug
```

Open `http://127.0.0.1:5000`.

Run the production-style local server:

```bash
gunicorn --bind 127.0.0.1:5000 app.main:app
```

## 8. Five-minute interview demonstration

### Opening explanation

Say:

> PhishGuard is an offline-first phishing-triage tool. A user pastes suspicious email text or a URL. The Flask API validates the input, the Python analyzer checks explainable phishing signals, and the browser displays a risk score with evidence and recommendations. The application never visits the submitted URL.

### Demonstration

1. Open the application.
2. Click **Load example**.
3. Explain that the example uses a documentation IP address and is not a real malicious website.
4. Click **Analyze safely**.
5. Point out the score and each finding.
6. Explain that the IP address, HTTP scheme, urgency, and password request contribute points.
7. Paste a normal sentence and analyze it.
8. Show that it receives a lower risk result.
9. Open the test file and run `pytest -q`.
10. Explain that the tests verify both detection behavior and secure API behavior.

### Closing explanation

Say:

> The current version is a transparent heuristic triage layer, not a complete email-security platform. A production extension could add authenticated case storage, sender-authentication header analysis, reputation enrichment in an isolated worker, and analyst feedback. I would evaluate those additions with precision, recall, and false-positive measurements.

## 9. Questions you may be asked

### Why did you choose heuristics instead of machine learning?

> I wanted the first version to be explainable and easy to validate. A security analyst can see exactly why a message received points. Machine learning could be added later and compared against the heuristic baseline using a labeled, privacy-safe dataset.

### Why do you not visit URLs?

> Visiting attacker-controlled URLs from the server could create SSRF, malware, and privacy risks. The first-pass tool treats URLs as data and leaves detonation or reputation checks to an isolated security service.

### Is the score a probability?

> No. It is a capped additive risk score. It prioritizes review; it does not prove that a message is malicious or safe.

### What happens when invalid data is sent?

> The API rejects non-JSON requests, missing or non-string `text` fields, empty text, and oversized input. It returns an appropriate HTTP error rather than passing invalid input to the analyzer.

### What security controls did you add?

> I added input-size limits, strict content-type validation, safe URL parsing, output escaping, a Content Security Policy, clickjacking protection, MIME sniffing protection, and a no-network design for submitted URLs.

### What part did you write in Python?

> The analyzer, URL extraction, scoring model, recommendations, Flask API, validation logic, security headers, and automated tests are all Python. The frontend is a small HTML/CSS/JavaScript interface that calls the Python API.

### Do you know Flask deeply?

> I understand the Flask concepts used in this project: application creation, routes, GET and POST requests, JSON validation, templates, and responses. I am continuing to deepen my Flask knowledge, but I can trace and explain the complete request flow in this application.

### Do you know Docker deeply?

> Docker is included as a reproducible packaging option. The Dockerfile installs the pinned Python dependencies, copies the application, exposes port 5000, and starts Gunicorn. My primary focus in this project is the Python security logic and Flask API.

## 10. What to claim on your resume

Use a technology list that reflects what you understand:

> **Technologies:** Python, Flask, HTML, CSS, REST API, pytest, Git/GitHub, networking, and web-security concepts.

You may mention JavaScript and Docker as supporting technologies only if you are comfortable explaining their basic role:

> **Supporting tools:** Vanilla JavaScript frontend and Docker deployment configuration.

Do not claim advanced Flask, JavaScript, Docker, machine learning, SQL, or SIEM expertise based only on this project.

## 11. Two-week study plan

### Days 1–2: Python foundations

Practice functions, lists, dictionaries, sets, loops, conditions, exceptions, and imports. Reproduce `extract_urls()` in a small separate file.

### Days 3–4: URL and text analysis

Read `urllib.parse`, `ipaddress`, and regular-expression examples. Add one harmless test signal and make it pass.

### Days 5–6: Flask basics

Learn routes, request methods, JSON requests, JSON responses, templates, and status codes. Trace a request from the browser to `api_analyze()`.

### Days 7–8: Security concepts

Study input validation, XSS, SSRF, clickjacking, MIME sniffing, Content Security Policy, and why the application does not fetch URLs.

### Days 9–10: Testing

Read every test and intentionally break one condition. Run the tests, observe the failure, fix the implementation, and run them again.

### Days 11–12: Frontend and deployment basics

Learn what `fetch()` does and understand the Dockerfile line by line. You do not need advanced JavaScript or Kubernetes.

### Days 13–14: Demonstration practice

Give the five-minute demonstration without reading notes. Then answer the interview questions aloud.

## 12. The minimum understanding standard

You are ready to show the project when you can explain these five points clearly:

1. The user submits text through the browser.
2. Flask receives and validates JSON.
3. The Python analyzer extracts URLs and checks phishing signals.
4. The score is explainable and is not a probability.
5. The application avoids visiting URLs because that would create security risk.

You do not need to memorize every line. You need to understand the data flow, the main security decisions, and the limits of the tool.
