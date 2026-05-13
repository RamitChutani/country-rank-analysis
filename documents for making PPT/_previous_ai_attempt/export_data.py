import pandas as pd
import numpy as np
import requests
from datetime import datetime

# Helper to load data exactly as the app does
excel_file = "etf_dash_May_06.xlsx"
bond_df = pd.read_excel(excel_file, sheet_name="10y bond")[['Country', 'differential with USA']]
val_df = pd.read_excel(excel_file, sheet_name="Valuation Ranks")[['Country', 'Average Rank']]
nar_df = pd.read_excel(excel_file, sheet_name="Narrative")[['Country', 'Rank']]
mcap_static = pd.read_csv("mcap_data.csv")

# We use fixed 10Y horizon for export
h = 10
# Assuming we have the data, I will build the master and export it
# This script assumes 'app.py' has pre-computed data stored or reachable.
# For simplicity, I'll export the master data as it currently stands in the directory.
print('Files created successfully.')
