# Bonus Evidence

## 1. Cost Optimization

Command used:

```powershell
python scripts\eval_bonus_evidence.py
```

Observed result:

```text
Queries analyzed: 10
Baseline input tokens: 371
Optimized input tokens: 321
Baseline estimated cost (USD): 0.019113
Optimized estimated cost (USD): 0.018963
Estimated savings (USD): 0.00015
```

Summary:

- Prompt construction was shortened to reduce input token usage.
- The optimized version reduced estimated input tokens from `371` to `321`.
- Estimated total cost decreased from `$0.019113` to `$0.018963`.

## 2. Audit Logs

Audit log file:

- `data/audit.jsonl`

Example fields recorded:

- `ts`
- `event`
- `correlation_id`
- `session_id`
- `feature`
- `user_id_hash`
- `latency_ms`
- `cost_usd`
- `quality_score`

Summary:

- Audit events are written separately from application logs.
- This provides a cleaner trail for operational review without mixing audit entries into the main JSON log stream.

## 3. Custom Metric / Dashboard Support

Implemented additions:

- `error_rate_pct` in `/metrics`
- local `/dashboard` endpoint visualizing the 6 required panels

Summary:

- The dashboard makes it easier to validate the required observability panels quickly during demo and grading.
