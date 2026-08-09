import streamlit as st
from app_utils.data_description import description_dict
from app_utils import obb_data_utils
import pandas as pd
import plotly.express as px
import datetime as dt
from pandas.tseries.offsets import BDay

st.title('VOLATILITY DATA')

# CONTROL OVERALL SESSION STATE
if 'current_state' not in st.session_state:
    st.session_state['current_state'] = 'empty'

##########################
## FETCH DATA FUNCTIONS ##
##########################

def fetch_cot_data():
    """Callback for the GET DATA button - stores the result in session_state."""
    with data_sidebar.spinner(f"Loading {st.session_state['data_sidebar_selection']}...",
                         show_time=True):
        st.session_state['cot_df_original'] = obb_data_utils.import_cot_data(
            contract_name=st.session_state['contract_selection'],
            start_date=str(st.session_state['cot_start_date']),
            end_date=str(st.session_state['cot_end_date']),
        )
        st.session_state['cot_df'] = st.session_state['cot_df_original'].copy()
        st.session_state['current_state'] = 'cot_data'

def fetch_futures_curve():
    """Callback to import and store futures curve data in session state."""
    futures_codes = obb_data_utils.futures_curve_contracts
    with data_sidebar.spinner(f"Loading {st.session_state['data_sidebar_selection']}...",
                             show_time=True):
        st.session_state['futures_curve_df'] = obb_data_utils.import_futures_curve_data(
            date=st.session_state['futures_curve_date'],
            type=futures_codes[st.session_state['futures_curve_type']]
        )
        st.session_state['current_state'] = 'futures_curve'

##########################
## UPDATE DATA FUNCTION ##
##########################

def filter_dates(df: pd.DataFrame):
    """Callback for the date slider - filters and stores the result in session_state."""
    min_value, max_value = st.session_state['cot_date_slider']
    st.session_state['cot_df'] = df.loc[min_value : max_value]

def update_futures_curve_date():
    """Update futures curve data date."""
    futures_codes = obb_data_utils.futures_curve_contracts
    st.session_state['futures_curve_date'] = st.session_state['futures_curve_update_date']
    st.session_state['futures_curve_df'] = obb_data_utils.import_futures_curve_data(
                date=st.session_state['futures_curve_date'],
                type=futures_codes[st.session_state['futures_curve_type']]
            )

#############
## SIDEBAR ##
#############

data_sidebar = st.sidebar
data_sidebar.title('DATA SELECTION PANE')
data_sidebar.selectbox(options=['COT Report', 'Futures Curve'],
                       label='Select Data',
                       key='data_sidebar_selection')

if st.session_state['data_sidebar_selection'] == 'COT Report':
    data_sidebar.header('COT REPORT INPUTS')
    data_sidebar.selectbox('CONTRACT',
                 options=obb_data_utils.cot_contract_selection_list,
                 placeholder='SELECT CONTRACT',
                 index=20,
                 key='contract_selection')
    data_sidebar.date_input('START DATE',
                           value='2010-01-01',
                           min_value='2010-01-01',
                           key='cot_start_date')
    data_sidebar.date_input('END DATE',
                           value='today',
                           max_value='today',
                           key='cot_end_date')
    data_sidebar.button(label='GET DATA',
                        key='cot_button',
                        on_click=fetch_cot_data,
                        icon="📊")

if st.session_state['data_sidebar_selection'] == 'Futures Curve':
    data_sidebar.header('FUTURES CURVE INPUTS')
    data_sidebar.selectbox('CONTRACT TYPE',
                 options=obb_data_utils.futures_curve_selection_list,
                 placeholder='SELECT CONTRACT TYPE',
                 index=0,
                 key='futures_curve_type')
    data_sidebar.date_input('CONTRACT DATE',
                           value=(dt.datetime.today() - BDay(1)),
                           min_value='2010-01-01',
                           max_value=(dt.datetime.today() - BDay(1)),
                           key='futures_curve_date')
    data_sidebar.button(label='GET DATA',
                        key='futures_curve_button',
                        on_click=fetch_futures_curve,
                        icon="📊")

#####################
## TITLE CONTAINER ##
#####################

with st.container(border=True, width='stretch', height='content'):
    st.subheader("EXOGENOUS VARIABLE EXPLORATION" if st.session_state['current_state']=='empty' else f"{st.session_state['data_sidebar_selection']}".upper())
    st.write("Select Data to Begin" if st.session_state['current_state']=='empty' else description_dict[st.session_state['current_state']]['description'])

    if st.session_state['current_state'] != 'empty':
        column_badge_1, column_badge_2 = st.columns(2)
        column_badge_1.badge(f"{description_dict[st.session_state['current_state']]['provider']}", icon="📋", color='primary')
        column_badge_2.badge(f"{description_dict[st.session_state['current_state']]['frequency']}", icon="⏱️", color='primary')

#########################
## SELECTION CONTAINER ##
#########################

def column_container_number(session_state: str):
    """Return int which updates depending on session state."""
    if session_state == 'empty':
        n_cols = 1
    elif session_state == 'futures_curve':
        n_cols = 2
    else:
        n_cols = 3
    return n_cols

selection_container = st.columns(column_container_number(st.session_state['current_state']),
                                 border=True if st.session_state['current_state'] != 'futures_curve' else False,
                                 width='stretch',
                                 vertical_alignment='top',
                                 gap='medium')

if st.session_state['current_state'] == 'empty':
    selection_container[0].write('👈 **USE SIDEBAR TO COLLECT DATA**')

elif st.session_state['current_state'] == 'cot_data':
    # COT DATA SELECTION
    selection_container[0].selectbox('**DISPLAY DATA**', options=[
            'Raw Data',
            'Investor-Type Breakdown',
            'Long/Short Breakdown',
            'Market Concentration'
        ], index=0, key='cot_data_type')
    # COT CHART VIEW
    selection_container[1].selectbox('**CHART TYPE**', options=[
            'Table',
            'Line Chart',
            'Stacked Bar Chart'
        ], index=0, key='cot_chart_type')
    # COT DATE FILTER
    cot_date_min = st.session_state['cot_df_original'].index.min().to_pydatetime()
    cot_date_max = st.session_state['cot_df_original'].index.max().to_pydatetime()
    selection_container[2].slider('**DATE SLIDER**',
                                  key='cot_date_slider',
                                  min_value=cot_date_min,
                                  max_value=cot_date_max,
                                  value=(cot_date_min, cot_date_max),
                                  on_change=filter_dates,
                                  args=[st.session_state['cot_df_original']])

elif st.session_state['current_state'] == 'futures_curve':
    # FUTURES CURVE CHART VIEW
    selection_container[0].selectbox('**CHANGE CHART TYPE**',
                                     options=[
                                         'Table',
                                         'Line Chart',
                                         ],
                                         index=0,
                                         key='futures_curve_chart_type',
                                         )
    # FUTURES CURVE DATE FILTER
    selection_container[1].date_input('**UPDATE DATE**',
                                      key='futures_curve_update_date',
                                      min_value=pd.Timestamp('2010-01-01'),
                                      max_value=(dt.datetime.today() - BDay(1)),
                                      value=st.session_state['futures_curve_date'],
                                      on_change=update_futures_curve_date)

###################
## SUMMARY CARDS ##
###################

if st.session_state['current_state'] == 'futures_curve':
    futures_codes = obb_data_utils.futures_curve_contracts
    summary_cards = st.columns(3)

    curve_prior_month, date_prior_month = obb_data_utils.futures_curve_slope_prior_month(date_t=st.session_state['futures_curve_date'],
                                                                type=futures_codes[st.session_state['futures_curve_type']])
    summary_cards[2].metric(label='PRIOR MONTH SLOPE', value=curve_prior_month, format='percent')
    summary_cards[2].write(date_prior_month)

    curve_tm1, date_tm1 = obb_data_utils.futures_curve_slope_prior_bd(date_t=st.session_state['futures_curve_date'],
                                                            type=futures_codes[st.session_state['futures_curve_type']])
    summary_cards[1].metric(label='PRIOR DAY SLOPE', value=curve_tm1, format='percent')
    summary_cards[1].write(date_tm1)

    slope_t = obb_data_utils.futures_curve_slope(st.session_state['futures_curve_df'])
    summary_cards[0].metric(label="SLOPE", value=round(slope_t, 4), delta=round((slope_t - curve_tm1), 4), format='percent')


####################
## DATA CONTAINER ##
####################

data_container = st.container(border=False if st.session_state['current_state'] is None else True, 
                              key='data_container',
                            width='stretch',
                            height=500 if st.session_state['current_state'] == 'empty' else 'stretch',
                            horizontal_alignment='center',
                            vertical_alignment='center')

# DATA TYPE: COT DATA
if st.session_state['current_state'] == 'cot_data':
    if st.session_state['cot_data_type'] == 'Raw Data':
        st.session_state['cot_df_updated_type'] = st.session_state['cot_df'].copy()
    elif st.session_state['cot_data_type'] == 'Investor-Type Breakdown':
        st.session_state['cot_df_updated_type'] = obb_data_utils.cot_oi_proportions_by_type(st.session_state['cot_df'])
    elif st.session_state['cot_data_type'] == 'Long/Short Breakdown':
        st.session_state['cot_df_updated_type'] = obb_data_utils.cot_long_short_proportions(st.session_state['cot_df'])
    elif st.session_state['cot_data_type'] == 'Market Concentration':
        st.session_state['cot_df_updated_type'] = obb_data_utils.cot_mkt_concentration(st.session_state['cot_df'])

# VISUAL TYPE: COT DATA
if st.session_state['current_state'] == 'cot_data':
    if st.session_state['cot_chart_type'] == 'Table':
        data_container.dataframe(st.session_state['cot_df_updated_type'])
    elif st.session_state['cot_chart_type'] == 'Line Chart':
        fig = px.line(st.session_state['cot_df_updated_type'], title=f"{st.session_state['cot_data_type']}".upper(),
                      labels={'value':'', 'date':''})
        data_container.plotly_chart(fig, use_container_width=True)
    elif st.session_state['cot_chart_type'] == 'Stacked Bar Chart':
        data_container.bar_chart(st.session_state['cot_df_updated_type'])

# DATA TYPE: FUTURES CURVE DATA
if st.session_state['current_state'] == 'futures_curve':
    if st.session_state['futures_curve_chart_type'] == 'Table':
        data_container.dataframe(st.session_state['futures_curve_df'])
    elif st.session_state['futures_curve_chart_type'] == 'Line Chart':
        data_container.plotly_chart(
            px.line(
                st.session_state['futures_curve_df'],
                x='dte',
                y='price',
                title=f"FUTURES CURVE | {st.session_state['futures_curve_date']}",
                labels={'price':'', 'dte':'Days to Expiry'}
                )
            )
