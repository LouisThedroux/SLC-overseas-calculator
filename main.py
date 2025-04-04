import streamlit as st
import pickle
import pandas as pd

# Set page layout to wide
st.set_page_config(
    page_title="SLC Overseas Calculator", layout="centered",
    page_icon=":money_with_wings:")

st.sidebar.markdown(
    """
    # Welcome to the SLC Overseas Calculator
    This project is a simple calculator for estimating the monthly charges for student loans from the Student Loan Company (SLC) for overseas earnings. If you have a student loan from the SLC and are living abroad, this calculator can help you understand how much you might owe based on your earnings in a foreign currency.
    The calculator uses the latest data from the UK government to provide accurate estimates. It allows you to select your loan plan, enter your earnings in your local currency, and see how much you would owe in GBP.
    The calculator is designed to be user-friendly and straightforward, making it accessible for anyone who wants to understand their potential SLC charges while living abroad.
    
    This calculator does not store any personal data or earnings information. All calculations are done locally in your browser, and no data is sent to any server.
    ## How to Use
    1. Select your loan plan(s) (Plan 1, Plan 2, Postgraduate).
    2. Choose your country of residence.
    3. Select your currency.
    4. Enter your earnings in the selected currency.
    5. The calculator will display your earnings in GBP and the estimated monthly charges for your SLC loan.
    6. You can also view the detailed breakdown of your earnings subject to SLC charges.
    7. The calculator provides a disclaimer about the exchange rates used.
    8. The data used in this calculator is sourced from the UK government and is updated annually.
    ## Disclaimer
    The calculator is for informational purposes only and should not be considered financial advice. Please consult with a financial advisor for personalized guidance.
    ## Contact
    If you have any questions or feedback about this project, please feel free to reach out.
    ## Author/Creator
    Andrew Thompson  
    [GitHub](https://github.com/LouisThedroux) | [LinkedIn](https://www.linkedin.com/in/andrew-thompson-3a36b11a2/)
    
    <style>
        .sidebar .sidebar-content {
            background-color: #f0f0f5;
        }
    </style>
    """,
    unsafe_allow_html=True
)




# Main content starts here
with open("slc_data.pkl", "rb") as f:
    data = pickle.load(f)

st.title("Student Loan Company (SLC) Overseas Charges Calculator")

# Loan plan selection using checkboxes
st.subheader("Start by selecting the Student Loan Plans that you currently have:")
plan_1_selected = st.checkbox("Plan 1", value=True)
plan_2_selected = st.checkbox("Plan 2", value=True)
postgraduate_selected = st.checkbox("Postgraduate", value=True)

# Country selection
countries = data["Country/Territory"].unique()
selected_country = st.selectbox("Select your current country of residence:", options=countries)

# Auto-populate currency based on selected country
currency_column = "Currency"  # Replace with the actual column name for currency in your dataframe
exchange_rate_column = "Exchange rate"  # Updated column name for exchange rates
available_currencies = data[data["Country/Territory"] == selected_country][currency_column].unique()
selected_currency = st.selectbox("Select the currency which you are paid with:", options=available_currencies)

# Input for earnings in the selected currency
user_earnings = st.number_input(f"Enter your estimated yearly earnings in {selected_currency}:", min_value=0.0, step=0.01)

# Calculate equivalent earnings in GBP
exchange_rate = data[(data["Country/Territory"] == selected_country) & (data[currency_column] == selected_currency)][exchange_rate_column].iloc[0]
earnings_in_gbp = user_earnings * exchange_rate

# Display equivalent earnings in GBP
st.write(f"Your earnings in GBP: £{earnings_in_gbp:.2f}")

# Add disclaimer about exchange rates
st.caption("This exchange rate is set once a year by SLC (around April 6th) and does not fluctuate with the actual conversion price between the currencies.")

# Calculate total yearly charges
total_yearly_charges = 0

if plan_1_selected:
    plan_1_threshold = data[(data["loan_type"] == "Plan 1") & (data["Country/Territory"] == selected_country)]["Earnings threshold (GBP)"].iloc[0]
    plan_1_subject_to_charges = max(0, earnings_in_gbp - plan_1_threshold)
    plan_1_charges = plan_1_subject_to_charges * 0.09
    total_yearly_charges += plan_1_charges

if plan_2_selected:
    plan_2_threshold = data[(data["loan_type"] == "Plan 2") & (data["Country/Territory"] == selected_country)]["Earnings threshold (GBP)"].iloc[0]
    plan_2_subject_to_charges = max(0, earnings_in_gbp - plan_2_threshold)
    plan_2_charges = plan_2_subject_to_charges * 0.09
    total_yearly_charges += plan_2_charges

if postgraduate_selected:
    postgraduate_threshold = data[(data["loan_type"] == "Postgraduate") & (data["Country/Territory"] == selected_country)]["Earnings threshold (GBP)"].iloc[0]
    postgraduate_subject_to_charges = max(0, earnings_in_gbp - postgraduate_threshold)
    postgraduate_charges = postgraduate_subject_to_charges * 0.06
    total_yearly_charges += postgraduate_charges

# Calculate monthly cost
monthly_cost = total_yearly_charges / 12

# Display the monthly cost in a bright box
st.markdown(
    f"""
    <div style="background-color: #ffcccb; padding: 20px; border-radius: 10px; text-align: center;">
        <h2>Your Monthly SLC Cost: £{monthly_cost:.2f}</h2>
    </div>
    """,
    unsafe_allow_html=True
)

# Add the header for the detailed breakdown
st.subheader("Your SLC Charges Breakdown")

if plan_1_selected:
    with st.container():
        st.markdown("### Plan 1")
        plan_1_threshold = data[(data["loan_type"] == "Plan 1") & (data["Country/Territory"] == selected_country)]["Earnings threshold (GBP)"].iloc[0]
        plan_1_subject_to_charges = max(0, earnings_in_gbp - plan_1_threshold)
        plan_1_charges = plan_1_subject_to_charges * 0.09
        st.write(f"£{plan_1_subject_to_charges:.2f} of your earnings are over the lower threshold and subject to SLC charges. SLC charges are 9% of this amount. Based on your salary information, your SLC charges will be £{plan_1_charges:.2f} over 1 year for your Plan 1 loan.")
        
if plan_1_selected:
    with st.expander("Earning Thresholds Data - Plan 1"):
        filtered_data = data[(data["loan_type"] == "Plan 1") & (data["Country/Territory"] == selected_country)]
        st.write(filtered_data)

if plan_2_selected:
    with st.container():
        st.markdown("### Plan 2")
        plan_2_threshold = data[(data["loan_type"] == "Plan 2") & (data["Country/Territory"] == selected_country)]["Earnings threshold (GBP)"].iloc[0]
        plan_2_subject_to_charges = max(0, earnings_in_gbp - plan_2_threshold)
        plan_2_charges = plan_2_subject_to_charges * 0.09
        st.write(f"£{plan_2_subject_to_charges:.2f} of your earnings are over the threshold and are subject to SLC charges. SLC charges are 9% of of this amount. Based on your salary information, your SLC charges will be £{plan_2_charges:.2f} over 1 year for your Plan 2 loan.")
if plan_2_selected:
    with st.expander("Earning Thresholds Data - Plan 2"):
        filtered_data = data[(data["loan_type"] == "Plan 2") & (data["Country/Territory"] == selected_country)]
        st.write(filtered_data)


if postgraduate_selected:
    with st.container():
        st.markdown("### Postgraduate")
        postgraduate_threshold = data[(data["loan_type"] == "Postgraduate") & (data["Country/Territory"] == selected_country)]["Earnings threshold (GBP)"].iloc[0]
        postgraduate_subject_to_charges = max(0, earnings_in_gbp - postgraduate_threshold)
        postgraduate_charges = postgraduate_subject_to_charges * 0.06
        st.write(f"£{postgraduate_subject_to_charges:.2f} of your earnings are subject to SLC charges. SLC charges are 6% of this amount. Based on your salary information, your SLC charges will be £{postgraduate_charges:.2f} over 1 year for your Postgraduate loan.")
        
# Filter data based on selected loan plans
if postgraduate_selected:
    with st.expander("Earning Thresholds Data - Postgraduate"):
        filtered_data = data[(data["loan_type"] == "Postgraduate") & (data["Country/Territory"] == selected_country)]
        st.write(filtered_data)

# Close the centered container
st.markdown('</div>', unsafe_allow_html=True)