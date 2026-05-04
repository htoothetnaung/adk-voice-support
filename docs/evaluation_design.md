# Evaluation Design

Text evaluation runs with:

```powershell
python -m evals.run_eval
```

Voice evaluation runs with:

```powershell
python -m evals.run_eval_voice --approach both --compare
```

Metrics include:

- intent accuracy
- routing accuracy
- tool recall
- required phrase coverage
- forbidden phrase violations
- latency
- voice WER and interrupt latency

Reports are saved under `evals/reports/` and ignored by Git.

