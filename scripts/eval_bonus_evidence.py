from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agent import LabAgent

QUERIES = Path("data/sample_queries.jsonl")


def baseline_prompt(feature: str, docs: list[str], message: str) -> str:
    return f"Feature={feature}\nDocs={docs}\nQuestion={message}"


def estimate_cost(tokens_in: int, tokens_out: int) -> float:
    input_cost = (tokens_in / 1_000_000) * 3
    output_cost = (tokens_out / 1_000_000) * 15
    return round(input_cost + output_cost, 6)


def main() -> None:
    agent = LabAgent()
    lines = [json.loads(line) for line in QUERIES.read_text(encoding="utf-8").splitlines() if line.strip()]

    baseline_input_tokens = 0
    optimized_input_tokens = 0

    for row in lines:
        docs = ["Metrics detect incidents, traces localize them, logs explain root cause."]
        raw_prompt = baseline_prompt(row["feature"], docs, row["message"])
        optimized_prompt = agent._build_prompt(row["feature"], docs, row["message"])
        baseline_input_tokens += max(20, len(raw_prompt) // 4)
        optimized_input_tokens += max(20, len(optimized_prompt) // 4)

    assumed_output_tokens = 120 * len(lines)
    baseline_cost = estimate_cost(baseline_input_tokens, assumed_output_tokens)
    optimized_cost = estimate_cost(optimized_input_tokens, assumed_output_tokens)

    print("--- Bonus Evidence: Cost Optimization ---")
    print(f"Queries analyzed: {len(lines)}")
    print(f"Baseline input tokens: {baseline_input_tokens}")
    print(f"Optimized input tokens: {optimized_input_tokens}")
    print(f"Baseline estimated cost (USD): {baseline_cost}")
    print(f"Optimized estimated cost (USD): {optimized_cost}")
    print(f"Estimated savings (USD): {round(baseline_cost - optimized_cost, 6)}")


if __name__ == "__main__":
    main()
