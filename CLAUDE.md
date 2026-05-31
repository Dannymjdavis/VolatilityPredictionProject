# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment

- **Python interpreter / venv**: `c:\ProjectsDannyDavis\DDVenv\Scripts\python.exe`
- **Install dependencies**: `pip install -r requirements.txt` (run from venv)
- **Run a notebook**: open in VS Code using the DDVenv kernel, or `jupyter notebook` from the venv
- **Run a standalone script**: `c:\ProjectsDannyDavis\DDVenv\Scripts\python.exe <script.py>`

## Architecture

This is a research-stage volatility forecasting pipeline. Work flows left-to-right across three notebook layers:

```
data_exploration/  →  time_series_tests/  →  time_series_modelling/
(fetch & explore)     (diagnostics)           (ARCH/GARCH fitting)
```

All notebooks pull shared helpers from `utils/` by inserting the absolute path at the top:
```python
sys.path.insert(0, r"c:\ProjectsDannyDavis\VolatilityPredictionProject\utils")
```

### `utils/` modules

| Module | Purpose |
|---|---|
| `obb_functions.py` | OpenBB wrappers — fetch index prices, futures curves, check available commands/providers |
| `returns_utils.py` | Compute simple/log returns (`append_returns`) and annualised forward vol (`append_fwd_vol`) |
| `plotting_functions.py` | Opinionated matplotlib plots with a teal-blue dark theme; `plot_line`, `plot_histogram`, `plot_bar`, `plot_scatter`, `plot_futures_curve`, `plot_subplots` |
| `file_reader.py` | `read_file()` — thin wrapper over `pd.read_parquet/csv/excel` |
| `File_Paths.py` | Defines `raw_data_filepath` pointing to local OneDrive parquet store |
| `API_Keys.py` | Stores the FMP API key as a plain string constant (`FMP_API`) |

### Data storage

Raw data lives outside the repo at `C:\Users\dannydavis\OneDrive\VolatilityModellingProject\RawData` (defined in `utils/File_Paths.py`). Parquet is the default format.

### Key conventions

- **ARCH inputs must be scaled by 100** — returns are percentage-point values (`SAP500 * 100`) before passing to `arch_model()`.
- **Returns column names**: `append_returns()` always produces `simple_return` and `log_return` columns.
- **Forward vol**: `append_fwd_vol()` annualises by `× √252`; default rolling window is 20 trading days.
- **Plotting dark theme**: pass `dark=True` to any `plot_*` function for the dark teal palette; the default is light. All `plot_*` functions accept an `ax=` kwarg for embedding in `plot_subplots`.
- **OpenBB exploration helpers**: use `get_commands_by_heading()` to discover available endpoints and `explore_query_inputs/outputs()` to inspect provider schemas before building a query.

## Data sources

| Source | Library | Notes |
|---|---|---|
| OpenBB | `openbb` | Equity prices, index data, VIX futures curve, derivatives chains |
| CFTC COT reports | via OpenBB `regulators` heading | Weekly speculator/hedger positioning data |
| FMP | REST API (key in `API_Keys.py`) | Financial Modelling Prep; key is stored in plaintext — keep out of commits |
