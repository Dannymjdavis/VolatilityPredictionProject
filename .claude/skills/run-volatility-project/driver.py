"""
Smoke-test driver for VolatilityPredictionProject utils.

Usage:
    python driver.py [--plot]

    --plot   Save a PNG of price / return distribution to driver_output.png

Exits 0 on success, 1 on failure.  Every util module is exercised in order:
    1. returns_utils  (append_returns, append_fwd_vol)
    2. plotting_functions (plot_line, plot_histogram)
    3. arch_model    (GARCH(1,1) fit + 5-day forecast)
"""

import sys
import argparse
import warnings

# ── Headless backend BEFORE any matplotlib import ──────────────────────────
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

UTILS = r"c:\ProjectsDannyDavis\VolatilityPredictionProject\utils"
sys.path.insert(0, UTILS)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

SEED = 42
N = 504  # ~2 trading years


def make_prices(n=N):
    np.random.seed(SEED)
    return pd.DataFrame(
        {"close": 4000 + np.cumsum(np.random.randn(n) * 20)},
        index=pd.date_range("2022-01-01", periods=n, freq="B"),
    )


def test_returns_utils():
    from returns_utils import append_returns, append_fwd_vol

    df = append_returns(make_prices(), "close")
    assert "simple_return" in df.columns, "missing simple_return"
    assert "log_return" in df.columns, "missing log_return"

    df = append_fwd_vol(df, "log_return")
    assert "forward_vol_1m" in df.columns, "missing forward_vol_1m"
    non_null = df["forward_vol_1m"].notna().sum()
    print(f"  [OK] returns_utils — shape={df.shape}, fwd_vol non-null rows={non_null}")
    return df


def test_plotting(df, save_plot=False):
    from plotting_functions import plot_line, plot_histogram

    fig, ax = plot_line(df, x=None, y="close", title="Price (smoke)", dark=True)  # noqa: F841
    assert ax is not None, "plot_line returned None ax"

    fig2, ax2 = plot_histogram(df["log_return"], title="Returns (smoke)", dark=True)  # noqa: F841
    assert ax2 is not None, "plot_histogram returned None ax"

    if save_plot:
        out_path = r"c:\ProjectsDannyDavis\VolatilityPredictionProject\.claude\skills\run-volatility-project\driver_output.png"
        fig_out, axes = plt.subplots(2, 1, figsize=(10, 6))
        plot_line(df, x=None, y="close", title="Price", dark=True, ax=axes[0])
        plot_histogram(df["log_return"], title="Log Returns", dark=True, ax=axes[1])
        fig_out.savefig(out_path, dpi=80, bbox_inches="tight")
        print(f"  [OK] plotting_functions — plot saved to {out_path}")
    else:
        print(f"  [OK] plotting_functions — render OK (pass --plot to save PNG)")

    plt.close("all")


def test_arch(df):
    from arch import arch_model as build_arch

    returns_scaled = df["log_return"] * 100  # ARCH convention
    model = build_arch(returns_scaled, vol="GARCH", p=1, q=1, dist="Normal")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = model.fit(disp="off")

    assert result.aic is not None, "GARCH fit returned no AIC"
    forecast = result.forecast(horizon=5)
    h5 = forecast.variance.iloc[-1].values
    print(f"  [OK] GARCH(1,1) — AIC={result.aic:.2f}, 5d variance forecast={h5.round(4)}")


def main():
    parser = argparse.ArgumentParser(description="VolatilityPredictionProject smoke driver")
    parser.add_argument("--plot", action="store_true", help="Save plot PNG to skill dir")
    args = parser.parse_args()

    print("=== VolatilityPredictionProject smoke test ===")
    try:
        df = test_returns_utils()
        test_plotting(df, save_plot=args.plot)
        test_arch(df)
        print("=== ALL PASSED ===")
        sys.exit(0)
    except Exception as exc:
        print(f"  [FAIL] {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
