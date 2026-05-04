"""Evaluation metrics for support responses."""

from __future__ import annotations


def routing_correct(expected_agent: str, actual_agent: str) -> bool:
    """Return whether the actual agent matches the expected agent."""

    return expected_agent == actual_agent


def tool_recall(expected_tools: list[str], actual_tools: list[str]) -> float:
    """Return fraction of expected tools present in actual tool calls."""

    if not expected_tools:
        return 1.0
    actual_set = set(actual_tools)
    return len([tool for tool in expected_tools if tool in actual_set]) / len(expected_tools)


def phrase_coverage(required_phrases: list[str], text: str) -> float:
    """Return fraction of required phrases found in text."""

    if not required_phrases:
        return 1.0
    lowered = text.lower()
    return len([phrase for phrase in required_phrases if phrase.lower() in lowered]) / len(required_phrases)


def forbidden_phrase_violation(forbidden_phrases: list[str], text: str) -> bool:
    """Return whether any forbidden phrase appears in text."""

    lowered = text.lower()
    return any(phrase.lower() in lowered for phrase in forbidden_phrases)


def scenario_passed(result: dict) -> bool:
    """Return whether one evaluated scenario passes all gates."""

    return (
        result["routing_correct"]
        and result["intent_correct"]
        and result["tool_recall"] >= 1.0
        and result["required_phrase_coverage"] >= 1.0
        and not result["forbidden_phrase_violation"]
        and result["latency_ms"] <= result["max_latency_ms"]
    )


def summarize_results(results: list[dict]) -> dict:
    """Build an aggregate metrics summary."""

    total = len(results)
    passed = len([result for result in results if result["passed"]])
    average_latency = sum(result["latency_ms"] for result in results) / total if total else 0
    average_tool_recall = sum(result["tool_recall"] for result in results) / total if total else 0
    routing_accuracy = len([result for result in results if result["routing_correct"]]) / total if total else 0
    intent_accuracy = len([result for result in results if result["intent_correct"]]) / total if total else 0

    return {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "routing_accuracy": routing_accuracy,
        "intent_accuracy": intent_accuracy,
        "average_tool_recall": average_tool_recall,
        "average_latency_ms": average_latency,
    }

