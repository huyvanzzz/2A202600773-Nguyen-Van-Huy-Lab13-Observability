# Evidence Checklist - Personal Observability Lab

Use this checklist right before submission/demo.

## Required Screenshots

- Langfuse trace list showing at least 10 traces
- One Langfuse trace waterfall
- `data/logs.jsonl` showing `correlation_id`
- `data/logs.jsonl` showing PII redaction, for example `[REDACTED_EMAIL]` or `[REDACTED_CREDIT_CARD]`
- Local dashboard at `http://127.0.0.1:8013/dashboard` with 6 panels
- `config/alert_rules.yaml` showing 3 alerts with runbook links
- `docs/alerts.md` showing matching runbook sections

## Commands To Reproduce Evidence

```powershell
python -m pytest
python -m uvicorn app.main:app --host 127.0.0.1 --port 8013
```

In another terminal:

```powershell
$env:BASE_URL='http://127.0.0.1:8013'
python scripts\load_test.py --concurrency 5
python scripts\validate_logs.py
```

Incident evidence:

```powershell
$env:BASE_URL='http://127.0.0.1:8013'
python scripts\inject_incident.py --scenario rag_slow
python scripts\load_test.py --concurrency 5
python scripts\inject_incident.py --scenario rag_slow --disable
```

## Final Checks

- `python -m pytest` passes
- `python scripts\validate_logs.py` reports `Estimated Score: 100/100`
- `/health` returns `tracing_enabled: true`
- `/metrics` has `traffic > 0`
- `/dashboard` opens successfully
- `.env` is not committed
