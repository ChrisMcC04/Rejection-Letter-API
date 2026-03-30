import csv
import requests
import json

# Configuration
API_URL = "http://127.0.0.1:8000/generate-rejection"
CSV_FILE = "REDACTED_OFFICIAL Isolated_cycle_4_project_4_gemma_AI_scoring.csv"

def run_test():
    feedback_points = []
    
    print(f"Reading data from {CSV_FILE}...")
    try:
        # 1. Read the CSV file
        with open(CSV_FILE, mode='r', encoding='utf-8-sig') as file:
            csv_reader = csv.DictReader(file)
            
            # Print the detected columns so we know we are reading the right data
            print(f"Detected columns: {csv_reader.fieldnames}")
            
            for row in csv_reader:
                # We pull out the score and justification. 
                # (Update the string keys below if your CSV headers are spelt slightly differently!)
                feedback_points.append({
                    "score": row.get("score", "Unknown"), 
                    "justification": row.get("justification", "No justification provided")
                })
                
    except FileNotFoundError:
        print(f"ERROR: Could not find the file '{CSV_FILE}'. Ensure it is in the same folder as this script.")
        return

    # 2. Build the data package
    payload = {
        "project_name": "Project 4",
        "domain": "Air",  # Change this to test different handrails (e.g., "Maritime" or "Land")
        "ai_feedback_points": feedback_points
    }

    # 3. Fire it at your local API
    print(f"\nFiring {len(feedback_points)} feedback points at the local Rejection Letter API...")
    try:
        response = requests.post(API_URL, json=payload)
        
        # 4. Print the results
        if response.status_code == 200:
            print("\nSUCCESS! Here is the AI's translated output:\n")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"\n❌ API ERROR (Code {response.status_code}):")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("\n CONNECTION ERROR: Is your Docker container / FastAPI server actually running?")

if __name__ == "__main__":
    run_test()