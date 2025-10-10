import pandas as pd

def test_metadata_extraction(excel_path):
    df = pd.read_excel(excel_path)
    df.columns = df.columns.str.strip()  # Clean column names
    print("Columns found:", df.columns.tolist())
    for idx, row in df.iterrows():
        incident_date = row.get("Reported Date", None)
        incident_number = row.get("Incident", None)
        portfolio = row.get("Product Portfolio -Area of cause", None)
        print(f"Row {idx}: Incident Date = {incident_date}, Incident Number = {incident_number}, portfolio = {portfolio}")
        if idx >= 9:  # Show only first 10 rows
            break

if __name__ == "__main__":
    # Replace with your actual Excel file path
    test_metadata_extraction("data/Major Significant & Key Incidents KB-2.xlsx")