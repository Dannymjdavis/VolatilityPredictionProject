import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Optional, Union

# ─────────────────────────────────────────────
# COLOR PALETTES
# ─────────────────────────────────────────────

color_primary = {
    "Teal Blue": ["#0097A7", (0, 151, 167)],
}

color_palette_teal_blue = {
    "Deep Teal":     ["#003D4C", (0, 61, 76)],
    "Ocean Teal":    ["#006175", (0, 97, 117)],
    "Classic Teal":  ["#008080", (0, 128, 128)],
    "Cerulean Teal": ["#00ACC1", (0, 172, 193)],
    "Bright Teal":   ["#00BCD4", (0, 188, 212)],
    "Sky Teal":      ["#26C6DA", (38, 198, 218)],
    "Light Teal":    ["#4DD0E1", (77, 208, 225)],
    "Pale Teal":     ["#80DEEA", (128, 222, 234)],
    "Mint Teal":     ["#B2EBF2", (178, 235, 242)],
}

color_accents = {
    "Dark Anchor": ["#003D4C", (0, 61, 76)],    # darkest — text, headers
    "Mid Tone":    ["#006175", (0, 97, 117)],    # supporting dark — borders, icons
    "Highlight":   ["#00BCD4", (0, 188, 212)],   # one step above primary — hover/active states
    "Soft":        ["#4DD0E1", (77, 208, 225)],  # light accent — backgrounds, tags
}

default_figsize = (11,4)

# Ordered list for cycling through the teal palette
TEAL_SEQUENCE = [v[0] for v in color_palette_teal_blue.values()]

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def _apply_dark_theme(ax: plt.Axes, fig: plt.Figure) -> None:
    """Apply consistent dark background styling."""
    bg = "#0D1117"
    grid_color = "#1F2937"
    text_color = "#E5E7EB"

    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)
    ax.tick_params(colors=text_color)
    ax.xaxis.label.set_color(text_color)
    ax.yaxis.label.set_color(text_color)
    ax.title.set_color(text_color)
    ax.spines["bottom"].set_color(grid_color)
    ax.spines["left"].set_color(grid_color)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.grid(True, color=grid_color, linewidth=0.6, linestyle="--")
    ax.set_axisbelow(True)


def _add_legend(ax: plt.Axes, dark: bool = True) -> None:
    legend = ax.legend(
        framealpha=0.15,
        edgecolor="#1F2937" if dark else "lightgrey",
        labelcolor="#E5E7EB" if dark else "black",
    )
    if dark and legend:
        legend.get_frame().set_facecolor("#0D1117")


# ─────────────────────────────────────────────
# LINE CHART
# ─────────────────────────────────────────────

def plot_line(
    data: Union[pd.DataFrame, dict],
    x: Optional[str] = None,
    y: Optional[Union[str, list[str]]] = None,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    figsize: tuple[float, float] = default_figsize,
    colors: Optional[list[str]] = None,
    linewidth: float = 1.8,
    alpha: float = 1.0,
    markers: bool = False,
    dark: bool = False,
    percent_y: bool = False,
    y_format: Optional[str] = None,
    ax: Optional[plt.Axes] = None,
) -> tuple[plt.Figure, plt.Axes]:
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.get_figure()

    colors = colors or TEAL_SEQUENCE
    marker_style = "o" if markers else None

    if isinstance(data, dict):
        for i, (label, values) in enumerate(data.items()):
            ax.plot(values, label=label, color=colors[i % len(colors)],
                    linewidth=linewidth, alpha=alpha, marker=marker_style, markersize=4)
    else:
        x_vals = data[x] if x else data.index
        cols = ([y] if isinstance(y, str) else y) if y else [c for c in data.columns if c != x]
        for i, col in enumerate(cols):
            ax.plot(x_vals, data[col], label=col, color=colors[i % len(colors)],
                    linewidth=linewidth, alpha=alpha, marker=marker_style, markersize=4)

    ax.set_title(title, fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)

    if percent_y:
        ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0))
    elif y_format:
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: y_format.format(x=x)))

    if dark:
        _apply_dark_theme(ax, fig)
    _add_legend(ax, dark)
    if ax.get_figure() == plt.gcf():
        plt.tight_layout()
    return fig, ax


# ─────────────────────────────────────────────
# HISTOGRAM
# ─────────────────────────────────────────────

def plot_histogram(
    data: Union[pd.Series, np.ndarray, list, dict],
    bins: Union[int, str] = 50,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "Frequency",
    figsize: tuple[float, float] = default_figsize,
    colors: Optional[list[str]] = None,
    alpha: float = 0.75,
    kde: bool = True,
    dark: bool = False,
    density: bool = False,
    ax: Optional[plt.Axes] = None,
) -> tuple[plt.Figure, plt.Axes]:
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.get_figure()

    colors = colors or TEAL_SEQUENCE

    if isinstance(data, dict):
        for i, (label, values) in enumerate(data.items()):
            ax.hist(values, bins=bins, color=colors[i % len(colors)],
                    alpha=alpha, label=label, density=density)
            if kde:
                from scipy.stats import gaussian_kde
                vals = np.array(values)
                vals = vals[~np.isnan(vals)]
                kde_fn = gaussian_kde(vals)
                x_range = np.linspace(vals.min(), vals.max(), 300)
                scale = len(vals) * (vals.max() - vals.min()) / bins if not density else 1
                ax.plot(x_range, kde_fn(x_range) * (1 if density else scale),
                        color=colors[i % len(colors)], linewidth=2)
    else:
        arr = np.array(data)
        arr = arr[~np.isnan(arr)]
        ax.hist(arr, bins=bins, color=colors[0], alpha=alpha, density=density)
        if kde:
            from scipy.stats import gaussian_kde
            kde_fn = gaussian_kde(arr)
            x_range = np.linspace(arr.min(), arr.max(), 300)
            scale = len(arr) * (arr.max() - arr.min()) / (bins if isinstance(bins, int) else len(np.histogram_bin_edges(arr, bins=bins)) - 1)
            ax.plot(x_range, kde_fn(x_range) * (1 if density else scale),
                    color=color_accents["Highlight"][0], linewidth=2, label="KDE")

    ax.set_title(title, fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)

    if dark:
        _apply_dark_theme(ax, fig)
    _add_legend(ax, dark)
    if ax.get_figure() == plt.gcf():
        plt.tight_layout()
    return fig, ax


# ─────────────────────────────────────────────
# BAR PLOT
# ─────────────────────────────────────────────

def plot_bar(
    data: Union[pd.Series, pd.DataFrame, dict],
    x: Optional[str] = None,
    y: Optional[Union[str, list[str]]] = None,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    figsize: tuple[float, float] = default_figsize,
    colors: Optional[list[str]] = None,
    alpha: float = 0.9,
    horizontal: bool = False,
    stacked: bool = False,
    dark: bool = False,
    bar_width: float = 0.8,
    value_labels: bool = False,
    y_format: Optional[str] = None,
    percent_y: bool = False,
    ax: Optional[plt.Axes] = None,
) -> tuple[plt.Figure, plt.Axes]:
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.get_figure()

    colors = colors or TEAL_SEQUENCE

    # Normalise input to a DataFrame
    if isinstance(data, dict):
        df = pd.Series(data).to_frame(name="value")
    elif isinstance(data, pd.Series):
        df = data.to_frame(name=data.name or "value")
    else:
        df = data.copy()
        if x:
            df = df.set_index(x)
        if y:
            df = df[[y] if isinstance(y, str) else y]

    bar_kwargs = dict(width=bar_width, alpha=alpha, stacked=stacked)
    plot_fn = df.plot.barh if horizontal else df.plot.bar

    if len(df.columns) == 1:
        bar_kwargs["color"] = colors[0]
    else:
        bar_kwargs["color"] = colors[: len(df.columns)]

    plot_fn(ax=ax, **bar_kwargs)

    if value_labels:
        for container in ax.containers:
            ax.bar_label(container, fmt="%.2f", padding=3,
                         color="#E5E7EB" if dark else "black", fontsize=8)

    ax.set_title(title, fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)

    value_axis = ax.yaxis if not horizontal else ax.xaxis
    if percent_y:
        value_axis.set_major_formatter(mticker.PercentFormatter(xmax=1.0))
    elif y_format:
        value_axis.set_major_formatter(mticker.FuncFormatter(lambda x, _: y_format.format(x=x)))

    if dark:
        _apply_dark_theme(ax, fig)
    _add_legend(ax, dark)
    if ax.get_figure() == plt.gcf():
        plt.tight_layout()
    return fig, ax


# ─────────────────────────────────────────────
# SCATTER PLOT
# ─────────────────────────────────────────────

def plot_scatter(
    data: pd.DataFrame,
    x: str,
    y: str,
    hue: Optional[str] = None,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    figsize: tuple[float, float] = default_figsize,
    colors: Optional[list[str]] = None,
    alpha: float = 0.7,
    size: float = 30,
    dark: bool = False,
    trend_line: bool = False,
    percent_x: bool = False,
    percent_y: bool = False,
    ax: Optional[plt.Axes] = None,
) -> tuple[plt.Figure, plt.Axes]:
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.get_figure()

    colors = colors or TEAL_SEQUENCE

    if hue is not None:
        categories = data[hue].unique()
        for i, cat in enumerate(categories):
            mask = data[hue] == cat
            subset = data[mask]
            color = colors[i % len(colors)]
            ax.scatter(subset[x], subset[y], label=str(cat), color=color,
                       alpha=alpha, s=size, edgecolors="none")
            if trend_line:
                coeffs = np.polyfit(subset[x].astype(float), subset[y].astype(float), 1)
                x_range = np.linspace(subset[x].min(), subset[x].max(), 200)
                ax.plot(x_range, np.polyval(coeffs, x_range), color=color,
                        linewidth=1.5, linestyle="--", alpha=0.9)
    else:
        ax.scatter(data[x], data[y], color=colors[0], alpha=alpha,
                   s=size, edgecolors="none")
        if trend_line:
            coeffs = np.polyfit(data[x].astype(float), data[y].astype(float), 1)
            x_range = np.linspace(data[x].min(), data[x].max(), 200)
            ax.plot(x_range, np.polyval(coeffs, x_range),
                    color=color_accents["Highlight"][0],
                    linewidth=1.8, linestyle="--", label="Trend")

    ax.set_title(title, fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel(xlabel or x, fontsize=11)
    ax.set_ylabel(ylabel or y, fontsize=11)

    if percent_x:
        ax.xaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0))
    if percent_y:
        ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0))

    if dark:
        _apply_dark_theme(ax, fig)
    if hue is not None or trend_line:
        _add_legend(ax, dark)
    if ax.get_figure() == plt.gcf():
        plt.tight_layout()
    return fig, ax


# ─────────────────────────────────────────────
# FUTURES CURVE WITH POLYNOMIAL FITS
# ─────────────────────────────────────────────

def plot_futures_curve(
    prices: Union[pd.Series, np.ndarray, list],
    dte: Union[pd.Index, np.ndarray, list],
    n: int = 3,
    title: str = "",
    xlabel: str = "Days to Expiration",
    ylabel: str = "Price",
    figsize: tuple[float, float] = default_figsize,
    smooth_points: int = 300,
    dark: bool = False,
    markers: bool = True,
    ax: Optional[plt.Axes] = None,
) -> tuple[plt.Figure, plt.Axes]:
    prices = np.asarray(prices, dtype=float)
    x = np.asarray(dte, dtype=float)
    x_smooth = np.linspace(x.min(), x.max(), smooth_points)

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.get_figure()

    raw_color = color_primary["Teal Blue"][0]
    ax.plot(x, prices, label="Raw", color=raw_color, linewidth=2.0,
            linestyle="-", marker="o" if markers else None, markersize=5, zorder=3)

    fit_colors = TEAL_SEQUENCE[1:] + TEAL_SEQUENCE[:1]
    degree_labels = {0: "Constant", 1: "Linear", 2: "Quadratic",
                     3: "Cubic", 4: "Quartic", 5: "Quintic"}

    for deg in range(n + 1):
        coeffs = np.polyfit(x, prices, deg)
        y_fit = np.polyval(coeffs, x_smooth)
        label = f"Deg {deg} ({degree_labels.get(deg, f'Poly-{deg}')})"
        color = fit_colors[deg % len(fit_colors)]
        ax.plot(x_smooth, y_fit, label=label, color=color,
                linewidth=1.6, linestyle="--", alpha=0.85)

    ax.set_title(title, fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)

    if dark:
        _apply_dark_theme(ax, fig)
    _add_legend(ax, dark)
    if ax.get_figure() == plt.gcf():
        plt.tight_layout()
    return fig, ax


# ─────────────────────────────────────────────
# MULTI-PANEL / SUBPLOT GRID
# ─────────────────────────────────────────────

def plot_subplots(
    plot_configs: list[dict],
    ncols: int = 2,
    figsize: Optional[tuple[float, float]] = None,
    suptitle: str = "",
    dark: bool = False,
) -> tuple[plt.Figure, np.ndarray]:
    """
    Create a grid of subplots from a list of plot configurations.

    Each config dict supports keys: type ('line'|'bar'|'hist'|'scatter'), data,
    title, xlabel, ylabel, and all kwargs accepted by the matching plot_* function
    (minus figsize/dark which are set globally here).

    Parameters
    ----------
    plot_configs : List of dicts, one per panel
    ncols        : Number of columns in the grid
    figsize      : Overall figure size; auto-calculated if None
    suptitle     : Figure-level title

    Example
    -------
    >>> import numpy as np
    >>> x = np.linspace(0, 10, 100)
    >>> configs = [
    ...     {
    ...         "type": "scatter",
    ...         "data": {"x": x, "y": np.random.randn(100)},
    ...         "title": "Random Scatter",
    ...         "xlabel": "x",
    ...         "ylabel": "y",
    ...     },
    ...     {
    ...         "type": "line",
    ...         "data": {"x": x, "y": np.sin(x)},
    ...         "title": "Sine Wave",
    ...         "xlabel": "x",
    ...         "ylabel": "sin(x)",
    ...     },
    ... ]
    >>> fig, axes = plot_subplots(configs, ncols=2, suptitle="Example Grid")
    """
    n = len(plot_configs)
    nrows = (n + ncols - 1) // ncols
    if figsize is None:
        figsize = (ncols * 7, nrows * 4.5)

    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, squeeze=False)
    flat_axes = axes.flatten()

    dispatchers = {"line": plot_line, "bar": plot_bar, "hist": plot_histogram, "scatter": plot_scatter}

    for cfg, ax in zip(plot_configs, flat_axes):
        cfg = cfg.copy()
        plot_type = cfg.pop("type", "line")
        cfg.pop("figsize", None)
        cfg["dark"] = dark
        cfg["ax"] = ax
        dispatchers[plot_type](**cfg)

    for ax in flat_axes[n:]:
        ax.set_visible(False)

    if suptitle:
        fig.suptitle(suptitle, fontsize=16, fontweight="bold",
                     color="#E5E7EB" if dark else "black", y=1.01)
    if dark:
        fig.patch.set_facecolor("#0D1117")

    plt.tight_layout()
    return fig, axes


# ─────────────────────────────────────────────
# BARE AXES
# ─────────────────────────────────────────────

def create_ax(
    figsize: tuple[float, float] = default_figsize,
    dark: bool = False,
) -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=figsize)
    if dark:
        _apply_dark_theme(ax, fig)
    return fig, ax
