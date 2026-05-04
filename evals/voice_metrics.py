"""Voice evaluation metrics."""

from __future__ import annotations

from evals.metrics import forbidden_phrase_violation, phrase_coverage, routing_correct, tool_recall


def word_error_rate(reference: str, hypothesis: str) -> float:
    """Compute simple Levenshtein word error rate."""

    ref_words = reference.lower().split()
    hyp_words = hypothesis.lower().split()
    if not ref_words:
        return 0.0 if not hyp_words else 1.0

    distances = [[0] * (len(hyp_words) + 1) for _ in range(len(ref_words) + 1)]
    for i in range(len(ref_words) + 1):
        distances[i][0] = i
    for j in range(len(hyp_words) + 1):
        distances[0][j] = j

    for i, ref_word in enumerate(ref_words, start=1):
        for j, hyp_word in enumerate(hyp_words, start=1):
            substitution_cost = 0 if ref_word == hyp_word else 1
            distances[i][j] = min(
                distances[i - 1][j] + 1,
                distances[i][j - 1] + 1,
                distances[i - 1][j - 1] + substitution_cost,
            )
    return distances[-1][-1] / len(ref_words)


def evaluate_voice_result(scenario: dict, response, support_response: dict, approach: str) -> dict:
    """Evaluate one voice result."""

    actual_tools = [tool_call["name"] for tool_call in support_response["tool_calls"]]
    latency_target = scenario["approach_a_live_api" if approach == "live_api" else "approach_b_pipeline"]["max_latency_ms"]
    interrupt_target = scenario["approach_a_live_api" if approach == "live_api" else "approach_b_pipeline"]["max_interrupt_latency_ms"]
    interrupt_latency = response.interrupt.latency_ms if response.interrupt else 0

    result = {
        "id": scenario["id"],
        "approach": approach,
        "expected_intent": scenario["expected_intent"],
        "actual_intent": support_response["intent"],
        "intent_correct": scenario["expected_intent"] == support_response["intent"],
        "expected_agent": scenario["expected_agent"],
        "actual_agent": support_response["selected_agent"],
        "routing_correct": routing_correct(scenario["expected_agent"], support_response["selected_agent"]),
        "expected_tools": scenario["expected_tools"],
        "actual_tools": actual_tools,
        "tool_recall": tool_recall(scenario["expected_tools"], actual_tools),
        "required_phrase_coverage": phrase_coverage(scenario["must_include"], response.text_response),
        "forbidden_phrase_violation": forbidden_phrase_violation(scenario["must_not_include"], response.text_response),
        "latency_ms": response.latency_ms,
        "max_latency_ms": latency_target,
        "interrupt_latency_ms": interrupt_latency,
        "max_interrupt_latency_ms": interrupt_target,
        "interrupt_detected": bool(response.interrupt and response.interrupt.interrupted),
        "wer": word_error_rate(scenario["transcript"], response.transcript),
        "text_response": response.text_response,
    }
    result["passed"] = (
        result["intent_correct"]
        and result["routing_correct"]
        and result["tool_recall"] >= 1.0
        and result["required_phrase_coverage"] >= 1.0
        and not result["forbidden_phrase_violation"]
        and result["latency_ms"] <= result["max_latency_ms"]
        and result["interrupt_latency_ms"] <= result["max_interrupt_latency_ms"]
        and result["wer"] <= 0.1
    )
    return result


def summarize_voice_results(results: list[dict]) -> dict:
    """Summarize voice evaluation results."""

    total = len(results)
    passed = len([result for result in results if result["passed"]])
    return {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "intent_accuracy": len([result for result in results if result["intent_correct"]]) / total if total else 0,
        "routing_accuracy": len([result for result in results if result["routing_correct"]]) / total if total else 0,
        "average_latency_ms": sum(result["latency_ms"] for result in results) / total if total else 0,
        "average_interrupt_latency_ms": sum(result["interrupt_latency_ms"] for result in results) / total if total else 0,
        "average_wer": sum(result["wer"] for result in results) / total if total else 0,
    }

