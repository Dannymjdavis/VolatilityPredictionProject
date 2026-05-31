---
name: run-volatility-project
description: run, test, screenshot, verify, smoke test the VolatilityPredictionProject utils (returns_utils, plotting_functions, ARCH/GARCH modelling)
---

This is a Python research library — no server, no GUI. The "app" is the `utils/` module layer
(returns, plotting, ARCH/GARCH) consumed by Jupyter notebooks. The driver is
`.claude/skills/run-volatility-project/driver.py`; it exercises all three layers in sequence
using synthetic data and exits 0 on success.

## Prerequisites

- Python venv at `c:\ProjectsDannyDavis\DDVenv\` (already installed on this machine)
- All dependencies already installed in that venv (`arch`, `pandas`, `numpy`, `matplotlib`, `seaborn`, `plotly`)

No `apt-get`, no `npm`, no build step — just run the driver.

## Run (agent path)

```powershell
& "c:\ProjectsDannyDavis\DDVenv\Scripts\python.exe" `
  "c:\ProjectsDannyDavis\VolatilityPredictionProject\.claude\skills\run-volatility-project\driver.py"
```

Add `--plot` to also save a PNG of price + return-distribution panels to
`.claude/skills/run-volatility-project/driver_output.png`:

```powershell
& "c:\ProjectsDannyDavis\DDVenv\Scripts\python.exe" `
  "c:\ProjectsDannyDavis\VolatilityPredictionProject\.claude\skills\run-volatility-project\driver.py" --plot
```

Expected output (all three layers pass):
```
=== VolatilityPredictionProject smoke test ===
  [OK] returns_utils — shape=(503, 4), fwd_vol non-null rows=482
  [OK] plotting_functions — plot saved to ...driver_output.png
  [OK] GARCH(1,1) — AIC=726.65, 5d variance forecast=[0.247 0.247 0.247 0.247 0.247]
=== ALL PASSED ===
```

## Direct invocation (for PRs that touch one module)

Import and call any util directly without the full driver:

```python
import sys
sys.path.insert(0, r"c:\ProjectsDannyDavis\VolatilityPredictionProject\utils")
from returns_utils import append_returns, append_fwd_vol
from plotting_functions import plot_line, plot_histogram
from arch import arch_model
```

Key conventions enforced by the code (not just docs):
- `append_returns(df, price_col)` always produces `simple_return` and `log_return` columns; drops the first row by default.
- `append_fwd_vol(df, returns_col)` annualises by `× √252`, default 20-day rolling window; last 20 rows will be NaN.
- `plot_line(df, x=None, y="col", dark=True)` — pass `x=None` to use the DataFrame index; do **not** pass a DatetimeIndex object as `x` (raises `ValueError: truth value of DatetimeIndex is ambiguous`).
- ARCH inputs must be scaled: `df["log_return"] * 100` before `arch_model(...)`.
- `plot_line` and `plot_histogram` return `(fig, ax)`, not just `ax`.

## Run (human path)

Open any notebook in VS Code with the **DDVenv** kernel selected, then run cells normally.
Notebooks live in `data_exploration/`, `time_series_tests/`, `time_series_modelling/`.

## Gotchas

- **`plot_line(df, x=df.index, ...)` crashes** — the `if x:` guard inside the function evaluates a DatetimeIndex as a boolean, which pandas forbids. Always pass `x=None` to use the index, or pass a column name string.
- **Matplotlib must be set to Agg before any import** — in headless/script contexts, call `matplotlib.use("Agg")` before `import matplotlib.pyplot`. The driver handles this automatically.
- **`forward_vol_1m` NaNs at tail** — the last `rolling_period` rows (default 20) are always NaN because the forward-looking window runs off the end of the series. This is by design.
- **ARCH convergence warnings** — `model.fit(disp="off")` suppresses output but `warnings.simplefilter("ignore")` is also needed to silence convergence warnings in scripts.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'arch'` | Run `& "c:\ProjectsDannyDavis\DDVenv\Scripts\pip.exe" install arch` |
| `ValueError: truth value of DatetimeIndex is ambiguous` | Pass `x=None` to `plot_line`, not a DatetimeIndex object |
| `command not found: python` in bash | Use PowerShell and the full venv path: `& "c:\ProjectsDannyDavis\DDVenv\Scripts\python.exe"` |
| Plot PNG is blank | Ensure `matplotlib.use("Agg")` is called before any `plt` import |
