import requests
import pandas as pd
from bs4 import BeautifulSoup
import pickle

def get_thresholds_data():
    urls = {
        "plan_1": "https://www.gov.uk/government/publications/overseas-earnings-thresholds-for-plan-1-student-loans/overseas-earnings-thresholds-for-plan-1-student-loans-2024-25",
        "plan_2": "https://www.gov.uk/government/publications/overseas-earnings-thresholds-for-plan-2-student-loans/overseas-earnings-thresholds-for-plan-2-student-loans-2024-25",
        "postgraduate": "https://www.gov.uk/government/publications/overseas-earnings-thresholds-for-postgraduate-student-loans/overseas-earnings-thresholds-for-postgraduate-student-loans-2024-25"
    }
    
    tables = {}
    
    for key, url in urls.items():
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"The website for {key} loan thresholds is not accessible.")
        
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table")
        if table is None:
            raise Exception(f"The website for {key} loan thresholds does not contain any tables.")
        
        df = pd.read_html(str(table))[0]
        tables[key] = df
    
    if "Lower earnings threshold (GBP)" in tables["plan_2"].columns:
        tables["plan_2"] = tables["plan_2"].rename(columns={
            "Lower earnings threshold (GBP)": "Earnings threshold (GBP)",
            "Upper earnings threshold (GBP)": "Upper earnings threshold (GBP)"  
        })
    
    thresholds_df = pd.concat(tables.values(), keys=tables.keys()).reset_index()
    thresholds_df = thresholds_df.rename(columns={"level_0": "loan_type"})
    thresholds_df = thresholds_df.drop(columns=["level_1"])  # Drop the level_1 column
    thresholds_df["loan_type"] = thresholds_df["loan_type"].replace({
        "plan_1": "Plan 1",
        "plan_2": "Plan 2",
        "postgraduate": "Postgraduate"
    })
    
    thresholds_df["study_type"] = thresholds_df["loan_type"].apply(lambda x: "postgraduate" if x == "Postgraduate" else "undergraduate")
    thresholds_df["prop_over_threshold"] = thresholds_df["loan_type"].apply(lambda x: 0.06 if x == "Postgraduate" else 0.09)
    
    if "study_type" in thresholds_df.columns:
        thresholds_df = thresholds_df.drop(columns=["study_type"])
        
    if "Fixed monthly repayment (GBP)" in thresholds_df.columns:
        thresholds_df = thresholds_df.drop(columns=["Fixed monthly repayment (GBP)"])
    
    # Rename prop_over_threshold to percentage_to_pay
    thresholds_df = thresholds_df.rename(columns={"prop_over_threshold": "percentage_to_pay"})
    
    currency_cols = [col for col in thresholds_df.columns if "GBP" in col]
    for col in currency_cols:
        thresholds_df[col] = thresholds_df[col].replace(r'[^0-9.]', '', regex=True).astype(float)
    
    # Add logic for upper threshold for Plan 2
    if "Upper earnings threshold (GBP)" in thresholds_df.columns:
        thresholds_df["adjusted_threshold"] = thresholds_df.apply(
            lambda row: row["Upper earnings threshold (GBP)"] if row["loan_type"] == "Plan 2" else row["Earnings threshold (GBP)"],
            axis=1
        )
    
    return thresholds_df

with open("slc_data.pkl", "wb") as f:
    pickle.dump(get_thresholds_data(), f)


