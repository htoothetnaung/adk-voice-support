"""Run voice evaluation in live-api simulation, pipeline simulation, or both."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from app.services import SupportAgentRunner
from app.voice import LiveApiSession, VoicePipelineRunner
from evals.voice_metrics import evaluate_voice_result, summarize_voice_results


def load_voice_scenarios(path: str | Path = "evals/eval_scenarios_voice.json") -> list[dict]:
    """Load voice scenarios."""

    return json.loads(Path(path).read_text(encoding="utf-8"))


def _support_response_for(transcript: str) -> dict:
    return SupportAgentRunner().run(transcript).to_dict()


def evaluate_voice_scenario(scenario: dict, approach: str) -> dict:
    """Evaluate one scenario for one approach."""

    if approach == "live_api":
        response = LiveApiSession().run_transcript_turn(scenario["transcript"], scenario.get("simulate_interrupt", False))
    elif approach == "pipeline":
        response = VoicePipelineRunner().run_transcript_turn(scenario["transcript"], scenario.get("simulate_interrupt", False))
    else:
        raise ValueError(f"Unsupported voice approach: {approach}")
    support_response = _support_response_for(response.transcript)
    return evaluate_voice_result(scenario, response, support_response, approach)


def run_voice_eval(approach: str = "both", scenario_path: str | Path = "evals/eval_scenarios_voice.json") -> dict:
    """Run voice evals and save a report."""

    approaches = ["live_api", "pipeline"] if approach == "both" else [approach]
    scenarios = load_voice_scenarios(scenario_path)
    results = [
        evaluate_voice_scenario(scenario, selected_approach)
        for selected_approach in approaches
        for scenario in scenarios
    ]

    summaries = {
        selected_approach: summarize_voice_results([result for result in results if result["approach"] == selected_approach])
        for selected_approach in approaches
    }
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "approach": approach,
        "summaries": summaries,
        "results": results,
    }

    report_dir = Path("evals/reports")
    report_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    report_path = report_dir / f"voice_eval_report_{timestamp}.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    report["report_path"] = str(report_path)
    return report


def main() -> None:
    """CLI entrypoint for voice evaluation."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--approach", choices=["live_api", "pipeline", "both"], default="both")
    parser.add_argument("--compare", action="store_true")
    parser.add_argument("--scenarios", default="evals/eval_scenarios_voice.json")
    args = parser.parse_args()

    report = run_voice_eval(args.approach, args.scenarios)
    print("Running voice evaluation scenarios...")
    for result in report["results"]:
        status = "PASS" if result["passed"] else "FAIL"
        print(f"[{status}] {result['approach']}:{result['id']} - latency={result['latency_ms']}ms")

    print("\nSummary:")
    for approach, summary in report["summaries"].items():
        print(
            f"{approach}: Total={summary['total']} Passed={summary['passed']} Failed={summary['failed']} "
            f"Intent={summary['intent_accuracy']:.0%} Avg latency={summary['average_latency_ms']:.1f}ms"
        )

    if args.compare and len(report["summaries"]) > 1:
        live = report["summaries"]["live_api"]
        pipeline = report["summaries"]["pipeline"]
        winner = "live_api" if live["average_latency_ms"] <= pipeline["average_latency_ms"] else "pipeline"
        print(f"\nComparison winner by latency: {winner}")

    print(f"Report saved to: {report['report_path']}")


if __name__ == "__main__":
    main()

