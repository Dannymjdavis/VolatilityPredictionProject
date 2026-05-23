"""Utilities for computing returns attributes."""

import pandas as pd
import numpy as np

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

# APPEND FWD VOL
def append_fwd_vol(df: pd.DataFrame, returns_column: str, rolling_period: 20, fwd_vol_col_name="forward_vol_1m") -> pd.DataFrame :
    '''
    Appends 1-month forward volatility (annualised)

    Parameters
    --------------
    df: DataFrame
        DataFrame to append fwd vol column.

    returns_column: str
        Label of the column to compute standard deviation
    
    rolling_period: int
        Default 20 days (approx. 1 month)

    fwd_vol_col_name: str
        New column name for fwd vol
    '''
    rolling_period_plus_1 = rolling_period+1

    df[fwd_vol_col_name] = df[returns_column].shift(-1).rolling(rolling_period_plus_1).std().shift(-rolling_period) * np.sqrt(252)

    return df