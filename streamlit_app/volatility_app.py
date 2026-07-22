import streamlit as st
from app_utils import app_utils
import pandas as pd

st.title('VOLATILITY DATA')

# CONTROL OVERALL SESSION STATE
if 'current_state' not in st.session_state:
    st.session_state['current_state'] = 'empty'

# FETCH DATA FUNCTIONS
def fetch_cot_data():
    """Callback for the GET DATA button - stores the result in session_state."""
    with data_sidebar.spinner(f"Loading {st.session_state['data_sidebar_selection']}...",
                         show_time=True):
        st.session_state['cot_df_original'] = app_utils.import_cot_data(
            contract_name=st.session_state['contract_selection'],
            start_date=str(st.session_state['cot_start_date']),
            end_date=str(st.session_state['cot_end_date']),
        )
        st.session_state['cot_df'] = st.session_state['cot_df_original'].copy()
        st.session_state['current_state'] = 'cot_data'

# FILTER DATES FUNCTION
def filter_dates(df: pd.DataFrame):
    """Callback for the date slider - filters and stores the result in session_state."""
    min_value, max_value = st.session_state['cot_date_slider']
    st.session_state['cot_df'] = df.loc[min_value : max_value]

# SIDEBAR
data_sidebar = st.sidebar
data_sidebar.title('SELECT DATA')
data_sidebar.selectbox(options=['COT Report'],
                       label='Select Data',
                       key='data_sidebar_selection')

if st.session_state['data_sidebar_selection'] == 'COT Report':
    data_sidebar.header('COT REPORT INPUTS')
    data_sidebar.selectbox('CONTRACT',
                 options=app_utils.cot_contract_selection_list,
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


# SELECTION CONTAINER
selection_container = st.columns(1 if st.session_state['current_state'] == 'empty' else 4,
                                 border=True,
                                 width='stretch',
                                 vertical_alignment='top',
                                 gap='medium')

if st.session_state['current_state'] == 'empty':
    selection_container[0].write('👈 USE SIDEBAR TO COLLECT DATA')
elif st.session_state['current_state'] == 'cot_data':
    # COT DATA SELECTION
    selection_container[0].selectbox('SHOW DATA', options=[
            'Raw Data',
            'Investor-Type Breakdown',
            'Long/Short Breakdown',
            'Market Concentration'
        ], index=0, key='cot_data_type')
    # COT CHART VIEW
    selection_container[1].selectbox('SHOW CHART', options=[
            'Table',
            'Line Chart',
            'Stacked Bar Chart'
        ], index=0, key='cot_chart_type')
    # COT DATE FILTER
    cot_date_min = st.session_state['cot_df_original'].index.min().to_pydatetime()
    cot_date_max = st.session_state['cot_df_original'].index.max().to_pydatetime()
    selection_container[2].slider('SHOW CHART',
                                  key='cot_date_slider',
                                  min_value=cot_date_min,
                                  max_value=cot_date_max,
                                  value=(cot_date_min, cot_date_max),
                                  on_change=filter_dates,
                                  args=[st.session_state['cot_df_original']])

# DATA CONTAINER
data_container = st.container(border=False if st.session_state['current_state'] is None else True, 
                              key='data_container',
                            width='stretch',
                            height=500 if st.session_state['current_state'] == 'empty' else 'stretch',
                            horizontal_alignment='center',
                            vertical_alignment='center')

# DATA TYPE - FOR COT DATA
if st.session_state['current_state'] == 'cot_data':
    if st.session_state['cot_data_type'] == 'Raw Data':
        st.session_state['cot_df_updated_type'] = st.session_state['cot_df'].copy()
    elif st.session_state['cot_data_type'] == 'Investor-Type Breakdown':
        st.session_state['cot_df_updated_type'] = app_utils.cot_oi_proportions_by_type(st.session_state['cot_df'])
    elif st.session_state['cot_data_type'] == 'Long/Short Breakdown':
        st.session_state['cot_df_updated_type'] = app_utils.cot_long_short_proportions(st.session_state['cot_df'])
    elif st.session_state['cot_data_type'] == 'Market Concentration':
        st.session_state['cot_df_updated_type'] = app_utils.cot_mkt_concentration(st.session_state['cot_df'])
    # COLUMN SELECTOR
    selection_container[3].multiselect('SELECT COLS',
                                       options=st.session_state['cot_df_updated_type'].columns,
                                       key='cot_col_select')
    # APPLY COLUMN SELECTION (empty selection = show all columns)
    if st.session_state['cot_col_select']:
        st.session_state['cot_df_display'] = st.session_state['cot_df_updated_type'][st.session_state['cot_col_select']]
    else:
        st.session_state['cot_df_display'] = st.session_state['cot_df_updated_type']

# VISUAL TYPE - FOR COT DATA
if st.session_state['current_state'] == 'cot_data':
    if st.session_state['cot_chart_type'] == 'Table':
        data_container.dataframe(st.session_state['cot_df_display'])
    elif st.session_state['cot_chart_type'] == 'Line Chart':
        data_container.line_chart(st.session_state['cot_df_display'])
    elif st.session_state['cot_chart_type'] == 'Stacked Bar Chart':
        data_container.bar_chart(st.session_state['cot_df_display'])
