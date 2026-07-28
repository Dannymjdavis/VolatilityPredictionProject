import pandas as pd
from openbb import obb
from openbb_core.app.command_runner import CommandRunner

# COMMAND RUNNER
_command_runner = CommandRunner()

# AVAILABLE COMMANDS FOR A GIVEN HEADING
def get_commands_by_heading(heading: str) -> dict:
    """
    Returns a filtered subset of obb.coverage.commands for a given top-level heading.

    Parameters
    ----------
    heading : str
        Top-level category to filter by (e.g. 'commodity', 'crypto', 'economy',
        'equity', 'etf', 'fixedincome', 'index', 'news', 'derivatives',
        'currency', 'regulators', 'uscongress').
    Example
    -------
    >>> get_commands_by_heading('economy')
    {'.economy.gdp.forecast': ['oecd'], ...}
    """
    prefix = f".{heading}."
    return {k: v for k, v in obb.coverage.commands.items() if k.startswith(prefix)}

# INPUTS REQUIRED FOR A COMMAND
def explore_query_inputs(command: str, provider: str) -> dict :
    '''
    Returns the required parameters for an openbb command.

    --------------
    Parameters:
        command: str
            Query to check inputs. Can be obtain from function get_commands_by_heading

        provider: str
            The provider to query
    
    --------------
    Example:
        explore_query_inputs(command: '.derivatives.options.chains', provider: 'cboe')
    '''
    params = obb.coverage.command_model[command][provider]['QueryParams']['fields']

    return params

# OUTPUTS PRODUCED FROM A COMMAND
def explore_query_outputs(command: str, provider: str) -> dict :
    '''
    Returns output features of an openbb command.

    --------------
    Parameters:
        command: str
            Query to check. Can be obtain from function get_commands_by_heading

        provider: str
            The provider to query
    
    --------------
    Example:
        explore_query_outputs(command: '.derivatives.options.chains', provider: 'cboe')
    '''
    params = obb.coverage.command_model[command][provider]['Data']['fields']

    return params

# AVAILABLE INDICES FROM PROVIDER
def check_available_indices(provider: str) -> pd.DataFrame:
    """
    Returns a DataFrame containing the available index data from a provider.

    Parameters
    ----------
    provider : str
        (cboe, yfinance, fmp)

    """
    available_result = obb.index.available(provider=provider)
    records = [r.model_dump() for r in available_result.results]
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
    result = obb.index.price.historical(symbol, start_date=start, end_date=end, provider=provider, interval=interval)
    df = result.to_df()
    return df

# DOWNLOAD FUTURES CURVE DATA
def get_futures_curve_data(dates: list, symbol='VX_EOD', provider='cboe') -> pd.DataFrame :
    '''Downloads futures prices across different expiry dates.
    
    Parameters
    --------------------------
        symbol: str
        provider: str
        dates: list containing str
            Format 'YYYY-MM-DD'
    '''
    df = obb.derivatives.futures.curve(symbol, provider=provider, date=dates)
    df = df.to_df()

    df.index = pd.to_datetime(df.index)
    df['expiration'] = pd.to_datetime(df['expiration'])

    df.sort_values(['date', 'expiration', 'symbol'], inplace=True)
    df['DTE'] = df['expiration'] - df.index

    df['DTE'] = df['DTE'].dt.days
    df = df[df['DTE']>0]

    return df

# FULL QUERY-BUILDER MAP FOR A HEADING
def describe_heading(heading: str) -> dict:
    """
    Every command, provider, and input parameter under a heading — enough
    to render a dynamic form (name, type, default, choices, description).

    Returns
    -------
    {command: {provider: {param_name: {..., 'scope': 'standard'|'extra'}}}}

    'standard' params are shared across all providers for that command;
    'extra' params are provider-specific and go in extra_params when
    calling run_query().

    Example
    -------
    >>> describe_heading('derivatives')['.derivatives.futures.curve']['cboe']
    """
    prefix = f".{heading}."
    routes = {k: v for k, v in obb.coverage.commands.items() if k.startswith(prefix)}
    out = {}
    for command, providers in routes.items():
        route = command.replace('.', '/')
        node = obb.reference['paths'][route]
        standard = node['parameters']['standard']
        cmd_out = {}
        for provider in providers:
            merged = {p['name']: {**p, 'scope': 'standard'} for p in standard}
            for p in node['parameters'].get(provider, []):
                merged[p['name']] = {**p, 'scope': 'extra'}
            cmd_out[provider] = merged
        out[command] = cmd_out
    return out

# RUN A COMMAND VIA COMMANDRUNNER (bypasses the generated static package)
def run_query(command: str, provider: str, **params) -> pd.DataFrame:
    """
    Execute any OpenBB command discovered via describe_heading(), splitting
    the flat params dict into standard_params/extra_params automatically.

    Example
    -------
    >>> run_query('.derivatives.futures.curve', 'cboe', symbol='VX_EOD', date='2024-01-05')
    """
    route = command.replace('.', '/')
    node = obb.reference['paths'][route]
    standard_names = {p['name'] for p in node['parameters']['standard']}
    extra_names = {p['name'] for p in node['parameters'].get(provider, [])}

    standard_params = {k: v for k, v in params.items() if k in standard_names}
    extra_params = {k: v for k, v in params.items() if k in extra_names and k not in standard_names}

    result = _command_runner.sync_run(
        route,
        provider_choices={'provider': provider},
        standard_params=standard_params,
        extra_params=extra_params,
    )
    return result.to_df()

