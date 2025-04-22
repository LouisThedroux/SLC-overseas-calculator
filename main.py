import streamlit as st
import pickle
import pandas as pd
from slc_data import get_thresholds_data  # Import the function from slc_data.py

# Regenerate the slc_data.pkl file
with open("slc_data.pkl", "wb") as f:
    pickle.dump(get_thresholds_data(), f)

# Set page layout
st.set_page_config(
    page_title="SLC Overseas Calculator", layout="centered",
    page_icon=":money_with_wings:")

# Sidebar content
st.sidebar.markdown(
    """
    # Welcome to the SLC Overseas Calculator
    Estimate your monthly SLC charges based on overseas earnings.
    - Select your loan plan(s).
    - Choose your country and currency.
    - Enter your earnings to calculate charges.
    ## Disclaimer
    This tool is for informational purposes only.
    """,
    unsafe_allow_html=True
)

# Load data
with open("slc_data.pkl", "rb") as f:
    data = pickle.load(f)

st.title("Student Loan Company (SLC) Overseas Charges Calculator")

# Loan plan selection
st.subheader("Select your Student Loan Plans:")
plan_1_selected = st.checkbox("Plan 1", value=False)
plan_2_selected = st.checkbox("Plan 2", value=False)
postgraduate_selected = st.checkbox("Postgraduate", value=False)

# Country selection
countries = sorted(data["Country/Territory"].unique())
default_index = countries.index("Canada") if "Canada" in countries else 0
selected_country = st.selectbox("Select your country of residence:", options=countries, index=default_index)

# Currency selection
currency_column = "Currency"
exchange_rate_column = "Exchange rate"
available_currencies = data[data["Country/Territory"] == selected_country][currency_column].unique()
selected_currency = st.selectbox("Select your currency:", options=available_currencies)

# Input earnings
user_earnings = st.number_input(f"Enter your yearly earnings in {selected_currency}:", min_value=0.0, step=0.01)

# Convert earnings to GBP
exchange_rate = data[(data["Country/Territory"] == selected_country) & (data[currency_column] == selected_currency)][exchange_rate_column].iloc[0]
earnings_in_gbp = user_earnings * exchange_rate
st.write(f"Your earnings in GBP: £{earnings_in_gbp:.2f}")
st.caption("Exchange rates are set annually by SLC and do not fluctuate.")

# Calculate total yearly charges
total_yearly_charges = 0

if plan_1_selected:
    plan_1_threshold = data[(data["loan_type"] == "Plan 1") & (data["Country/Territory"] == selected_country)]["Earnings threshold (GBP)"].iloc[0]
    plan_1_subject_to_charges = max(0, earnings_in_gbp - plan_1_threshold)
    plan_1_charges = plan_1_subject_to_charges * 0.09
    total_yearly_charges += plan_1_charges

if plan_2_selected:
    plan_2_threshold = data[(data["loan_type"] == "Plan 2") & (data["Country/Territory"] == selected_country)]["Earnings threshold (GBP)"].iloc[0]
    if "Upper earnings threshold (GBP)" in data.columns:
        plan_2_upper_threshold = data[(data["loan_type"] == "Plan 2") & (data["Country/Territory"] == selected_country)]["Upper earnings threshold (GBP)"].iloc[0]
    else:
        st.error("The 'Upper earnings threshold (GBP)' column is missing.")
    
    if earnings_in_gbp > plan_2_upper_threshold:
        plan_2_subject_to_charges = max(0, plan_2_upper_threshold - plan_2_threshold)
    else:
        plan_2_subject_to_charges = max(0, earnings_in_gbp - plan_2_threshold)
    
    plan_2_charges = plan_2_subject_to_charges * 0.09
    total_yearly_charges += plan_2_charges

if postgraduate_selected:
    postgraduate_threshold = data[(data["loan_type"] == "Postgraduate") & (data["Country/Territory"] == selected_country)]["Earnings threshold (GBP)"].iloc[0]
    postgraduate_subject_to_charges = max(0, earnings_in_gbp - postgraduate_threshold)
    postgraduate_charges = postgraduate_subject_to_charges * 0.06
    total_yearly_charges += postgraduate_charges

# Display monthly cost
monthly_cost = total_yearly_charges / 12
st.markdown(
    f"""
    <div style="background-color: #ffcccb; padding: 20px; border-radius: 10px; text-align: center;">
        <h2>Your Monthly SLC Cost: £{monthly_cost:.2f}</h2>
    </div>
    """,
    unsafe_allow_html=True
)

# Detailed breakdown
st.subheader("Your SLC Charges Breakdown")

if plan_1_selected:
    with st.container():
        st.markdown("### Plan 1")
        st.write(f"£{plan_1_subject_to_charges:.2f} of your earnings are over the threshold and subject to charges. Yearly charges: £{plan_1_charges:.2f}.")
    with st.expander("Earning Thresholds Data - Plan 1"):
        filtered_data = data[(data["loan_type"] == "Plan 1") & (data["Country/Territory"] == selected_country)]
        st.write(filtered_data)

if plan_2_selected:
    with st.container():
        st.markdown("### Plan 2")
        st.write(f"£{plan_2_subject_to_charges:.2f} of your earnings are over the threshold and subject to charges. Yearly charges: £{plan_2_charges:.2f}.")
    with st.expander("Earning Thresholds Data - Plan 2"):
        filtered_data = data[(data["loan_type"] == "Plan 2") & (data["Country/Territory"] == selected_country)]
        st.write(filtered_data)

if postgraduate_selected:
    with st.container():
        st.markdown("### Postgraduate")
        st.write(f"£{postgraduate_subject_to_charges:.2f} of your earnings are subject to charges. Yearly charges: £{postgraduate_charges:.2f}.")
    with st.expander("Earning Thresholds Data - Postgraduate"):
        filtered_data = data[(data["loan_type"] == "Postgraduate") & (data["Country/Territory"] == selected_country)]
        st.write(filtered_data)