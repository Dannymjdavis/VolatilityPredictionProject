"""Volatility app utilities."""
from app_utils import app_data
import pandas as pd
from openbb import obb

# COT contract inputs
cot_contract_dict = app_data.cot_contract_dict()
cot_contract_selection_list = list(cot_contract_dict.keys())

def import_cot_data(contract_name: str, start_date: str = '2010-01-01', end_date: str = '2025-12-31', all_columns: bool = False):
    """Committment of Traders report data between two dates."""
    contract_code = cot_contract_dict[contract_name]
    cot_raw = obb.regulators.cftc.cot(contract_code, provider='cftc', start_date=start_date, end_date=end_date)
    cot_df = cot_raw.to_df()
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

def _nearest_report_date(cot_df: pd.DataFrame, date: str):
    """COT reports are weekly, so snap any date to the closest available report date."""
    target = pd.to_datetime(date)
    idx = cot_df.index.get_indexer([target], method='ffill')[0]
    return cot_df.index[idx]
