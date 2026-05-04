"""Run deterministic text evaluation scenarios."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from app.services import SupportAgentRunner
from evals.metrics import (
    forbidden_phrase_violation,
    phrase_coverage,
    routing_correct,
    scenario_passed,
    summarize_results,
    tool_recall,
)


def load_scenarios(path: str | Path = "evals/eval_scenarios.json") -> list[dict]:
    """Load evaluation scenarios from JSON."""

    return json.loads(Path(path).read_text(encoding="utf-8"))


def evaluate_scenario(scenario: dict, runner: SupportAgentRunner | None = None) -> dict:
    """Evaluate a single scenario."""

    active_runner = runner or SupportAgentRunner()
    response = active_runner.run(scenario["user_message"])
    actual_tools = [tool_call["name"] for tool_call in response.tool_calls]

    result = {
        "id": scenario["id"],
        "user_message": scenario["user_message"],
        "expected_intent": scenario["expected_intent"],
        "actual_intent": response.intent,
        "intent_correct": scenario["expected_intent"] == response.intent,
        "expected_agent": scenario["expected_agent"],
        "actual_agent": response.selected_agent,
        "routing_correct": routing_correct(scenario["expected_agent"], response.selected_agent),
        "expected_tools": scenario["expected_tools"],
        "actual_tools": actual_tools,
        "tool_recall": tool_recall(scenario["expected_tools"], actual_tools),
        "required_phrase_coverage": phrase_coverage(scenario.get("must_include", []), response.final_response),
        "forbidden_phrase_violation": forbidden_phrase_violation(scenario.get("must_not_include", []), response.final_response),
        "latency_ms": response.latency_ms,
        "max_latency_ms": scenario["max_latency_ms"],
        "final_response": response.final_response,
        "raw_events": response.raw_events,
    }
    result["passed"] = scenario_passed(result)
    return result


def run_eval(scenario_path: str | Path = "evals/eval_scenarios.json") -> dict:
    """Run all scenarios and save a report."""

    scenarios = load_scenarios(scenario_path)
    results = [evaluate_scenario(scenario) for scenario in scenarios]
    summary = summarize_results(results)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "results": results,
    }

    report_dir = Path("evals/reports")
    report_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    report_path = report_dir / f"eval_report_{timestamp}.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    report["report_path"] = str(report_path)
    return report


def main() -> None:
    """CLI entrypoint for text evaluation."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--scenarios", default="evals/eval_scenarios.json")
    args = parser.parse_args()
    report = run_eval(args.scenarios)
    summary = report["summary"]

    print("Running evaluation scenarios...")
    for result in report["results"]:
        status = "PASS" if result["passed"] else "FAIL"
        print(f"[{status}] {result['id']} - agent={result['actual_agent']} latency={result['latency_ms']}ms")

    print("\nSummary:")
    print(f"Total: {summary['total']} | Passed: {summary['passed']} | Failed: {summary['failed']}")
    print(f"Routing accuracy: {summary['routing_accuracy']:.0%}")
    print(f"Intent accuracy: {summary['intent_accuracy']:.0%}")
    print(f"Tool recall: {summary['average_tool_recall']:.0%}")
    print(f"Avg latency: {summary['average_latency_ms']:.1f}ms")
    print(f"Report saved to: {report['report_path']}")


if __name__ == "__main__":
    main()

