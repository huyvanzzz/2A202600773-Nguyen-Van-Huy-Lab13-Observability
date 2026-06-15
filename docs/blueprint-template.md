# Day 13 Observability Lab Report - Individual Submission

> Replace only the placeholders for your name, student ID, repo URL, and commit evidence link.

## 1. Student Information

- Student name: `Nguyễn Văn Huy`
- MSSV: 2A202600773
- Repo URL: `https://github.com/huyvanzzz/2A202600773-Nguyen-Van-Huy-Lab13-Observability`

---

## 2. Auto-Verified Results

- Validate logs final score: `100/100`
- Total traces count: `22+`
- PII leaks found: `0`

---

## 3. Technical Evidence

### 3.1 Logging and Tracing

- Correlation ID screenshot: `evidence/correlation_id.png`
- PII redaction screenshot: `evidence/PII.png`
- Trace list screenshot: `evidence/langfuse.png`
- Trace waterfall screenshot: `evidence/waterfall.png`
- Trace waterfall explanation:
  The trace shows the `run` observation with tagged context such as `lab`, `qa` or `summary`, and the model name. It also contains output metrics including latency, tokens, cost, and quality score. This makes it possible to debug from trace detail back to metrics and logs.

### 3.2 Dashboard and SLOs

- Dashboard 6 panels screenshot: `evidence/dashboard.png`

| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | 2651ms observed |
| Error Rate | < 2% | 28d | 0.0% observed |
| Cost Budget | < $2.5/day | 1d | $0.0632 observed |

### 3.3 Alerts and Runbook

- Alert rules screenshot: `evidence/alerts.png`
- Sample runbook link: `docs/alerts.md#1-high-latency-p95`

---

## 4. Incident Response

- Scenario name: `rag_slow`
- Symptoms observed:
  Request latency increased significantly during concurrent load. Client-side request durations moved from sub-second responses to multi-second responses, and the dashboard reflected elevated tail latency.
- Root cause proved by:
  Metrics showed P95 latency rising to `2651ms`, Langfuse trace detail showed a slow `run` observation with high latency, and application logs preserved correlation IDs for request-by-request inspection. The injected incident state also confirmed `rag_slow=true` during testing.
- Fix action:
  Disable the incident with `python scripts\inject_incident.py --scenario rag_slow --disable`, then rerun load generation to confirm recovery.
- Preventive measure:
  Keep the `high_latency_p95` alert enabled, use the linked runbook in `docs/alerts.md`, and inspect trace detail plus logs together whenever latency rises above SLO.

---

## 5. Personal Work Summary

- Tasks completed:
  I implemented correlation ID propagation, structured JSON logging, PII scrubbing, Langfuse tracing integration, dashboard metrics, alert verification, incident testing, and evidence collection.
- Evidence link:
  [`https://github.com/huyvanzzz/2A202600773-Nguyen-Van-Huy-Lab13-Observability`](https://github.com/VinUni-AI20k/Lab13-Observability/compare/main...huyvanzzz:2A202600773-Nguyen-Van-Huy-Lab13-Observability:main)
- Self-explanation readiness:
  I can explain the middleware flow, logging pipeline, PII scrubbing approach, trace verification steps, dashboard metrics, and incident root-cause analysis.

---

## 6. Bonus Items (Optional)

- Cost optimization:
  Claimed. Prompt construction was shortened to reduce input token usage. Bonus evidence is documented in `docs/bonus-evidence.md`, showing estimated input tokens reduced from `371` to `321` and estimated cost reduced from `$0.019113` to `$0.018963`.
- Audit logs:
  Claimed. Separate audit entries are written to `data/audit.jsonl` with fields including `correlation_id`, `session_id`, `feature`, `latency_ms`, `cost_usd`, and `quality_score`.
- Custom metric:
  Claimed. Added `error_rate_pct` to `/metrics` and a lightweight local dashboard endpoint that visualizes the six required panels directly from exported metrics for easier validation and demo.
