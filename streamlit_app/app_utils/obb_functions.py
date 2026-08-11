import importlib.util
import os
import shutil
import sys
import tempfile
from pathlib import Path

import pandas as pd


def _ensure_openbb_package_writable() -> None:
    """Make sure `import openbb` resolves to a writable copy of the package.

    openbb rebuilds its extension package on import (writing .build.lock and
    generating package/*.py) whenever installed extensions differ from its
    shipped reference.json — true on every fresh deploy. Streamlit Cloud
    installs dependencies with uv, which links package files from a shared
    cache and marks them read-only to protect that cache; the app's user
    doesn't own them, so neither writing nor chmod'ing them works.

    Instead of fighting that, copy the small, pre-build `openbb` package
    directory into a writable temp dir and prioritise it on sys.path so the
    import resolves there. The heavier openbb_* extension packages
    (openbb_equity, openbb_index, ...) never need to be written to and stay
    where uv installed them.

    No-op wherever the installed package is already writable, e.g. local dev.
    """
    spec = importlib.util.find_spec("openbb")
    if not spec or not spec.submodule_search_locations:
        return
    openbb_dir = Path(list(spec.submodule_search_locations)[0])
    if os.access(openbb_dir, os.W_OK):
        return

    writable_root = Path(tempfile.gettempdir()) / "openbb_writable_package"
    writable_openbb_dir = writable_root / "openbb"
    if not writable_openbb_dir.exists():
        shutil.copytree(openbb_dir, writable_openbb_dir)
    sys.path.insert(0, str(writable_root))


_ensure_openbb_package_writable()

from openbb import obb  # noqa: E402
from openbb_core.app.command_runner import CommandRunner  # noqa: E402

# COMMAND RUNNER
_command_runner = CommandRunner()

# AVAILABLE INDICES FROM PROVIDER
def check_available_indices(provider: str) -> pd.DataFrame:
    """
    Returns a DataFrame containing the available index data from a provider.

    Parameters
    ----------
    provider : str
        (cboe, yfinance, fmp)

    """
    available_result = obb.index.available(provider=provider) # pyright: ignore[reportAttributeAccessIssue] # type: ignore
    records = [r.model_dump() for r in available_result.results] # type: ignore
    df = pd.DataFrame(records)
    df = df.dropna(axis=1, how="all")
    df = df.set_index("symbol")
    return df

# COLLECT INDEX PRICE DATA
def get_index_price_data(symbol: str, start: str, end: str, provider='cboe', interval='1d') -> pd.DataFrame :
    """
    Returns a DataFrame containing open, high, low, and close of a given index.

    Parameters
    ----------
    symbol : str
        available from check_available_indices()

    start: str
        format 'YYYY-MM-DD'
    
    end: str
        format 'YYYY-MM-DD'
    
    provider: str
        yfinance or cboe
    
    interval: str
        default daily
    """
    result = obb.index.price.historical(symbol, start_date=start, end_date=end, provider=provider, interval=interval) # pyright: ignore[reportAttributeAccessIssue] # type: ignore
    df = result.to_df()
    return df

command_coverage_dict = _command_runner.command_map.command_coverage

_command_headings = list(set([key.split("/")[1] for key in command_coverage_dict.keys()]))

def explore_paths(heading: str|None= None):
    """Collect available paths for a given heading.
    
    Execute _command_headings to explore high-level headings.
    
    Example:
    explore_paths('regulators/cftc/')
    """
    if heading is None:
        return command_coverage_dict
    else:
        exploration_dict = {}
        for command, provider in command_coverage_dict.items():
            if command.startswith(f"/{heading}"):
                exploration_dict[command] = provider
        return exploration_dict

def explore_query_inputs(query_path: str):
    """Explore standard and extra inputs for a query.
    
    Run .explore_paths() to explore query paths.
    
    Output
    ---
    >>> {'standard_params':{}. 'extra_params':{}}"""
    exploration_dict = obb.reference['paths'][query_path]['parameters'] # type: ignore # pyright: ignore[reportAttributeAccessIssue]

    param_dict = {'standard_params':{}, 'extra_params':{}}

    for key, values in exploration_dict.items():
        if key.startswith('standard'):
            param_dict['standard_params'] = values
        else:
            param_dict['extra_params'][key] = values

    return param_dict

# RUN A COMMAND VIA COMMANDRUNNER (bypasses the generated static package)
def run_query(path: str, provider: str, standard_params: dict = {}, extra_params: dict = {}) -> pd.DataFrame:
    """
    Execute any OpenBB command discovered via explore_paths().

    Example
    -------
    >>> run_query(path="/regulators/cftc/cot",
    provider='cftc',
    standard_params={'id':'13874+','start_date':'2015-01-01', 'end_date':'2020-01-01'})
    """
    result = _command_runner.sync_run(
        path,
        provider_choices={'provider': provider},
        standard_params=standard_params,
        extra_params=extra_params,
    )
    return result.to_df()