import pandas as pd
import os

# Put the exact name of your downloaded file here
RAW_DATA_FILE = '../data/Bitext_Sample.csv' 
CLEAN_OUTPUT = '../data/incoming_tickets.csv'

def prepare_data():
    print(f"Loading raw dataset from {RAW_DATA_FILE}...")
    
    try:
        # Load the raw dataset
        df = pd.read_csv(RAW_DATA_FILE)
        
        # The Bitext dataset usually stores the customer's message in a column called 'instruction'.
        # If your file uses a different column name for the text (like 'utterance' or 'text'), change it below!
        text_column = 'instruction' 
        
        if text_column not in df.columns:
            print(f"Columns found: {df.columns.tolist()}")
            raise KeyError(f"Could not find column '{text_column}'. Please check the column names above and update the script.")

        # Let's take a random sample of 100 tickets to process
        print("Sampling 100 random tickets...")
        df_sample = df.sample(n=100, random_state=42).reset_index(drop=True)
        
        # Create a new Dataframe matching our pipeline's exact expected format
        clean_df = pd.DataFrame({
            'ticket_id': range(2000, 2100), # Generate IDs from 2000 to 2099
            'customer_text': df_sample[text_column]
        })
        
        # Save it, overwriting the old 8 tickets
        clean_df.to_csv(CLEAN_OUTPUT, index=False)
        print(f"Success! Saved 100 clean tickets to {CLEAN_OUTPUT}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    prepare_data()