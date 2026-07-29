"""Description of data sources."""

# keys must mirror st.session_state['current_state']
description_dict = {
    "cot_data": {
        "description":"Weekly snapshot of how different types of traders are positioned (long vs. short) in U.S. futures markets — shows who is holding how much of a contract",
        "provider":"U.S. Commodity Futures Trading Commission (CTFC)",
        "frequency":"Every Friday (for prior Tuesday's positions)"
    },
    "futures_curve":{
        "description":"Futures prices for the same underlying asset across different expiration dates. Shows what the market currently expects/prices in for near-term vs. far-term delivery",
        "provider":"Cboe Futures Exchange",
        "frequency":"End of Day"
    }
}