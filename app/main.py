from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from dotenv import load_dotenv
from structlog.contextvars import bind_contextvars

from .agent import LabAgent
from .incidents import disable, enable, status
from .logging_config import configure_logging, get_logger, write_audit_event
from .metrics import record_error, snapshot
from .middleware import CorrelationIdMiddleware
from .pii import hash_user_id, summarize_text
from .schemas import ChatRequest, ChatResponse
from .tracing import tracing_enabled

load_dotenv()
configure_logging()
log = get_logger()
app = FastAPI(title="Day 13 Observability Lab")
app.add_middleware(CorrelationIdMiddleware)
agent = LabAgent()


@app.on_event("startup")
async def startup() -> None:
    log.info(
        "app_started",
        service=os.getenv("APP_NAME", "day13-observability-lab"),
        env=os.getenv("APP_ENV", "dev"),
        payload={"tracing_enabled": tracing_enabled()},
    )


@app.get("/health")
async def health() -> dict:
    return {"ok": True, "tracing_enabled": tracing_enabled(), "incidents": status()}


@app.get("/metrics")
async def metrics() -> dict:
    return snapshot()


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard() -> str:
    return """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="15">
  <title>Day 13 Observability Dashboard</title>
  <style>
    :root {
      --bg: #f6f3ed;
      --ink: #17201a;
      --muted: #5f6b63;
      --panel: #ffffff;
      --line: #d8d2c6;
      --accent: #0f766e;
      --warn: #b45309;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Aptos", "Segoe UI", sans-serif;
      color: var(--ink);
      background: linear-gradient(135deg, #f6f3ed 0%, #e8efe9 100%);
    }
    main {
      width: min(1120px, calc(100% - 32px));
      margin: 0 auto;
      padding: 28px 0 36px;
    }
    header {
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: end;
      margin-bottom: 22px;
    }
    h1 {
      margin: 0 0 6px;
      font-size: 28px;
      letter-spacing: 0;
    }
    p { margin: 0; color: var(--muted); }
    .grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 14px;
    }
    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      min-height: 148px;
      box-shadow: 0 10px 28px rgba(23, 32, 26, 0.08);
    }
    .label {
      color: var(--muted);
      font-size: 13px;
      text-transform: uppercase;
    }
    .value {
      margin-top: 12px;
      font-size: 30px;
      font-weight: 700;
    }
    .sub {
      margin-top: 10px;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.45;
    }
    .bar {
      height: 8px;
      border-radius: 999px;
      margin-top: 16px;
      background: #e7e2d8;
      overflow: hidden;
    }
    .fill {
      height: 100%;
      width: var(--w);
      background: var(--accent);
    }
    .warn { color: var(--warn); }
    @media (max-width: 760px) {
      header { display: block; }
      .grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>Day 13 Observability Dashboard</h1>
        <p>Layer-2 view, 1h window, auto refresh every 15 seconds.</p>
      </div>
      <p id="updated">Loading metrics...</p>
    </header>
    <section class="grid">
      <article class="panel">
        <div class="label">Latency P50 / P95 / P99</div>
        <div class="value" id="latency">0 / 0 / 0 ms</div>
        <div class="sub">SLO threshold: P95 &lt; 3000 ms</div>
        <div class="bar"><div class="fill" id="latencyBar" style="--w: 0%"></div></div>
      </article>
      <article class="panel">
        <div class="label">Traffic</div>
        <div class="value" id="traffic">0 requests</div>
        <div class="sub">Total successful requests in current process.</div>
      </article>
      <article class="panel">
        <div class="label">Error Rate</div>
        <div class="value" id="errorRate">0%</div>
        <div class="sub" id="errors">Breakdown: none</div>
      </article>
      <article class="panel">
        <div class="label">Cost</div>
        <div class="value" id="cost">$0.0000</div>
        <div class="sub">Daily budget threshold: $2.50</div>
      </article>
      <article class="panel">
        <div class="label">Tokens In / Out</div>
        <div class="value" id="tokens">0 / 0</div>
        <div class="sub">Input and output token totals.</div>
      </article>
      <article class="panel">
        <div class="label">Quality Proxy</div>
        <div class="value" id="quality">0.00</div>
        <div class="sub">Heuristic average target: 0.75+</div>
        <div class="bar"><div class="fill" id="qualityBar" style="--w: 0%"></div></div>
      </article>
    </section>
  </main>
  <script>
    async function refreshMetrics() {
      const res = await fetch('/metrics');
      const data = await res.json();
      document.getElementById('latency').textContent =
        `${data.latency_p50} / ${data.latency_p95} / ${data.latency_p99} ms`;
      document.getElementById('traffic').textContent = `${data.traffic} requests`;
      document.getElementById('errorRate').textContent = `${data.error_rate_pct}%`;
      document.getElementById('errors').textContent =
        `Breakdown: ${Object.keys(data.error_breakdown).length ? JSON.stringify(data.error_breakdown) : 'none'}`;
      document.getElementById('cost').textContent = `$${Number(data.total_cost_usd).toFixed(4)}`;
      document.getElementById('tokens').textContent = `${data.tokens_in_total} / ${data.tokens_out_total}`;
      document.getElementById('quality').textContent = Number(data.quality_avg).toFixed(2);
      document.getElementById('latencyBar').style.setProperty('--w', `${Math.min(data.latency_p95 / 3000 * 100, 100)}%`);
      document.getElementById('qualityBar').style.setProperty('--w', `${Math.min(data.quality_avg * 100, 100)}%`);
      document.getElementById('updated').textContent = `Updated ${new Date().toLocaleTimeString()}`;
    }
    refreshMetrics();
    setInterval(refreshMetrics, 15000);
  </script>
</body>
</html>
"""


@app.post("/chat", response_model=ChatResponse)
async def chat(request: Request, body: ChatRequest) -> ChatResponse:
    bind_contextvars(
        user_id_hash=hash_user_id(body.user_id),
        session_id=body.session_id,
        feature=body.feature,
        model=agent.model,
        env=os.getenv("APP_ENV", "dev"),
    )
    
    log.info(
        "request_received",
        service="api",
        payload={"message_preview": summarize_text(body.message)},
    )
    try:
        result = agent.run(
            user_id=body.user_id,
            feature=body.feature,
            session_id=body.session_id,
            message=body.message,
        )
        log.info(
            "response_sent",
            service="api",
            latency_ms=result.latency_ms,
            tokens_in=result.tokens_in,
            tokens_out=result.tokens_out,
            cost_usd=result.cost_usd,
            payload={"answer_preview": summarize_text(result.answer)},
        )
        write_audit_event(
            "chat_completed",
            correlation_id=request.state.correlation_id,
            session_id=body.session_id,
            feature=body.feature,
            user_id_hash=hash_user_id(body.user_id),
            latency_ms=result.latency_ms,
            cost_usd=result.cost_usd,
            quality_score=result.quality_score,
        )
        return ChatResponse(
            answer=result.answer,
            correlation_id=request.state.correlation_id,
            latency_ms=result.latency_ms,
            tokens_in=result.tokens_in,
            tokens_out=result.tokens_out,
            cost_usd=result.cost_usd,
            quality_score=result.quality_score,
        )
    except Exception as exc:  # pragma: no cover
        error_type = type(exc).__name__
        record_error(error_type)
        log.error(
            "request_failed",
            service="api",
            error_type=error_type,
            payload={"detail": str(exc), "message_preview": summarize_text(body.message)},
        )
        write_audit_event(
            "chat_failed",
            correlation_id=request.state.correlation_id,
            session_id=body.session_id,
            feature=body.feature,
            user_id_hash=hash_user_id(body.user_id),
            error_type=error_type,
        )
        raise HTTPException(status_code=500, detail=error_type) from exc


@app.post("/incidents/{name}/enable")
async def enable_incident(name: str) -> JSONResponse:
    try:
        enable(name)
        log.warning("incident_enabled", service="control", payload={"name": name})
        return JSONResponse({"ok": True, "incidents": status()})
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/incidents/{name}/disable")
async def disable_incident(name: str) -> JSONResponse:
    try:
        disable(name)
        log.warning("incident_disabled", service="control", payload={"name": name})
        return JSONResponse({"ok": True, "incidents": status()})
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
