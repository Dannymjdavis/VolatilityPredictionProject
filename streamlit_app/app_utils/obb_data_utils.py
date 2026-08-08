"""Volatility app utilities."""
from app_utils.app_data_codes import cot_contract_dict, futures_curve_types
from typing import Literal
import pandas as pd
import numpy as np
from pandas.tseries.offsets import BusinessDay, BusinessMonthEnd
from app_utils.obb_functions import run_query

#####################
### COT CONTRACTS ###
#####################

cot_contracts = cot_contract_dict()
cot_contract_selection_list = list(cot_contracts.keys())

def import_cot_data(contract_name: str, start_date: str = '2010-01-01', end_date: str = '2025-12-31', all_columns: bool = False):
    """Committment of Traders report data between two dates."""
    contract_code = cot_contracts[contract_name]

    cot_df = run_query(path='/regulators/cftc/cot', provider='cftc', standard_params={'id': contract_code, 'start_date': start_date, 'end_date': end_date})

    cot_df.index = pd.to_datetime(cot_df.index)
    if all_columns:
        return cot_df
    else:
        return cot_df [['noncomm_positions_long_all','noncomm_positions_short_all','noncomm_postions_spread_all',
                    'comm_positions_long_all','comm_positions_short_all',
                    'nonrept_positions_long_all','nonrept_positions_short_all',
                    'tot_rept_positions_long_all', 'tot_rept_positions_short',
                    'conc_net_le_4_tdr_long_all','conc_net_le_4_tdr_short_all',
                    'conc_net_le_8_tdr_long_all','conc_net_le_8_tdr_short_all']]

def cot_oi_proportions_by_type(cot_df: pd.DataFrame) -> pd.DataFrame:
    """Proportion of total open interest held by each investor type.

    Commercial: Hedging Positions
    Non-Commercial: Speculative Positions
    Non-Reportable: Retail

    """
    proportion_df = pd.DataFrame(index=cot_df.index)
    proportion_df['Hedging'] = cot_df[['comm_positions_long_all', 'comm_positions_short_all']].mean(axis=1)
    proportion_df['Speculator'] = (
        cot_df[['noncomm_positions_long_all', 'noncomm_positions_short_all']].mean(axis=1)
        + cot_df['noncomm_postions_spread_all']
    )
    proportion_df['Retail'] = cot_df[['nonrept_positions_long_all', 'nonrept_positions_short_all']].mean(axis=1)

    total = proportion_df.sum(axis=1)
    return proportion_df.div(total, axis=0)

def cot_long_short_proportions(cot_df: pd.DataFrame):
    """The proportion of contracts sold long and short for each investor classification.
    
    short_prop = 1 - long_prop
    (long_prop + short_prop always sum to 1 - this is a directional-bias read on a single group, not a share of overall open interest).
    """
    position_dict = {
        'Speculative': ['noncomm_positions_long_all', 'noncomm_positions_short_all'],
        'Hedging': ['comm_positions_long_all', 'comm_positions_short_all'],
        'Retail': ['nonrept_positions_long_all', 'nonrept_positions_short_all'],
        'Total': ['tot_rept_positions_long_all', 'tot_rept_positions_short'],
    }

    proportion_df = pd.DataFrame()

    for investor, cols in position_dict.items():
        proportion_df[f"{investor}_Long"] = cot_df[cols[0]] / cot_df[cols].sum(axis=1)
        proportion_df[f"{investor}_Short"] = cot_df[cols[1]] / cot_df[cols].sum(axis=1)
    
    return proportion_df

def cot_mkt_concentration(cot_df: pd.DataFrame):
    """Concentration of the top 4/8 net positions."""
    cot_df_copy = cot_df.copy()
    cot_df_copy = cot_df_copy[['conc_net_le_4_tdr_long_all',
                                'conc_net_le_4_tdr_short_all',
                                'conc_net_le_8_tdr_long_all',
                                'conc_net_le_8_tdr_short_all']]
    cot_df_copy.rename(columns={'conc_net_le_4_tdr_long_all':'TOP_4_LONG_CONCENTRATION',
                                'conc_net_le_4_tdr_short_all':'TOP_4_SHORT_CONCENTRATION',
                                'conc_net_le_8_tdr_long_all':'TOP_8_LONG_CONCENTRATION',
                                'conc_net_le_8_tdr_short_all':'TOP_8_SHORT_CONCENTRATION'},
                                inplace=True)
    return cot_df_copy

#####################
### FUTURES CURVE ###
#####################

futures_curve_contracts = futures_curve_types()
futures_curve_selection_list = list(futures_curve_contracts.keys())

def import_futures_curve_data(date:str, type: str|Literal['VX_EOD', 'VX_AM']):
    """Import futures curve across expiry dates at date t."""
    futures_curve_t = run_query(path='/derivatives/futures/curve',
                    provider='cboe',
                    standard_params={'symbol':type,
                                        'date':date})
    
    futures_curve_t.index = pd.to_datetime(futures_curve_t.index)
    futures_curve_t['expiration'] = pd.to_datetime(futures_curve_t['expiration'])
    futures_curve_t['dte'] = (futures_curve_t['expiration'] - futures_curve_t.index).dt.days
    return futures_curve_t

def futures_curve_slope(futures_curve_df: pd.DataFrame) -> float:
    """Compute the slope of the futures curve on a given day using linear regression."""
    return np.polyfit(x=futures_curve_df['dte'], y=futures_curve_df['price'], deg=1)[0].item()

def futures_curve_slope_prior_bd(date_t: str, type: str|Literal['VX_EOD', 'VX_AM']) -> tuple[float, str]:
    """Futures curve at prior business day."""

    date_t_sub_1 = pd.to_datetime(date_t) - BusinessDay(1)
    date_t_sub_1_str = date_t_sub_1.strftime("%Y-%m-%d")

    futures_curve_t_sub_1 = import_futures_curve_data(date_t_sub_1_str, type)

    slope_t_sub_1 = futures_curve_slope(futures_curve_t_sub_1)

    return round(slope_t_sub_1,4), date_t_sub_1_str

def futures_curve_slope_prior_month(date_t: str, type: str|Literal['VX_EOD', 'VX_AM']) -> tuple[float, str]:
    """Futures curve at prior business day."""

    date_t_sub_1m = pd.to_datetime(date_t) - BusinessMonthEnd(1)
    date_t_sub_1m_str = date_t_sub_1m.strftime("%Y-%m-%d")

    futures_curve_t_sub_1m = import_futures_curve_data(date_t_sub_1m_str, type)

    slope_t_sub_1m = futures_curve_slope(futures_curve_t_sub_1m)

    return round(slope_t_sub_1m,4), date_t_sub_1m_str

def futures_curve_classification(slope: float) -> str:
    """Classify curve based on linear slope."""
    if slope > 0.5:
        classification = 'Contango'
    elif slope < -0.5:
        classification = 'Backwardation'
    else:
        classification = 'Flat'
    return classification

