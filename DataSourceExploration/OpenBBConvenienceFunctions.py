import numpy as np
import pandas as pd
from openbb import obb

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

# APPEND RETURNS COLUMNS
def append_returns(df: pd.DataFrame, price_column: str, drop_first=True) -> pd.DataFrame :
    '''
    Appends simple and log returns columns.

    Parameters
    --------------
    df: DataFrame
        DataFrame to append returns columns.

    price_column: str
        Label of the column to compute returns
    
    drop_first: bool
        Whether or not to drop the first column
    '''
    df['simple_return'] = df[price_column].pct_change()
    df['log_return'] = np.log(df['simple_return'] + 1)

    if drop_first is True:
        return df.iloc[1:]
    else:
        return df
