from evals.run_eval_voice import evaluate_voice_scenario, load_voice_scenarios, run_voice_eval
from evals.voice_metrics import word_error_rate


def test_word_error_rate_exact_match() -> None:
    assert word_error_rate("hello world", "hello world") == 0.0


def test_load_voice_scenarios_has_minimum_set() -> None:
    assert len(load_voice_scenarios()) >= 10


def test_evaluate_voice_scenario_passes() -> None:
    result = evaluate_voice_scenario(load_voice_scenarios()[0], "live_api")

    assert result["passed"] is True


def test_run_voice_eval_both() -> None:
    report = run_voice_eval("both")

    assert report["summaries"]["live_api"]["total"] >= 10
    assert report["summaries"]["pipeline"]["total"] >= 10

