from app.metrics import ERRORS, TRAFFIC, percentile, record_error, snapshot


def test_percentile_basic() -> None:
    assert percentile([100, 200, 300, 400], 50) >= 100


def test_snapshot_includes_error_rate() -> None:
    original_traffic = TRAFFIC
    original_errors = ERRORS.copy()
    try:
        import app.metrics as metrics

        metrics.TRAFFIC = 4
        metrics.ERRORS.clear()
        record_error("RuntimeError")

        data = snapshot()

        assert data["error_rate_pct"] == 20.0
        assert data["error_breakdown"] == {"RuntimeError": 1}
    finally:
        import app.metrics as metrics

        metrics.TRAFFIC = original_traffic
        metrics.ERRORS.clear()
        metrics.ERRORS.update(original_errors)
