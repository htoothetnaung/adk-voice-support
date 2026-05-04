from evals.run_eval import evaluate_scenario, load_scenarios


def test_load_scenarios_has_minimum_set() -> None:
    scenarios = load_scenarios()

    assert len(scenarios) >= 12


def test_evaluate_first_scenario_passes() -> None:
    scenario = load_scenarios()[0]
    result = evaluate_scenario(scenario)

    assert result["passed"] is True
    assert result["actual_agent"] == "billing_agent"

