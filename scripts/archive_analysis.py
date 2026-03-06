import os
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
api_key = os.environ.get("GEMINI_API") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API key not found in .env")
    exit(1)

genai.configure(api_key=api_key)

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "archive", "veterinary_clinical_data.csv")

def perform_analysis():
    print(f"Loading data from {DATA_PATH}...")
    try:
        df = pd.read_csv(DATA_PATH)
    except FileNotFoundError:
        print(f"File not found: {DATA_PATH}")
        return
        
    print(f"Total records in archive: {len(df)}")
    
    # Take a sample of 10 random records to analyze using Gemini
    sample_df = df.sample(n=10, random_state=42)
    csv_string = sample_df.to_csv(index=False)
    
    prompt = f"""
    You are an expert veterinary data analyst. I have a dataset of veterinary clinical data.
    The dataset contains animal types, breeds, age, weight, medical history, and 5 symptom columns.
    
    Please analyze the following random sample of 10 cases from the dataset and provide:
    1. A brief summary of the most severe cases.
    2. Potential likely diseases for these specific combinations of symptoms.
    3. General insights on what common trends might exist based on this data slice.
    
    Here is the CSV data slice:
    {csv_string}
    """
    
    print("\nSending data to Gemini for analysis...\n")
    
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        print("=== GEMINI ANALYSIS REPORT ===")
        print(response.text)
        
        # Save report
        report_path = os.path.join(os.path.dirname(__file__), "..", "archive", "gemini_analysis_report.md")
        with open(report_path, "w") as f:
            f.write("# Gemini Veterinary Data Analysis\n\n")
            f.write(response.text)
        print(f"\nReport saved to: {report_path}")
        
    except Exception as e:
        print(f"Failed to analyze with Gemini: {e}")
        print("Note: Ensure your API key in .env is valid and not revoked.")

if __name__ == "__main__":
    perform_analysis()
